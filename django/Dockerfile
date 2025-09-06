FROM python:3.11-slim

WORKDIR /app

# Install system deps (incl. ffmpeg for yt-dlp)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (better layer caching)
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . /app

# Run migrations, create superuser, then start Gunicorn on 5000
CMD ["/bin/bash", "-c", "\
  set -e && \
  echo '🚀 Applying migrations...' && \
  python manage.py makemigrations --noinput || true && \
  python manage.py migrate --noinput && \
  echo '🚀 Collecting static files...' && \
  python manage.py collectstatic --noinput && \
  echo '🚀 Creating superuser...' && \
  python manage.py shell -c \"import os; from django.contrib.auth import get_user_model; User=get_user_model(); username=os.getenv('DJANGO_SU_USERNAME','admin'); email=os.getenv('DJANGO_SU_EMAIL','admin@admin.com'); password=os.getenv('DJANGO_SU_PASSWORD','Password123!'); User.objects.filter(email=email).exists() or User.objects.create_superuser(username=username,email=email,password=password)\" && \
  echo '🚀 Starting Gunicorn (with autoreload) on 0.0.0.0:5000...' && \
  exec gunicorn core.wsgi:application --bind 0.0.0.0:5000 --workers 2 --reload --timeout 0 \
"]