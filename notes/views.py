import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage

from .chatbot import ask_groq


# -------------------------------
# 1. Teacher Upload Notes
# -------------------------------
# @csrf_exempt
# def upload_note(request):
#     if request.method == "POST":
#         subject = request.POST.get("subject")
#         unit = request.POST.get("unit")
#         title = request.POST.get("title")
#         file = request.FILES.get("file")

#         if not (subject and unit and title and file):
#             return JsonResponse({"error": "All fields are required"}, status=400)

#         fs = FileSystemStorage()
#         filename = fs.save(file.name, file)

#         note = Note(subject=subject, unit=unit, title=title, file=filename)
#         note.save()
#         print(f"Note uploaded: {note}")

#         return JsonResponse({"message": "Note uploaded successfully!"})

#     return JsonResponse({"error": "Invalid request"}, status=405)



# -------------------------------
# 3. Chatbot with Groq
# -------------------------------
# notes/views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .chatbot import ask_groq

@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def chatbot(request):
    if request.method == "OPTIONS":
        # Handle CORS preflight
        response = JsonResponse({"status": "ok"})
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type"
        return response

    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))
            query = data.get("query", "")
            if not query:
                return JsonResponse({"error": "Query is required"}, status=400)
            
            answer = ask_groq(query)
            return JsonResponse({"answer": answer})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
        





from django.shortcuts import render
from django.http import JsonResponse
from .models import ClassNote
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def upload_notes(request, class_id, subject):
    if request.method == 'POST':
        pdf_file = request.FILES.get('pdf_file')
        if pdf_file:
            ClassNote.objects.create(
                class_id=class_id,
                subject_name=subject,
                pdf_file=pdf_file
            )
            return JsonResponse({'status': 'success', 'message': 'Notes uploaded successfully'})
        return JsonResponse({'status': 'error', 'message': 'No file uploaded'}, status=400)
    
    return render(request, 'upload_notes.html', {'class_id': class_id, 'subject': subject})




from django.http import JsonResponse, FileResponse
from .models import ClassNote  # Replace with your actual model name

def get_notes_by_class_and_subject(request):
    class_name = request.GET.get('className')
    subject_name = request.GET.get('subjectName')

    if not class_name or not subject_name:
        return JsonResponse({'error': 'Missing className or subjectName'}, status=400)

    notes = ClassNote.objects.filter(class_id__iexact=class_name, subject_name__iexact=subject_name)

    data = [
        {
            'id': note.id,
            'filename': note.pdf_file.name.split('/')[-1],
            'uploaded_at': note.uploaded_at.strftime('%Y-%m-%d %H:%M'),
        }
        for note in notes
    ]

    return JsonResponse(data, safe=False)


def download_note(request, note_id):
    try:
        note = ClassNote.objects.get(id=note_id)
        return FileResponse(note.pdf_file.open(), as_attachment=True, filename=note.pdf_file.name)
    except ClassNote.DoesNotExist:
        return JsonResponse({'error': 'Note not found'}, status=404)





from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import make_password, check_password
from .models import Teacher
from django.core.exceptions import ObjectDoesNotExist

