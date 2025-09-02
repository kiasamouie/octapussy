#!/bin/bash
set -e

echo "🚀 Applying migrations..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

echo "🚀 Creating superuser..."
python manage.py shell <<EOF
import os
from django.contrib.auth import get_user_model

User = get_user_model()
username = os.getenv("DJANGO_SU_USERNAME", "admin")
email = os.getenv("DJANGO_SU_EMAIL", "admin@admin.com")
password = os.getenv("DJANGO_SU_PASSWORD", "Password123!")

if not User.objects.filter(email=email).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
EOF

echo "🚀 Starting Django server on 0.0.0.0:5000..."
exec python manage.py runserver 0.0.0.0:5000