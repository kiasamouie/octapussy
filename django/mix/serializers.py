from rest_framework import serializers
from .models import Mix
from datetime import datetime, timezone
from django.db import transaction

class MixSerializer(serializers.ModelSerializer):
    upload_id = serializers.CharField(validators=[])

    class Meta:
        model = Mix
        fields = "__all__"
