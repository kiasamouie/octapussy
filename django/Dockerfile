FROM python:3.11-slim

WORKDIR /app

# Install system deps (incl. ffmpeg for yt-dlp)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app

# Entrypoint handles migrations + superuser + runserver
ENTRYPOINT ["/app/entrypoint.sh"]
