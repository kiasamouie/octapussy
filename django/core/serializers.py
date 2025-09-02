from djoser.serializers import UserSerializer
from rest_framework import serializers
from .models import Profile
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['phone_number', 'address']  # Add your custom fields here

class CustomUserSerializer(UserSerializer):
    is_superuser = serializers.BooleanField(read_only=True)
    is_staff = serializers.BooleanField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    date_joined = serializers.DateTimeField(read_only=True)
    last_login = serializers.DateTimeField(read_only=True)
    groups = serializers.StringRelatedField(many=True, read_only=True)
    user_permissions = serializers.StringRelatedField(many=True, read_only=True)
    profile = ProfileSerializer()  # Removed read_only=True to allow updates

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + (
            'is_superuser',
            'is_staff',
            'first_name',
            'last_name',
            'date_joined',
            'last_login',
            'groups',
            'user_permissions',
            'profile',
        )

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', None)
        instance = super().update(instance, validated_data)
        if profile_data:
            Profile.objects.update_or_create(user=instance, defaults=profile_data)
        return instance

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
