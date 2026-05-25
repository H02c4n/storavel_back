import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone

class UserWord(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('learning', 'Learning'),
        ('reviewing', 'Reviewing'),
        ('mastered', 'Mastered'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notebook_words')
    language = models.ForeignKey('languages.Language', on_delete=models.CASCADE)
    word = models.CharField(max_length=100)
    part_of_speech = models.CharField(max_length=20, blank=True)
    definition = models.TextField()
    example_sentence = models.TextField(blank=True)
    translation = models.CharField(max_length=200)
    synonyms = models.JSONField(default=list)
    romanization = models.CharField(max_length=200, blank=True)
    audio_url = models.URLField(blank=True)
    source_story = models.ForeignKey('stories.Story', on_delete=models.SET_NULL, null=True, blank=True)
    source_word = models.ForeignKey('vocabulary.Word', on_delete=models.SET_NULL, null=True, blank=True)

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='new')
    is_favorite = models.BooleanField(default=False)
    times_reviewed = models.PositiveIntegerField(default=0)
    last_reviewed_at = models.DateTimeField(null=True, blank=True)
    next_review_at = models.DateTimeField(null=True, blank=True)
    ease_factor = models.FloatField(default=2.5)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'language', 'word')
        indexes = [
            models.Index(fields=['user', 'next_review_at']),
            models.Index(fields=['user', 'status']),
        ]

    def save(self, *args, **kwargs):
        # Set next_review_at on first save so word appears in review queue
        if not self.next_review_at:
            self.next_review_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.email} - {self.word}"

class UserWordCollection(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='collections')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#4F46E5')
    icon = models.CharField(max_length=50, blank=True)
    words = models.ManyToManyField(UserWord, related_name='collections', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'name')

    def __str__(self):
        return f"{self.user.email} - {self.name}"