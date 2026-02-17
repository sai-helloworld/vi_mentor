from django.db import models

# 📘 Class Note Model
class ClassNote(models.Model):
    class_id = models.CharField(max_length=20)  # e.g., "CSE101", "MATH202"
    subject_name = models.CharField(max_length=100)  # e.g., "Data Structures"
    pdf_file = models.FileField(upload_to='notes_pdfs/')  # stored in MEDIA_ROOT/notes_pdfs/
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.subject_name} - {self.class_id}"

# 🏫 Class Section Model
class ClassSection(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20, unique=True)  # e.g., "10-A"
    year = models.IntegerField()

    def __str__(self):
        return self.name

# 👨‍🎓 Student Model
class Student(models.Model):
    roll_number = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128, default='default_password123')  # You can hash this manually
    year = models.IntegerField()
    section = models.ForeignKey(ClassSection, on_delete=models.SET_NULL, null=True, related_name='students')

    def __str__(self):
        return self.name

# 👩‍🏫 Teacher Model
class Teacher(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128, default='default_password123')  # You can hash this manually
    department = models.CharField(max_length=100)

    def __str__(self):
        return self.name

# 📚 Subject Model
class Subject(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

# 🧑‍🏫 Teacher-Subject-Section Assignment
class TeacherSubjectAssignment(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='assignments')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    section = models.ForeignKey(ClassSection, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('teacher', 'subject', 'section')

    def __str__(self):
        return f"{self.teacher.name} - {self.subject.name} - {self.section.name}"




# 📝 Quiz Model
class Quiz(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='quizzes')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    section = models.ForeignKey(ClassSection, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

# ❓ Question Model
class Question(models.Model):
    id = models.AutoField(primary_key=True)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    option_a = models.CharField(max_length=200)
    option_b = models.CharField(max_length=200)
    option_c = models.CharField(max_length=200)
    option_d = models.CharField(max_length=200)
    correct_option = models.CharField(max_length=1)  # 'A', 'B', 'C', or 'D'

    def __str__(self):
        return f"Q: {self.text[:50]}..."

# 🧮 Student Quiz Attempt
class StudentQuizAttempt(models.Model):
    id = models.AutoField(primary_key=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='quiz_attempts')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    score = models.IntegerField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.name} - {self.quiz.title}"

# ✅ Student Answer Model
class StudentAnswer(models.Model):
    attempt = models.ForeignKey(StudentQuizAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.CharField(max_length=1)  # 'A', 'B', 'C', or 'D'
    is_correct = models.BooleanField()

    def __str__(self):
        return f"{self.attempt.student.name} - Q{self.question.id} - {self.selected_option}"



# 🧠 Chat Session
class ChatSession(models.Model):
    id = models.AutoField(primary_key=True)
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="chat_sessions"
    )
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    section = models.ForeignKey(ClassSection, on_delete=models.CASCADE)

    title = models.CharField(max_length=255, blank=True)
    summary = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student.roll_number} - {self.title or self.subject.name}"


# 💬 Chat Message
class ChatMessage(models.Model):
    session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,
        related_name="messages"
    )
    sender = models.CharField(
        max_length=10,
        choices=[("USER", "User"), ("BOT", "Bot")]
    )
    message_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender}: {self.message_text[:30]}"
