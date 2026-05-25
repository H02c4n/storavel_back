from rest_framework import serializers
from .models import UserWord, UserWordCollection
from apps.languages.models import Language

class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ['code', 'name', 'flag_emoji', 'native_name', 'rtl']

class UserWordSerializer(serializers.ModelSerializer):
    language = LanguageSerializer(read_only=True)

    class Meta:
        model = UserWord
        exclude = ['user']
        read_only_fields = ['id', 'status', 'times_reviewed', 'last_reviewed_at', 'next_review_at', 'ease_factor', 'created_at', 'updated_at']

class UserWordCreateSerializer(serializers.ModelSerializer):
    language = serializers.SlugRelatedField(
        slug_field='code',
        queryset=Language.objects.all()
    )

    class Meta:
        model = UserWord
        fields = ['language', 'word', 'part_of_speech', 'definition', 'example_sentence', 'translation', 'synonyms', 'romanization', 'audio_url', 'source_story', 'source_word']
        read_only_fields = ['id']

    def validate(self, attrs):
        user = self.context['request'].user
        language = attrs.get('language')
        word = attrs.get('word')
        if language and word:
            if UserWord.objects.filter(user=user, language=language, word=word).exists():
                raise serializers.ValidationError({"word": "already_saved"})
        return attrs

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class UserWordReviewSerializer(serializers.Serializer):
    quality = serializers.IntegerField(min_value=0, max_value=5)

class UserWordCollectionSerializer(serializers.ModelSerializer):
    word_count = serializers.SerializerMethodField()

    class Meta:
        model = UserWordCollection
        fields = ['id', 'name', 'description', 'color', 'icon', 'word_count', 'created_at']
        read_only_fields = ['id', 'created_at']

    def get_word_count(self, obj):
        return obj.words.count()

class UserWordCollectionDetailSerializer(serializers.ModelSerializer):
    words = UserWordSerializer(many=True, read_only=True)

    class Meta:
        model = UserWordCollection
        fields = '__all__'
        read_only_fields = ['id', 'user', 'created_at']

class AddRemoveWordSerializer(serializers.Serializer):
    word_id = serializers.UUIDField()