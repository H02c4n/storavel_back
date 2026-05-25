from rest_framework import serializers
from apps.vocabulary.models import StoryWord, Word
from .models import Story, StoryVersion, StoryTag, UserStoryProgress, UserNote

class StoryTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoryTag
        fields = ['name', 'slug']

class StoryVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoryVersion
        fields = ['id', 'version_type', 'content', 'word_count', 'created_at', 'updated_at']

class StoryListSerializer(serializers.ModelSerializer):
    language_code = serializers.CharField(source='language.code', read_only=True)

    class Meta:
        model = Story
        fields = ['id', 'title', 'slug', 'language', 'language_code', 'level_min', 'level_max', 'story_type', 'cover_image', 'estimated_read_minutes', 'is_premium', 'order', 'tags']

class StoryDetailSerializer(serializers.ModelSerializer):
    versions = StoryVersionSerializer(many=True, read_only=True)
    tags = StoryTagSerializer(many=True, read_only=True)
    language_code = serializers.CharField(source='language.code', read_only=True)

    class Meta:
        model = Story
        fields = '__all__'

class UserStoryProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserStoryProgress
        fields = ['last_version_read', 'versions_read', 'completed', 'read_count', 'last_read_at', 'quiz_best_score', 'time_spent_seconds']

class UserNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserNote
        fields = ['id', 'content', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class StoryWordSerializer(serializers.ModelSerializer):
    word_text = serializers.CharField(source='word.word', read_only=True)
    definition = serializers.CharField(source='word.definition', read_only=True)

    class Meta:
        model = StoryWord
        fields = ['id', 'word', 'word_text', 'definition', 'example_sentence', 'order']