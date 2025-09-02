from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from core.serializers import CustomUserSerializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = self.get_token(self.user)

        data["refresh"] = str(refresh)
        data["access"] = str(refresh.access_token)

        # Add custom user data
        user_data = CustomUserSerializer(self.user).data
        data.update(user_data)

        return data
