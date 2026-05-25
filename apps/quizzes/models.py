import uuid
from django.db import models
from django.conf import settings

class Quiz(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    story = models.ForeignKey('stories.Story', on_delete=models.CASCADE, related_name='quizzes')
    version_type = models.CharField(max_length=20)
    title = models.CharField(max_length=200)
    is_premium = models.BooleanField(default=False)

    class Meta:
        unique_together = ('story', 'version_type')

    def __str__(self):
        return self.title

class QuizQuestion(models.Model):
    TYPE_CHOICES = [
        ('true_false', 'True/False'),
        ('fill_blank', 'Fill in the Blank'),
        ('multiple_choice', 'Multiple Choice'),
        ('translation', 'Translation'),
    ]
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    hint_text = models.TextField(blank=True)
    correct_answer = models.TextField()
    options = models.JSONField(default=list)
    explanation = models.TextField(blank=True)
    question_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='multiple_choice')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

class UserQuizAttempt(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='quiz_attempts')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.FloatField()
    correct_answers = models.PositiveIntegerField()
    total_questions = models.PositiveIntegerField()
    answers = models.JSONField()
    time_taken_seconds = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)