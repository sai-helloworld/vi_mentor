# use this to covert the unhashed passwords into hashed in the student table of the database

1. python manage.py shell
2. paste this
   from django.core.management.base import BaseCommand
   from django.contrib.auth.hashers import make_password
   from yourapp.models import Student

class Command(BaseCommand):
help = "Rehash plain text student passwords into Django's encrypted format"

    def handle(self, *args, **kwargs):
        updated = 0
        for student in Student.objects.all():
            if not student.password.startswith("pbkdf2_"):
                student.password = make_password(student.password)
                student.save()
                updated += 1
        self.stdout.write(self.style.SUCCESS(f"Rehashed {updated} student passwords"))
