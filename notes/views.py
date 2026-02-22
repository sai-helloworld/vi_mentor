import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage

from .chatbot import ask_groq



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
        





# from django.shortcuts import render
# from django.http import JsonResponse
# from .models import ClassNote
# from django.views.decorators.csrf import csrf_exempt

# @csrf_exempt
# def upload_notes(request, class_id, subject):
#     if request.method == 'POST':
#         pdf_file = request.FILES.get('pdf_file')
#         if pdf_file:
#             ClassNote.objects.create(
#                 class_id=class_id,
#                 subject_name=subject,
#                 pdf_file=pdf_file
#             )
#             return JsonResponse({'status': 'success', 'message': 'Notes uploaded successfully'})
#         return JsonResponse({'status': 'error', 'message': 'No file uploaded'}, status=400)
    
#     return render(request, 'upload_notes.html', {'class_id': class_id, 'subject': subject})
# from django.shortcuts import render
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from .models import (
#     ClassNote,
#     Teacher,
#     Subject,
#     ClassSection,
#     TeacherSubjectAssignment
# )
# from .rag_faiss_utils import build_or_update_faiss_index
# import os

# @csrf_exempt
# def upload_notes(request, teacher_id, subject_id, section_id):
#     """
#     Teacher uploads notes for an assigned subject & section.
#     FAISS index is created or updated automatically.
#     """

#     if request.method != 'POST':
#         return JsonResponse(
#             {'error': 'Only POST method allowed'},
#             status=405
#         )

#     pdf_file = request.FILES.get('pdf_file')
#     if not pdf_file:
#         return JsonResponse(
#             {'error': 'No PDF uploaded'},
#             status=400
#         )

#     # Fetch objects
#     try:
#         teacher = Teacher.objects.get(id=teacher_id)
#         subject = Subject.objects.get(id=subject_id)
#         section = ClassSection.objects.get(id=section_id)
#     except:
#         return JsonResponse(
#             {'error': 'Invalid teacher / subject / section'},
#             status=400
#         )

#     # Authorization check
#     if not TeacherSubjectAssignment.objects.filter(
#         teacher=teacher,
#         subject=subject,
#         section=section
#     ).exists():
#         return JsonResponse(
#             {'error': 'Teacher not assigned to this subject & section'},
#             status=403
#         )

#     # Save PDF
#     note = ClassNote.objects.create(
#         class_id=section.name,      # stored as string (per your model)
#         subject_name=subject.name,
#         pdf_file=pdf_file
#     )

#     # Build FAISS path
#     vector_dir = os.path.join(
#         "vector_indexes",
#         teacher.department.replace(" ", "_"),
#         section.name,
#         subject.name.lower()
#     )

#     # Update FAISS index
#     build_or_update_faiss_index(
#         pdf_path=note.pdf_file.path,
#         vector_dir=vector_dir
#     )

#     return JsonResponse({
#         'status': 'success',
#         'message': 'Notes uploaded and FAISS index updated',
#         'vector_path': vector_dir
#     })


# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from django.views.decorators.http import require_POST
# from django.db import transaction
# from django.conf import settings
# from .models import (
#     ClassNote,
#     Teacher,
#     Subject,
#     ClassSection,
#     TeacherSubjectAssignment
# )
# from .rag_faiss_utils import build_or_update_faiss_index
# import os


# @csrf_exempt
# @require_POST
# def upload_notes(request, teacher_id, subject_id, section_id):
#     """
#     Upload PDF or DOCX notes and update subject-specific FAISS index.
#     CSRF exempt for frontend API usage.
#     """

#     uploaded_file = request.FILES.get("pdf_file")

#     # 1️⃣ File existence check
#     if not uploaded_file:
#         return JsonResponse(
#             {"error": "No file uploaded."},
#             status=400
#         )

#     # 2️⃣ File type validation
#     allowed_extensions = [".pdf", ".docx"]
#     file_ext = os.path.splitext(uploaded_file.name)[1].lower()

#     if file_ext not in allowed_extensions:
#         return JsonResponse(
#             {"error": "Only PDF and DOCX files are allowed."},
#             status=400
#         )

#     # 3️⃣ File size limit (10MB example)
#     max_size = 10 * 1024 * 1024
#     if uploaded_file.size > max_size:
#         return JsonResponse(
#             {"error": "File size exceeds 10MB limit."},
#             status=400
#         )

#     # 4️⃣ Fetch DB objects safely
#     try:
#         teacher = Teacher.objects.get(id=teacher_id)
#         subject = Subject.objects.get(id=subject_id)
#         section = ClassSection.objects.get(id=section_id)
#     except Teacher.DoesNotExist:
#         return JsonResponse({"error": "Teacher not found."}, status=404)
#     except Subject.DoesNotExist:
#         return JsonResponse({"error": "Subject not found."}, status=404)
#     except ClassSection.DoesNotExist:
#         return JsonResponse({"error": "Section not found."}, status=404)

#     # 5️⃣ Authorization check
#     is_assigned = TeacherSubjectAssignment.objects.filter(
#         teacher=teacher,
#         subject=subject,
#         section=section
#     ).exists()

#     if not is_assigned:
#         return JsonResponse(
#             {"error": "Teacher not assigned to this subject and section."},
#             status=403
#         )

#     # 6️⃣ Save + FAISS update
#     try:
#         with transaction.atomic():

#             note = ClassNote.objects.create(
#                 class_id=section.name,
#                 subject_name=subject.name,
#                 pdf_file=uploaded_file
#             )

#             vector_dir = os.path.join(
#                 settings.BASE_DIR,
#                 "vector_indexes",
#                 teacher.department.replace(" ", "_"),
#                 section.name,
#                 subject.name.lower()
#             )

#             build_or_update_faiss_index(
#                 file_path=note.pdf_file.path,
#                 vector_dir=vector_dir
#             )

#     except Exception as e:
#         return JsonResponse(
#             {"error": f"Indexing failed: {str(e)}"},
#             status=500
#         )

#     return JsonResponse({
#         "status": "success",
#         "message": "Notes uploaded and FAISS index updated successfully."
#     })


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db import transaction
from django.conf import settings
from .models import (
    ChatMessage,
    ClassNote,
    Teacher,
    Subject,
    ClassSection,
    TeacherSubjectAssignment
)
from .rag_faiss_utils import build_or_update_faiss_index
import os


@csrf_exempt
@require_POST
def upload_notes(request, teacher_id, subject_id, section_id):
    """
    Upload PDF or DOCX notes and update subject-specific FAISS index.
    """

    uploaded_file = request.FILES.get("pdf_file")

    if not uploaded_file:
        return JsonResponse({"error": "No file uploaded."}, status=400)

    # Validate extension
    allowed_extensions = [".pdf", ".docx"]
    file_ext = os.path.splitext(uploaded_file.name)[1].lower()

    if file_ext not in allowed_extensions:
        return JsonResponse(
            {"error": "Only PDF and DOCX files are allowed."},
            status=400
        )

    # Validate file size (10MB)
    max_size = 10 * 1024 * 1024
    if uploaded_file.size > max_size:
        return JsonResponse(
            {"error": "File size exceeds 10MB limit."},
            status=400
        )

    # Fetch database objects
    try:
        teacher = Teacher.objects.get(id=teacher_id)
        subject = Subject.objects.get(id=subject_id)
        section = ClassSection.objects.get(id=section_id)
    except Teacher.DoesNotExist:
        return JsonResponse({"error": "Teacher not found."}, status=404)
    except Subject.DoesNotExist:
        return JsonResponse({"error": "Subject not found."}, status=404)
    except ClassSection.DoesNotExist:
        return JsonResponse({"error": "Section not found."}, status=404)

    # Authorization check
    if not TeacherSubjectAssignment.objects.filter(
        teacher=teacher,
        subject=subject,
        section=section
    ).exists():
        return JsonResponse(
            {"error": "Teacher not assigned to this subject and section."},
            status=403
        )

    # Save + Index
    try:
        with transaction.atomic():

            note = ClassNote.objects.create(
                class_id=section.name,
                subject_name=subject.name,
                pdf_file=uploaded_file
            )

            vector_dir = os.path.join(
                settings.BASE_DIR,
                "vector_indexes",
                teacher.department.replace(" ", "_"),
                section.name,
                subject.name.lower()
            )

            result = build_or_update_faiss_index(
                file_path=note.pdf_file.path,
                vector_dir=vector_dir
            )

    except Exception as e:
        return JsonResponse(
            {"error": f"Indexing failed: {str(e)}"},
            status=500
        )

    if result == "duplicate":
        message = "File already indexed. Duplicate skipped."
    else:
        message = "Notes uploaded and FAISS index updated successfully."

    return JsonResponse({
        "status": "success",
        "message": message,
        "section": section.name,
        "subject": subject.name
    })




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


from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .models import Teacher, TeacherSubjectAssignment, ClassNote

@require_GET
def get_notes_by_teacher(request, teacher_id):
    """
    Retrieve all notes for the subjects and sections assigned to a specific teacher.
    """
    try:
        # Check if teacher exists
        teacher = Teacher.objects.get(id=teacher_id)
    except Teacher.DoesNotExist:
        return JsonResponse({"error": "Teacher not found."}, status=404)

    # Get all subject/section assignments for this teacher
    assignments = TeacherSubjectAssignment.objects.filter(teacher=teacher).select_related('section', 'subject')
    
    if not assignments.exists():
        # If the teacher has no assigned classes, return an empty list
        return JsonResponse([], safe=False)

    # Build a dynamic query to match assigned class_id and subject_name
    query = Q()
    for assignment in assignments:
        query |= Q(
            class_id__iexact=assignment.section.name, 
            subject_name__iexact=assignment.subject.name
        )

    # Fetch notes matching the teacher's assignments
    notes = ClassNote.objects.filter(query).distinct().order_by('-uploaded_at')

    # Format the response data
    data = [
        {
            'id': note.id,
            'filename': note.pdf_file.name.split('/')[-1],
            'class_name': note.class_id,
            'subject_name': note.subject_name,
            'uploaded_at': note.uploaded_at.strftime('%Y-%m-%d %H:%M'),
            'file_url': note.pdf_file.url if note.pdf_file else None
        }
        for note in notes
    ]

    return JsonResponse(data, safe=False)




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

# @api_view(['POST'])
# def submit_quiz(request):
#     data = request.data

#     required_fields = ['quiz_id', 'student_roll_number', 'answers']
#     if not all(field in data for field in required_fields):
#         return Response({'error': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)

#     quiz_id = data['quiz_id']
#     roll_number = data['student_roll_number']
#     answers = data['answers']  # list of {question_id, selected_option}

#     if not isinstance(answers, list) or not answers:
#         return Response({'error': 'Answers must be a non-empty list'}, status=status.HTTP_400_BAD_REQUEST)

#     try:
#         student = Student.objects.get(roll_number=roll_number)
#         score = 0
#         attempt = StudentQuizAttempt.objects.create(student=student, quiz_id=quiz_id, score=0)

#         for ans in answers:
#             question_id = ans.get('question_id')
#             selected_option = ans.get('selected_option', '').upper()

#             if not question_id or selected_option not in ['A', 'B', 'C', 'D']:
#                 continue

#             try:
#                 question = Question.objects.get(id=question_id)
#                 is_correct = (selected_option == question.correct_option)
#                 if is_correct:
#                     score += 1

#                 StudentAnswer.objects.create(
#                     attempt=attempt,
#                     question=question,
#                     selected_option=selected_option,
#                     is_correct=is_correct
#                 )
#             except Question.DoesNotExist:
#                 continue

#         attempt.score = score
#         attempt.save()

#         return Response({'message': 'Quiz submitted successfully', 'score': score}, status=status.HTTP_200_OK)

#     except Student.DoesNotExist:
#         return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)
#     except Exception as e:
#         return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
   
# from rest_framework.decorators import api_view
# from rest_framework.response import Response
# from rest_framework import status
# from .models import Student, Quiz, Question, StudentQuizAttempt, StudentAnswer

# @api_view(['POST'])
# def submit_quiz(request):
#     data = request.data

#     required_fields = ['quiz_id', 'student_roll_number', 'answers']
#     if not all(field in data for field in required_fields):
#         return Response({'error': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)

#     quiz_id = data['quiz_id']
#     roll_number = data['student_roll_number']
#     answers = data['answers']  # list of {question_id, selected_option}

#     if not isinstance(answers, list) or not answers:
#         return Response({'error': 'Answers must be a non-empty list'}, status=status.HTTP_400_BAD_REQUEST)

#     try:
#         student = Student.objects.get(roll_number=roll_number)
#         quiz = Quiz.objects.get(id=quiz_id)

#         # Prevent duplicate attempts
#         if StudentQuizAttempt.objects.filter(student=student, quiz=quiz).exists():
#             return Response({'error': 'Quiz already attempted'}, status=status.HTTP_400_BAD_REQUEST)

#         score = 0
#         attempt = StudentQuizAttempt.objects.create(student=student, quiz=quiz, score=0)

#         for ans in answers:
#             question_id = ans.get('question_id')
#             selected_option = ans.get('selected_option', '').upper()

#             if not question_id or selected_option not in ['A', 'B', 'C', 'D']:
#                 continue

#             try:
#                 question = Question.objects.get(id=question_id)
#                 is_correct = (selected_option == question.correct_option)
#                 if is_correct:
#                     score += 1

#                 StudentAnswer.objects.create(
#                     attempt=attempt,
#                     question=question,
#                     selected_option=selected_option,
#                     is_correct=is_correct
#                 )
#             except Question.DoesNotExist:
#                 continue

#         attempt.score = score
#         attempt.save()

#         # Return detailed answers for frontend
#         answers_data = [
#             {
#                 "question_text": ans.question.text,
#                 "selected_option": ans.selected_option,
#                 "correct_option": ans.question.correct_option,
#                 "is_correct": ans.is_correct,
#             }
#             for ans in attempt.answers.all()
#         ]

#         return Response({
#             'message': 'Quiz submitted successfully',
#             'score': score,
#             'answers': answers_data
#         }, status=status.HTTP_200_OK)

#     except Student.DoesNotExist:
#         return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)
#     except Quiz.DoesNotExist:
#         return Response({'error': 'Quiz not found'}, status=status.HTTP_404_NOT_FOUND)
#     except Exception as e:
#         return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction

from .models import Student, Quiz, Question, StudentQuizAttempt, StudentAnswer


@api_view(['POST'])
def submit_quiz(request):
    data = request.data

    required_fields = ['quiz_id', 'student_roll_number', 'answers']
    if not all(field in data for field in required_fields):
        return Response(
            {'error': 'Missing required fields'},
            status=status.HTTP_400_BAD_REQUEST
        )

    quiz_id = data['quiz_id']
    roll_number = data['student_roll_number']
    answers = data['answers']  # list of {question_id, selected_option}

    if not isinstance(answers, list) or not answers:
        return Response(
            {'error': 'Answers must be a non-empty list'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        student = Student.objects.get(roll_number=roll_number)
        quiz = Quiz.objects.get(id=quiz_id)

        # 🚫 Prevent duplicate submissions
        if StudentQuizAttempt.objects.filter(student=student, quiz=quiz).exists():
            return Response(
                {'error': 'Quiz already attempted'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ✅ Atomic transaction guarantees consistency
        with transaction.atomic():
            attempt = StudentQuizAttempt.objects.create(
                student=student,
                quiz=quiz,
                score=0
            )

            score = 0
            valid_answer_count = 0

            for ans in answers:
                question_id = ans.get('question_id')
                selected_option = ans.get('selected_option')

                if not question_id or not selected_option:
                    continue

                selected_option = selected_option.upper()
                if selected_option not in ['A', 'B', 'C', 'D']:
                    continue

                try:
                    question = Question.objects.get(
                        id=question_id,
                        quiz=quiz   # 🔒 Enforce question–quiz consistency
                    )
                except Question.DoesNotExist:
                    continue

                is_correct = (selected_option == question.correct_option)
                if is_correct:
                    score += 1

                StudentAnswer.objects.create(
                    attempt=attempt,      # ✅ SAME attempt object
                    question=question,
                    selected_option=selected_option,
                    is_correct=is_correct
                )

                valid_answer_count += 1

            # 🚫 No valid answers → rollback
            if valid_answer_count == 0:
                raise ValueError("No valid answers submitted")

            attempt.score = score
            attempt.save()

        # ✅ Return saved answers
        answers_data = [
            {
                "question_text": ans.question.text,
                "selected_option": ans.selected_option,
                "correct_option": ans.question.correct_option,
                "is_correct": ans.is_correct,
            }
            for ans in attempt.answers.select_related("question")
        ]

        return Response(
            {
                'message': 'Quiz submitted successfully',
                'attempt_id': attempt.id,
                'score': score,
                'answers': answers_data
            },
            status=status.HTTP_200_OK
        )

    except Student.DoesNotExist:
        return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)

    except Quiz.DoesNotExist:
        return Response({'error': 'Quiz not found'}, status=status.HTTP_404_NOT_FOUND)

    except ValueError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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



# views.py
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import StudentQuizAttempt, Quiz
from .serializers import StudentQuizAttemptSerializer

@api_view(['GET'])
def teacher_quiz_performance(request, teacher_id):
    # Get all quizzes conducted by this teacher
    quizzes = Quiz.objects.filter(teacher_id=teacher_id)

    # Get all student attempts for those quizzes
    attempts = StudentQuizAttempt.objects.filter(quiz__in=quizzes).select_related('student', 'quiz').prefetch_related('answers')

    serializer = StudentQuizAttemptSerializer(attempts, many=True)
    return Response(serializer.data)
    



# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from .models import StudentQuizAttempt

# @csrf_exempt
# def get_student_quiz_attempts(request, student_id):
#     """
#     API endpoint: Get all quiz attempts for a student,
#     including score, quiz title, description, and subject.
#     """
#     if request.method == "GET":
#         attempts = StudentQuizAttempt.objects.filter(student__id=student_id).select_related("quiz__subject")

#         data = []
#         for attempt in attempts:
#             data.append({
#                 "quiz_id": attempt.quiz.id,
#                 "quiz_title": attempt.quiz.title,
#                 "quiz_description": attempt.quiz.description,
#                 "subject": attempt.quiz.subject.name,   # assuming Subject has a 'name' field
#                 "score": attempt.score,
#                 "submitted_at": attempt.submitted_at,
#             })

#         return JsonResponse({"attempts": data}, safe=False)
#     else:
#         return JsonResponse({"error": "Only GET method allowed"}, status=405)
# from django.http import JsonResponse
# from .models import StudentQuizAttempt

# def get_student_quiz_attempts(request, student_id):
#     # student_id here is actually the roll_number string
#     attempts = StudentQuizAttempt.objects.filter(student__roll_number=student_id).select_related("quiz__subject")

#     data = []
#     for attempt in attempts:
#         data.append({
#             "quiz_id": attempt.quiz.id,
#             "quiz_title": attempt.quiz.title,
#             "quiz_description": attempt.quiz.description,
#             "subject": attempt.quiz.subject.name if hasattr(attempt.quiz.subject, "name") else str(attempt.quiz.subject),
#             "score": attempt.score,
#             "submitted_at": attempt.submitted_at,
#         })

#     return JsonResponse({"attempts": data}, safe=False)

from django.http import JsonResponse
from .models import StudentQuizAttempt

def get_student_quiz_attempts(request, student_id):
    """
    API to fetch all quiz attempts for a student (by roll_number).
    Includes quiz info, section info, and detailed answers.
    """
    attempts = (
        StudentQuizAttempt.objects
        .filter(student__roll_number=student_id)
        .select_related("quiz__subject", "student__section")
        .prefetch_related("answers__question")
    )

    data = []
    for attempt in attempts:
        # Collect answers for this attempt
        def option_text(question, opt):
            return {
                "A": question.option_a,
                "B": question.option_b,
                "C": question.option_c,
                "D": question.option_d,
            }.get(opt)

        answers_data = [
            {
                "question_text": ans.question.text,
                "options": {
                    "A": ans.question.option_a,
                    "B": ans.question.option_b,
                    "C": ans.question.option_c,
                    "D": ans.question.option_d,
                },
                "selected_option": ans.selected_option,
                "selected_option_text": option_text(ans.question, ans.selected_option),
                "correct_option": ans.question.correct_option,
                "correct_option_text": option_text(
                    ans.question, ans.question.correct_option
                ),
                "is_correct": ans.is_correct,
            }
            for ans in attempt.answers.select_related("question")
        ]

        print(answers_data)
        # Build attempt dictionary
        data.append({
            "quiz_id": attempt.quiz.id,
            "quiz_title": attempt.quiz.title,
            "quiz_description": attempt.quiz.description,
            "subject": attempt.quiz.subject.name,
            "score": attempt.score,
            "submitted_at": attempt.submitted_at,
            "section_name": attempt.student.section.name if attempt.student.section else None,
            "section_year": attempt.student.section.year if attempt.student.section else None,
            "answers": answers_data,
        })

    return JsonResponse({"attempts": data})

# get student details by roll_number
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Student

@api_view(['GET'])
def get_student_details(request, student_id):
    """
    API to fetch student details by roll_number (student_id).
    """
    try:
        student = Student.objects.get(roll_number=student_id)
        data = {
            "roll_number": student.roll_number,
            "name": student.name,
            "email": student.email,
            "year": student.year,
            "section_id": student.section_id,
            "section": student.section.name if student.section else None
        }
        return Response(data, status=status.HTTP_200_OK)

    except Student.DoesNotExist:
        return Response(
            {"error": "Student not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": "Internal server error"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )



from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Student, Quiz, StudentQuizAttempt

@api_view(['GET'])
def get_unattempted_quizzes(request, student_id):
    """
    API to fetch all quizzes for a student's section that the student has NOT attempted yet.
    """
    try:
        # Step 1: Get student
        student = Student.objects.get(roll_number=student_id)

        # Step 2: Get student's section
        section = student.section
        if not section:
            return Response(
                {"error": "Student does not belong to any section"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Step 3: Get all quizzes for this section
        quizzes = Quiz.objects.filter(section=section)

        # Step 4: Get quizzes already attempted by student
        attempted_quiz_ids = StudentQuizAttempt.objects.filter(
            student=student
        ).values_list("quiz_id", flat=True)

        # Step 5: Filter quizzes not attempted
        unattempted_quizzes = quizzes.exclude(id__in=attempted_quiz_ids)

        # Prepare response data
        data = [
            {
                "quiz_id": quiz.id,
                "title": quiz.title,
                "description": quiz.description,
                "subject": quiz.subject.name,
                "teacher": quiz.teacher.name,
                "created_at": quiz.created_at
            }
            for quiz in unattempted_quizzes
        ]

        return Response({"unattempted_quizzes": data}, status=status.HTTP_200_OK)

    except Student.DoesNotExist:
        return Response({"error": "Student not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



# get quiz
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Quiz, Question

@api_view(['GET'])
def get_quiz_details(request, quiz_id):
    """
    API to fetch quiz details (title, description, subject, teacher, section)
    along with all questions and options using quiz_id.
    """
    try:
        quiz = Quiz.objects.get(id=quiz_id)

        # Prepare quiz metadata
        quiz_data = {
            "quiz_id": quiz.id,
            "title": quiz.title,
            "description": quiz.description,
            "subject": quiz.subject.name,
            "teacher": quiz.teacher.name,
            "section": quiz.section.name,
            "created_at": quiz.created_at,
        }

        # Prepare questions
        questions = Question.objects.filter(quiz=quiz)
        quiz_data["questions"] = [
            {
                "question_id": q.id,
                "text": q.text,
                "option_a": q.option_a,
                "option_b": q.option_b,
                "option_c": q.option_c,
                "option_d": q.option_d,
            }
            for q in questions
        ]

        return Response(quiz_data, status=status.HTTP_200_OK)

    except Quiz.DoesNotExist:
        return Response({"error": "Quiz not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Teacher, TeacherSubjectAssignment

@api_view(['GET'])
def get_teacher_assignments(request, teacher_id):
    """
    API to fetch all sections and subjects assigned to a teacher using teacher_id.
    """
    try:
        teacher = Teacher.objects.get(id=teacher_id)
        assignments = TeacherSubjectAssignment.objects.filter(teacher=teacher)

        data = {
            "teacher_id": teacher.id,
            "teacher_name": teacher.name,
            "department": teacher.department,
            "assignments": [
                {
                    "section_id": a.section.id,
                    "section_name": a.section.name,
                    "subject_id": a.subject.id,
                    "subject_name": a.subject.name,
                }
                for a in assignments
            ]
        }
        return Response(data, status=status.HTTP_200_OK)

    except Teacher.DoesNotExist:
        return Response({"error": "Teacher not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



from .models import ChatSession

@csrf_exempt
@require_POST
def create_new_chat(request):
    data = json.loads(request.body)

    roll_number = data.get("roll_number")
    subject_id = data.get("subject_id")

    try:
        student = Student.objects.get(roll_number=roll_number)
        subject = Subject.objects.get(id=subject_id)
    except:
        return JsonResponse({"error": "Invalid student or subject"}, status=400)

    session = ChatSession.objects.create(
        student=student,
        subject=subject,
        section=student.section,
        title="New Conversation"
    )

    return JsonResponse({"session_id": session.id})



def get_student_chats(request, roll_number):
    try:
        student = Student.objects.get(roll_number=roll_number)
    except:
        return JsonResponse({"error": "Student not found"}, status=404)

    sessions = ChatSession.objects.filter(
        student=student
    ).order_by("-updated_at")

    data = []

    for session in sessions:
        data.append({
            "session_id": session.id,
            "title": session.title or session.subject.name,
            "subject": session.subject.name,
            "updated_at": session.updated_at
        })

    return JsonResponse({"sessions": data})


from .models import ChatMessage
def get_chat_history(request, session_id):
    try:
        session = ChatSession.objects.get(id=session_id)
    except:
        return JsonResponse({"error": "Invalid session"}, status=404)

    messages = ChatMessage.objects.filter(
        session=session
    ).order_by("created_at")

    data = []

    for msg in messages:
        data.append({
            "sender": msg.sender,
            "message": msg.message_text,
            "created_at": msg.created_at
        })

    return JsonResponse({"messages": data})



# from .rag_faiss_utils import load_faiss_index, search_with_threshold
# from langchain_openai import ChatOpenAI
# from django.utils import timezone
# from dotenv import load_dotenv
# import os
# import json
# load_dotenv()
# OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# @csrf_exempt
# @require_POST
# def ask_question(request):
    
#     data = json.loads(request.body)

#     session_id = data.get("session_id")
#     question = data.get("question")

#     try:
#         session = ChatSession.objects.get(id=session_id)
#     except:
#         return JsonResponse({"error": "Invalid session"}, status=400)

#     # 🔹 Load FAISS index
#     vector_dir = os.path.join(
#     settings.BASE_DIR,
#     "vector_indexes",
#     session.subject.teachersubjectassignment_set.first().teacher.department.replace(" ", "_"),
#     session.section.name,
#     session.subject.name.lower()
#     )


#     try:
#         vectorstore = load_faiss_index(vector_dir)
#         print(vector_dir)
#     except:
#         print('the vector dir is ',vector_dir)
#         print('the os path is ',os.path.exists(vector_dir))

#         return JsonResponse({
#             "answer": "No syllabus content found for this subject."
#         })

#     docs = search_with_threshold(vectorstore, question, k=3)

#     if not docs:
#         answer = "This question is outside the syllabus and no docs."
#     else:
#         retrieved_context = "\n\n".join(
#             [doc.page_content for doc in docs]
#         )

#         # 🔹 Load recent history (last 6 messages)
#         history = ChatMessage.objects.filter(
#             session=session
#         ).order_by("-created_at")[:6]

#         history = reversed(history)

#         messages = []

#         messages.append({
#             "role": "system",
#             "content": (
#                 "You are a syllabus-constrained academic assistant. "
#                 "Use only authorized syllabus content. "
#                 "If answer not found, say: "
#                 "'This question is outside the syllabus.'"
#             )
#         })

#         for msg in history:
#             role = "user" if msg.sender == "USER" else "assistant"
#             messages.append({
#                 "role": role,
#                 "content": msg.message_text
#             })

#         messages.append({
#             "role": "system",
#             "content": f"Authorized syllabus content:\n{retrieved_context}"
#         })

#         messages.append({
#             "role": "user",
#             "content": question
#         })

#         llm = ChatOpenAI(
#             model="nvidia/nemotron-3-nano-30b-a3b:free",
#             openai_api_key=OPENROUTER_API_KEY,
#             openai_api_base="https://openrouter.ai/api/v1",
#             temperature=0
#         )

#         response = llm.invoke(messages)
#         answer = response.content.strip()

#     # 🔹 Save messages
#     ChatMessage.objects.create(
#         session=session,
#         sender="USER",
#         message_text=question
#     )

#     ChatMessage.objects.create(
#         session=session,
#         sender="BOT",
#         message_text=answer
#     )

#     # 🔹 Update session timestamp
#     session.updated_at = timezone.now()

#     # 🔹 Auto-generate title
#     if session.title == "New Conversation":
#         session.title = question[:50]
#     session.save()

#     return JsonResponse({"answer": answer})



# from .rag_faiss_utils import get_hybrid_retriever
# from langchain_openai import ChatOpenAI
# from django.utils import timezone
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from django.views.decorators.http import require_POST
# from django.conf import settings
# from .models import ChatSession, ChatMessage
# import os
# import json
# from dotenv import load_dotenv
# from langchain_classic.callbacks.tracers import LangChainTracer
# from pydantic import BaseModel, Field

# load_dotenv()
# # We use the OpenRouter Key to access the Nvidia model
# OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
# tracer = LangChainTracer(project_name=os.getenv("LANGSMITH_PROJECT"))
# @csrf_exempt
# @require_POST
# def ask_question(request):
#     data = json.loads(request.body)
#     session_id = data.get("session_id")
#     question = data.get("question")

#     try:
#         session = ChatSession.objects.get(id=session_id)
#     except ChatSession.DoesNotExist:
#         return JsonResponse({"error": "Invalid session"}, status=400)

#     # 🔹 1. Construct Path to Vector Store
#     # Note: Ensure the teacher relationship exists
#     teacher_assignment = session.subject.teachersubjectassignment_set.first()
#     if not teacher_assignment:
#          return JsonResponse({"answer": "No teacher assigned to this subject yet."})

#     vector_dir = os.path.join(
#         settings.BASE_DIR,
#         "vector_indexes",
#         teacher_assignment.teacher.department.replace(" ", "_"),
#         session.section.name,
#         session.subject.name.lower()
#     )

#     # 🔹 2. Get Hybrid Retriever
#     retriever = get_hybrid_retriever(vector_dir)
    
#     if not retriever:
#         return JsonResponse({
#             "answer": "No syllabus content found for this subject."
#         })

#     # 🔹 3. Retrieve Documents (Vector + Keyword)
#     docs = retriever.invoke(question)

#     if not docs:
#         retrieved_context = "No relevant context found in notes."
#     else:
#         retrieved_context = "\n\n".join([doc.page_content for doc in docs])

#     # 🔹 4. Build Chat History
#     history = ChatMessage.objects.filter(session=session).order_by("-created_at")[:6]
#     history = reversed(history)

#     messages = []
#     class Good_response(BaseModel):
#         answer: str
#         follow_up_question_1: str
#         follow_up_question_2: str
#         follow_up_question_3: str

    
#     # System Prompt: Strict Syllabus Adherence
#     messages.append({
#         "role": "system",
#         "content": (
#             "You are a helpful academic assistant strictly bound by the provided syllabus context. "
#             "Use ONLY the Context below to answer. "
#             "If the answer is not in the Context, explicitly state: 'This question is outside the syllabus provided in the notes.' "
#             "Do not hallucinate or use outside knowledge."
#         )
#     })

#     # Add History
#     for msg in history:
#         role = "user" if msg.sender == "USER" else "assistant"
#         messages.append({"role": role, "content": msg.message_text})

#     # Add Current Question + Context
#     messages.append({
#         "role": "user",
#         "content": f"Context:\n{retrieved_context}\n\nQuestion: {question}"
#     })

#     # 🔹 5. Call LLM (NVIDIA Model via OpenRouter)
#     # We use ChatOpenAI client because OpenRouter is OpenAI-compatible
#     llm = ChatOpenAI(
#         model="nvidia/nemotron-3-nano-30b-a3b:free", # Your specific model
#         openai_api_key=OPENROUTER_API_KEY,
#         openai_api_base="https://openrouter.ai/api/v1",
#         temperature=0.2, # Low temperature for factual accuracy
#         callbacks = [tracer]

#     )
#     llm_with_structured_output = llm.with_structured_output(Good_response)

#     try:
#         response = llm_with_structured_output.invoke(messages)
#     except Exception as e:
#         return JsonResponse({"error": str(e)}, status=500)

#     answer = response.answer

#     # 🔹 6. Save Conversation
#     ChatMessage.objects.create(session=session, sender="USER", message_text=question)
#     ChatMessage.objects.create(session=session, sender="BOT", message_text=answer)
    
#     session.updated_at = timezone.now()
#     if session.title == "New Conversation":
#         session.title = question[:50]
#     session.save()
#     print(answer, follow_ups)
#     return JsonResponse({
#     "answer": answer,
#     "follow_up_questions": follow_ups[:3]
# })




from .rag_faiss_utils import get_hybrid_retriever
from langchain_openai import ChatOpenAI
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
from .models import ChatSession, ChatMessage
import os
import json
import re
from dotenv import load_dotenv
from langchain_classic.callbacks.tracers import LangChainTracer

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
tracer = LangChainTracer(project_name=os.getenv("LANGSMITH_PROJECT"))


@csrf_exempt
@require_POST
def ask_question(request):
    try:
        data = json.loads(request.body)
        session_id = data.get("session_id")
        question = data.get("question")

        if not session_id or not question:
            return JsonResponse({"error": "Missing session_id or question"}, status=400)

        try:
            session = ChatSession.objects.get(id=session_id)
        except ChatSession.DoesNotExist:
            return JsonResponse({"error": "Invalid session"}, status=400)

        # 🔹 1. Construct Vector Path
        teacher_assignment = session.subject.teachersubjectassignment_set.first()
        if not teacher_assignment:
            return JsonResponse({
                "answer": "No teacher assigned to this subject yet.",
                "follow_up_questions": []
            })

        vector_dir = os.path.join(
            settings.BASE_DIR,
            "vector_indexes",
            teacher_assignment.teacher.department.replace(" ", "_"),
            session.section.name,
            session.subject.name.lower()
        )

        # 🔹 2. Get Retriever
        retriever = get_hybrid_retriever(vector_dir)

        if not retriever:
            return JsonResponse({
                "answer": "No syllabus content found for this subject.",
                "follow_up_questions": []
            })

        # 🔹 3. Retrieve Context
        docs = retriever.invoke(question)

        if not docs:
            retrieved_context = "No relevant context found in notes."
        else:
            retrieved_context = "\n\n".join([doc.page_content for doc in docs])

        # 🔹 4. Build Chat History (Last 6 Messages)
        history = ChatMessage.objects.filter(session=session)\
            .order_by("-created_at")[:6]
        history = reversed(history)

        messages = []

        # 🔹 Strict JSON + Syllabus Enforcement Prompt
        system_prompt = (
            "You are a helpful academic assistant strictly bound by the terms provided in the syllabus context.\n"
            "Use ONLY the terms used in Context below to answer, but you are free to use outside examples to simplify the answers.\n"
            "If the answer is not in the Context, respond exactly:\n"
            "'This question is outside the syllabus provided in the notes.'\n\n"
            "If the user says to explain in detail use some examples outside of the cotext but don't introduce new terms to the response:\n"
            "You MUST respond ONLY in valid JSON format like this:\n"
            "{\n"
            '  "answer": "string",\n'
            '  "follow_up_questions": ["q1", "q2", "q3"]\n'
            "}\n"
            "Do not include any extra text outside JSON."
        )

        messages.append({
            "role": "system",
            "content": system_prompt
        })

        # Add conversation history
        for msg in history:
            role = "user" if msg.sender == "USER" else "assistant"
            messages.append({
                "role": role,
                "content": msg.message_text
            })

        # Add current question with context
        messages.append({
            "role": "user",
            "content": f"Context:\n{retrieved_context}\n\nQuestion: {question}"
        })

        # 🔹 5. Call LLM
        llm = ChatOpenAI(
            model="nvidia/nemotron-3-nano-30b-a3b:free",
            openai_api_key=OPENROUTER_API_KEY,
            openai_api_base="https://openrouter.ai/api/v1",
            temperature=0.2,
            callbacks=[tracer]
        )

        raw_response = llm.invoke(messages)
        content = raw_response.content.strip()

        # 🔹 6. Safe JSON Extraction
        try:
            # Try direct parse
            parsed = json.loads(content)
        except json.JSONDecodeError:
            # Try extracting JSON block if model added extra text
            json_match = re.search(r"\{.*\}", content, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group())
            else:
                raise ValueError("Model did not return valid JSON.")

        answer = parsed.get("answer", "Error generating answer.")
        follow_ups = parsed.get("follow_up_questions", [])

        # Ensure exactly 3 follow-ups
        if not isinstance(follow_ups, list):
            follow_ups = []

        while len(follow_ups) < 3:
            follow_ups.append("")

        follow_ups = follow_ups[:3]

        # 🔹 7. Save Conversation
        ChatMessage.objects.create(
            session=session,
            sender="USER",
            message_text=question
        )

        ChatMessage.objects.create(
            session=session,
            sender="BOT",
            message_text=answer
        )

        session.updated_at = timezone.now()
        if session.title == "New Conversation":
            session.title = question[:50]
        session.save()

        return JsonResponse({
            "answer": answer,
            "follow_up_questions": follow_ups
        })

    except Exception as e:
        print("🔥 API Error:", str(e))
        return JsonResponse({
            "answer": "Error generating response.",
            "follow_up_questions": []
        }, status=500)






from django.http import JsonResponse
from .models import Student, TeacherSubjectAssignment

@csrf_exempt

def get_student_subjects(request, roll_number):
    try:
        student = Student.objects.get(roll_number=roll_number)
    except Student.DoesNotExist:
        return JsonResponse({"error": "Student not found"}, status=404)

    section = student.section

    # Get subjects assigned to this section
    assignments = TeacherSubjectAssignment.objects.filter(
        section=section
    ).select_related("subject")

    subjects = []
    unique_subject_ids = set()

    for assignment in assignments:
        if assignment.subject.id not in unique_subject_ids:
            subjects.append({
                "id": assignment.subject.id,
                "name": assignment.subject.name
            })
            unique_subject_ids.add(assignment.subject.id)

    return JsonResponse({"subjects": subjects})




import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from .models import Notification, Teacher, ClassSection, Subject, Student

# ---------------------------------------------------------
# TEACHER: Create a Notification
# ---------------------------------------------------------
@csrf_exempt
@require_POST
def create_notification(request):
    try:
        data = json.loads(request.body)
        
        teacher_id = data.get('teacher_id')
        section_id = data.get('section_id')
        subject_id = data.get('subject_id') # Optional
        title = data.get('title')
        message = data.get('message')
        deadline = data.get('deadline') # Expected format: "YYYY-MM-DDTHH:MM:SSZ" or None

        # Validation
        if not all([teacher_id, section_id, title, message]):
            return JsonResponse({"error": "Missing required fields (teacher_id, section_id, title, message)."}, status=400)

        teacher = Teacher.objects.get(id=teacher_id)
        section = ClassSection.objects.get(id=section_id)
        subject = Subject.objects.get(id=subject_id) if subject_id else None

        # Create Notification
        notification = Notification.objects.create(
            teacher=teacher,
            section=section,
            subject=subject,
            title=title,
            message=message,
            deadline=deadline
        )

        return JsonResponse({
            "status": "success", 
            "message": "Notification created successfully.",
            "notification_id": notification.id
        }, status=201)

    except Teacher.DoesNotExist:
        return JsonResponse({"error": "Teacher not found."}, status=404)
    except ClassSection.DoesNotExist:
        return JsonResponse({"error": "Section not found."}, status=404)
    except Subject.DoesNotExist:
        return JsonResponse({"error": "Subject not found."}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# ---------------------------------------------------------
# STUDENT: Get Notifications
# ---------------------------------------------------------
@require_GET
def get_student_notifications(request, roll_number):
    try:
        student = Student.objects.select_related('section').get(roll_number=roll_number)
    except Student.DoesNotExist:
        return JsonResponse({"error": "Student not found."}, status=404)

    if not student.section:
        return JsonResponse([], safe=False)

    # Fetch notifications for the student's section, newest first
    notifications = Notification.objects.filter(section=student.section).order_by('-created_at')

    data = []
    for notif in notifications:
        data.append({
            "id": notif.id,
            "title": notif.title,
            "message": notif.message,
            "teacher_name": notif.teacher.name,
            "subject_name": notif.subject.name if notif.subject else "General Announcement",
            "deadline": notif.deadline.isoformat() if notif.deadline else None,
            "created_at": notif.created_at.strftime('%Y-%m-%d %H:%M'),
        })

    return JsonResponse(data, safe=False)

    # ---------------------------------------------------------
# TEACHER: Get Created Notifications
# ---------------------------------------------------------
@require_GET
def get_teacher_notifications(request, teacher_id):
    try:
        # Check if the teacher exists
        teacher = Teacher.objects.get(id=teacher_id)
    except Teacher.DoesNotExist:
        return JsonResponse({"error": "Teacher not found."}, status=404)

    # Fetch notifications created by this teacher
    # Using select_related to optimize database queries for section and subject names
    notifications = Notification.objects.filter(teacher=teacher).select_related('section', 'subject').order_by('-created_at')

    data = []
    for notif in notifications:
        data.append({
            "id": notif.id,
            "title": notif.title,
            "message": notif.message,
            "section_name": notif.section.name,
            "subject_name": notif.subject.name if notif.subject else "General Announcement",
            "deadline": notif.deadline.isoformat() if notif.deadline else None,
            "created_at": notif.created_at.strftime('%Y-%m-%d %H:%M'),
        })

    return JsonResponse(data, safe=False)