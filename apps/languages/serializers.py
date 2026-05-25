from rest_framework import serializers
from .models import Language, UserTargetLanguage

class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ['code', 'name', 'native_name', 'flag_emoji', 'script', 'rtl', 'has_romanization']

class UserTargetLanguageSerializer(serializers.ModelSerializer):
    language = LanguageSerializer(read_only=True)
    language_code = serializers.SlugRelatedField(slug_field='code', queryset=Language.objects.all(), write_only=True)

    class Meta:
        model = UserTargetLanguage
        fields = ['id', 'language', 'language_code', 'is_primary', 'added_at']
        read_only_fields = ['id', 'added_at']