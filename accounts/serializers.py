
from rest_framework import serializers
from django.utils import timezone
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    is_admin = serializers.BooleanField(write_only=False, default=False, required=False)
    deletion_date = serializers.DateTimeField(required=True)

    class Meta:
        model = User
        fields = ['name', 'last_name', 'family_name', 'id_card', 'education_level',
                  'work_place', 'education_place', 'home', 'phone_number', 'email', 'password',
                  'confirm_password', 'is_admin', 'avatar', 'deletion_date']

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError('Passwords do not match')
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = User.objects.create_user(**validated_data)
        return user





class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['name', 'last_name', 'family_name', 'id_card', 'education_level',
                  'work_place', 'education_place', 'home', 'email', 'avatar', 'deletion_date']
        read_only_fields = ['phone_number']

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.family_name = validated_data.get('family_name', instance.family_name)
        instance.id_card = validated_data.get('id_card', instance.id_card)
        instance.education_level = validated_data.get('education_level', instance.education_level)
        instance.work_place = validated_data.get('work_place', instance.work_place)
        instance.education_place = validated_data.get('education_place', instance.education_place)
        instance.home = validated_data.get('home', instance.home)
        instance.email = validated_data.get('email', instance.email)
        instance.deletion_date = validated_data.get('deletion_date', instance.deletion_date)
        if 'avatar' in validated_data:
            instance.avatar = validated_data['avatar']
        elif not instance.avatar:
            instance.avatar = 'accounts/avatars/avatar.jpg'
        instance.save()
        return instance









class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'phone_number', 'name', 'last_name', 'family_name', 'id_card', 'education_level',
                  'work_place', 'education_place', 'home', 'email', 'avatar', 'deletion_date']






class PasswordResetSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    class Meta:
        fields = ['old_password', 'new_password']

    def validate(self, data):
        if data['old_password'] == data['new_password']:
            raise serializers.ValidationError("The new password cannot be the same as the old password.")
        return data








class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        # Ensure the phone number is provided in the correct format
        phone_number = attrs.get("phone_number")
        if not phone_number:
            raise serializers.ValidationError("Phone number is required.")

        # Perform standard validation and obtain user instance
        data = super().validate(attrs)
        user = self.user
        print(user.deletion_date)

        # Additional check for deletion date
        if user.deletion_date and user.deletion_date <= timezone.now():
            raise serializers.ValidationError("Your account has expired. Please contact support.")

        # Return the token data
        return data