# 👨‍🏫 Teacher Signup
@api_view(['POST'])
def teacher_signup(request):
    data = request.data
    try:
        teacher = Teacher.objects.create(
            name=data['name'],
            email=data['email'],
            password=make_password(data['password']),
            department=data['department']
        )
        return Response({'message': 'Teacher registered successfully'}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

# 🔐 Teacher Login
@api_view(['POST'])
def teacher_login(request):
    data = request.data
    try:
        teacher = Teacher.objects.get(email=data['email'])
        if check_password(data['password'], teacher.password):
            return Response({'message': 'Login successful', 'teacher_id': teacher.id}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid password'}, status=status.HTTP_401_UNAUTHORIZED)
    except ObjectDoesNotExist:
        return Response({'error': 'Teacher not found'}, status=status.HTTP_404_NOT_FOUND)

from .models import Student

# 👨‍🎓 Student Signup
@api_view(['POST'])
def student_signup(request):
    data = request.data
    try:
        student = Student.objects.create(
            roll_number=data['roll_number'],
            name=data['name'],
            email=data['email'],
            password=make_password(data['password']),
            year=data['year'],
            section_id=data['section_id']  # assuming you're passing section ID
        )
        return Response({'message': 'Student registered successfully'}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

# 🔐 Student Login
@api_view(['POST'])
def student_login(request):
    data = request.data
    try:
        student = Student.objects.get(email=data['email'])
        if check_password(data['password'], student.password):
            return Response({'message': 'Login successful', 'roll_number': student.roll_number}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid password'}, status=status.HTTP_401_UNAUTHORIZED)
    except ObjectDoesNotExist:
        return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)
    
from .models import Quiz, Question, StudentQuizAttempt, StudentAnswer
@api_view(['POST'])
def create_quiz(request):
    data = request.data
    try:
        quiz = Quiz.objects.create(
            title=data['title'],
            description=data['description'],
            teacher_id=data['teacher_id'],
            subject_id=data['subject_id'],
            section_id=data['section_id']
        )
        return Response({'message': 'Quiz created', 'quiz_id': quiz.id}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def add_question(request):
    data = request.data
    try:
        question = Question.objects.create(
            quiz_id=data['quiz_id'],
            text=data['text'],
            option_a=data['option_a'],
            option_b=data['option_b'],
            option_c=data['option_c'],
            option_d=data['option_d'],
            correct_option=data['correct_option'].upper()
        )
        return Response({'message': 'Question added', 'question_id': question.id}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
@api_view(['POST'])
def submit_quiz(request):
    data = request.data

    required_fields = ['quiz_id', 'student_roll_number', 'answers']
    if not all(field in data for field in required_fields):
        return Response({'error': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)

    quiz_id = data['quiz_id']
    roll_number = data['student_roll_number']
    answers = data['answers']  # list of {question_id, selected_option}

    if not isinstance(answers, list) or not answers:
        return Response({'error': 'Answers must be a non-empty list'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        student = Student.objects.get(roll_number=roll_number)
        score = 0
        attempt = StudentQuizAttempt.objects.create(student=student, quiz_id=quiz_id, score=0)

        for ans in answers:
            question_id = ans.get('question_id')
            selected_option = ans.get('selected_option', '').upper()

            if not question_id or selected_option not in ['A', 'B', 'C', 'D']:
                continue

            try:
                question = Question.objects.get(id=question_id)
                is_correct = (selected_option == question.correct_option)
                if is_correct:
                    score += 1

                StudentAnswer.objects.create(
                    attempt=attempt,
                    question=question,
                    selected_option=selected_option,
                    is_correct=is_correct
                )
            except Question.DoesNotExist:
                continue

        attempt.score = score
        attempt.save()

        return Response({'message': 'Quiz submitted successfully', 'score': score}, status=status.HTTP_200_OK)

    except Student.DoesNotExist:
        return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
   

@api_view(['GET'])
def get_student_score(request, student_roll_number, quiz_id):
    try:
        attempt = StudentQuizAttempt.objects.get(student__roll_number=student_roll_number, quiz_id=quiz_id)
        return Response({
            'student': attempt.student.name,
            'quiz': attempt.quiz.title,
            'score': attempt.score,
            'submitted_at': attempt.submitted_at
        }, status=status.HTTP_200_OK)
    except StudentQuizAttempt.DoesNotExist:
        return Response({'error': 'No attempt found'}, status=status.HTTP_404_NOT_FOUND)

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Teacher

@api_view(['GET'])
def get_teacher_id_by_email(request):
    email = request.query_params.get('email')
    if not email:
        return Response({'error': 'Email parameter is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        teacher = Teacher.objects.get(email=email)
        return Response({'teacher_id': teacher.id}, status=status.HTTP_200_OK)
    except Teacher.DoesNotExist:
        return Response({'error': 'Teacher not found'}, status=status.HTTP_404_NOT_FOUND)
