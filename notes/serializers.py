# serializers.py
from rest_framework import serializers
from .models import StudentQuizAttempt, StudentAnswer

class StudentAnswerSerializer(serializers.ModelSerializer):
    question_text = serializers.CharField(source='question.text', read_only=True)

    class Meta:
        model = StudentAnswer
        fields = ['question_text', 'selected_option', 'is_correct']


class StudentQuizAttemptSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.name', read_only=True)
    student_roll = serializers.CharField(source='student.roll_number', read_only=True)
    student_email = serializers.CharField(source='student.email', read_only=True)
    section_name = serializers.CharField(source='student.section.name', read_only=True)
    section_year = serializers.IntegerField(source='student.section.year', read_only=True)
    quiz_title = serializers.CharField(source='quiz.title', read_only=True)
    subject_name = serializers.CharField(source='quiz.subject.name', read_only=True)
    answers = StudentAnswerSerializer(many=True, read_only=True)

    class Meta:
        model = StudentQuizAttempt
        fields = [
            'id',
            'student_name',
            'student_roll',
            'student_email',
            'section_name',
            'section_year',
            'quiz_title',
            'subject_name',
            'score',
            'submitted_at',
            'answers'
        ]
