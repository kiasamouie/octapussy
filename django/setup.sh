#!/bin/bash

# CREATE SCHEMA IF NOT EXISTS djangoapi;
# Apply migrations
echo "🚀 Applying migrations..."
python manage.py makemigrations
python manage.py migrate

# Create superuser automatically
echo "🚀 Creating superuser..."
echo "from django.contrib.auth import get_user_model; \
User = get_user_model(); \
User.objects.filter(email='admin@admin.com').exists() or \
User.objects.create_superuser('admin', 'admin@admin.com', 'Password123!')" | python manage.py shell

# Run Django server
echo "🚀 Starting Django server on localhost:5000..."
python manage.py runserver localhost:5000