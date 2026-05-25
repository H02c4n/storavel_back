from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password

from apps.languages.models import Language
from .models import User, UserSettings


class UserSerializer(serializers.ModelSerializer):
    native_language = serializers.SlugRelatedField(
        slug_field='code',
        queryset=Language.objects.all(),
        allow_null=True
    )

    avatar = serializers.ImageField(required=False)

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'username',
            'display_name',
            'avatar',
            'bio',
            'native_language',
            'is_premium',
            'timezone',
            'created_at'
        ]

        read_only_fields = [
            'id',
            'is_premium',
            'created_at'
        ]


class UserSettingsSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserSettings
        fields = '__all__'
        read_only_fields = ['user']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )

    password2 = serializers.CharField(
        write_only=True,
        required=True
    )

    class Meta:
        model = User
        fields = [
            'email',
            'username',
            'display_name',
            'password',
            'password2'
        ]

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({
                "password": "Passwords do not match"
            })

        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')

        user = User.objects.create_user(**validated_data)

        # Create default settings
        UserSettings.objects.create(user=user)

        return user