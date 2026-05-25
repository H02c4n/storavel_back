from rest_framework import serializers
from .models import Quiz, QuizQuestion, UserQuizAttempt

class QuizQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizQuestion
        exclude = ['correct_answer']

class QuizDetailSerializer(serializers.ModelSerializer):
    questions = QuizQuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = ['id', 'title', 'story', 'version_type', 'is_premium', 'questions']

class QuizAttemptSerializer(serializers.Serializer):
    answers = serializers.DictField(child=serializers.CharField())
    time_taken_seconds = serializers.IntegerField(min_value=0)
    version_type = serializers.CharField(required=False, default='original')

class UserQuizAttemptSerializer(serializers.ModelSerializer):
    quiz_title = serializers.CharField(source='quiz.title', read_only=True)
    story_slug = serializers.CharField(source='quiz.story.slug', read_only=True)

    class Meta:
        model = UserQuizAttempt
        fields = ['id', 'quiz', 'quiz_title', 'story_slug', 'score', 'correct_answers', 'total_questions', 'time_taken_seconds', 'created_at']