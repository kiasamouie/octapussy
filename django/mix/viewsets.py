from rest_framework import viewsets
from .models import Mix
from .serializers import MixSerializer

class MixViewSet(viewsets.ModelViewSet):
    queryset = Mix.objects.all()
    serializer_class = MixSerializer
