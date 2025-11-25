from . import views
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static


urlpatterns=[
    path("chatbot/", views.chatbot),
    # path("view/<int:note_id>/", views.view_note_content, name='view_note_content'),  # Assuming you have a view_note function to handle this
    path('upload/<int:class_id>/<str:subject>/', views.upload_notes, name='upload_notes'),
    path('api/notes/', views.get_notes_by_class_and_subject, name='get_notes_by_class_and_subject'),
    path('download/<int:note_id>/', views.download_note, name='download_note'),
    path('api/teacher/signup/', views.teacher_signup, name='teacher_signup'),
    path('api/teacher/login/', views.teacher_login, name='teacher_login'),
    path('api/student/signup/', views.student_signup, name='student_signup'),
    path('api/student/login/', views.student_login, name='student_login'),

]
urlpatterns += [
    path('api/quiz/create/', views.create_quiz),
    path('api/quiz/add-question/', views.add_question),
    path('api/quiz/submit/', views.submit_quiz),
    path('api/quiz/score/<str:student_roll_number>/<int:quiz_id>/', views.get_student_score),
    path('api/teacher/id/', views.get_teacher_id_by_email),
    path("api/student/<str:student_id>/quiz-attempts/", views.get_student_quiz_attempts, name="get_student_quiz_attempts"),

]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)