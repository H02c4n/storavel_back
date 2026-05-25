from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator

class UserProgress(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='progress')
    language = models.ForeignKey('languages.Language', on_delete=models.CASCADE, null=True, blank=True)
    total_stories_read = models.PositiveIntegerField(default=0)
    total_words_learned = models.PositiveIntegerField(default=0)
    total_quiz_attempts = models.PositiveIntegerField(default=0)
    total_xp = models.PositiveIntegerField(default=0)
    current_streak_days = models.PositiveIntegerField(default=0)
    longest_streak_days = models.PositiveIntegerField(default=0)
    last_active_date = models.DateField(null=True, blank=True)

class DailyActivity(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='daily_activities')
    date = models.DateField()
    stories_read = models.PositiveIntegerField(default=0)
    words_reviewed = models.PositiveIntegerField(default=0)
    quizzes_taken = models.PositiveIntegerField(default=0)
    xp_earned = models.PositiveIntegerField(default=0)
    minutes_spent = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('user', 'date')

class Achievement(models.Model):
    code = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=50, blank=True)
    xp_reward = models.PositiveIntegerField(default=0)
    condition_type = models.CharField(max_length=50)
    condition_value = models.IntegerField()

    def __str__(self):
        return self.title

class UserAchievement(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='achievements')
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'achievement')