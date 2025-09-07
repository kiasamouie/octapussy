#!/bin/bash
set -e

# Usage: ./clone_app.sh <new_app_name>
NEW_APP=$1
BASE_APP="youtubedl"
DJANGO_DIR="$(dirname "$0")/django"

if [ -z "$NEW_APP" ]; then
  echo "❌ Please provide a new app name"
  echo "Usage: ./clone_app.sh <new_app_name>"
  exit 1
fi

SRC="$DJANGO_DIR/$BASE_APP"
DST="$DJANGO_DIR/$NEW_APP"

if [ ! -d "$SRC" ]; then
  echo "❌ Base app $BASE_APP not found in $DJANGO_DIR"
  exit 1
fi

if [ -d "$DST" ]; then
  echo "⚠️  Destination $DST already exists, aborting."
  exit 1
fi

# Copy folder
cp -r "$SRC" "$DST"

# Clean __pycache__ and migrations (except __init__.py)
rm -rf "$DST/__pycache__"
rm -rf "$DST/migrations/"[0-9]*.py
rm -rf "$DST/migrations/__pycache__"

# Replace occurrences of base app name inside files (case sensitive)
find "$DST" -type f -exec sed -i "s/$BASE_APP/$NEW_APP/g" {} +

cat > "$DST/admin.py" <<EOF
from django.contrib import admin
from .models import ${NEW_APP^}

admin.site.register(${NEW_APP^})
EOF

# Reset important files to valid skeletons
cat > "$DST/models.py" <<EOF
from django.db import models

class ${NEW_APP^}(models.Model):
    # Add your fields here
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)
EOF

cat > "$DST/serializers.py" <<EOF
from rest_framework import serializers
from .models import ${NEW_APP^}
from datetime import datetime, timezone
from django.db import transaction

class ${NEW_APP^}Serializer(serializers.ModelSerializer):
    upload_id = serializers.CharField(validators=[])

    class Meta:
        model = ${NEW_APP^}
        fields = "__all__"
EOF

cat > "$DST/tasks.py" <<EOF
from celery import shared_task

@shared_task
def example_task():
    return "Task from $NEW_APP ran successfully!"
EOF

cat > "$DST/tests.py" <<EOF
from django.test import TestCase
from .models import ${NEW_APP^}

class ${NEW_APP^}TestCase(TestCase):
    def test_placeholder(self):
        self.assertTrue(True)
EOF

cat > "$DST/viewsets.py" <<EOF
from rest_framework import viewsets
from .models import ${NEW_APP^}
from .serializers import ${NEW_APP^}Serializer

class ${NEW_APP^}ViewSet(viewsets.ModelViewSet):
    queryset = ${NEW_APP^}.objects.all()
    serializer_class = ${NEW_APP^}Serializer
EOF

# Update settings.py
SETTINGS_FILE="$DJANGO_DIR/core/settings.py"
if grep -q "'$NEW_APP'," $SETTINGS_FILE; then
  echo "⚠️  $NEW_APP already in INSTALLED_APPS"
else
  sed -i "/INSTALLED_APPS = \[/a \ \ \ \ '$NEW_APP'," $SETTINGS_FILE
  echo "✅ Added $NEW_APP to INSTALLED_APPS"
fi

echo "🎉 App cloned from $BASE_APP to $NEW_APP successfully!"
echo "👉 Run migrations next: docker compose exec django python manage.py makemigrations $NEW_APP"
