import uuid
from django.db import models
from django.conf import settings
from cloudinary.models import CloudinaryField
from core.utils import unique_slug_generator

class StoryTag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug_generator(self, 'slug', 'name')
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Story(models.Model):
    STORY_TYPE_CHOICES = [
        ('narrative', 'Narrative'),
        ('dialog', 'Dialog'),
        ('news', 'News'),
        ('business', 'Business'),
        ('academic', 'Academic'),
    ]
    LEVEL_CHOICES = [(c, c) for c in ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    language = models.ForeignKey('languages.Language', on_delete=models.CASCADE, related_name='stories')
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    level_min = models.CharField(max_length=2, choices=LEVEL_CHOICES, default='A1')
    level_max = models.CharField(max_length=2, choices=LEVEL_CHOICES, default='C2')
    story_type = models.CharField(max_length=20, choices=STORY_TYPE_CHOICES, default='narrative')
    cover_image = CloudinaryField('cover', blank=True, null=True)
    estimated_read_minutes = models.PositiveSmallIntegerField(default=5)
    is_premium = models.BooleanField(default=False)
    is_published = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    tags = models.ManyToManyField(StoryTag, blank=True)

    class Meta:
        ordering = ['order', 'title']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['language', 'is_published']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug_generator(self, 'slug', 'title')
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class StoryVersion(models.Model):
    VERSION_TYPES = [
        ('original', 'Original'),
        ('present', 'Present Tense'),
        ('past', 'Past Tense'),
        ('future', 'Future Tense'),
        ('native', 'Native Speaker'),
        ('dialog', 'Dialog Form'),
        ('idioms', 'Idioms Highlighted'),
        ('emotional', 'Emotional Tone'),
        ('vocabulary', 'Vocabulary Focus'),
        ('qa', 'Q&A Format'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='versions')
    version_type = models.CharField(max_length=20, choices=VERSION_TYPES)
    content = models.TextField()
    word_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('story', 'version_type')

    def save(self, *args, **kwargs):
        self.word_count = len(self.content.split())
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.story.title} - {self.version_type}"

class UserStoryProgress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='story_progress')
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='user_progress')
    last_version_read = models.CharField(max_length=20, blank=True)
    versions_read = models.JSONField(default=list)
    completed = models.BooleanField(default=False)
    read_count = models.PositiveIntegerField(default=0)
    last_read_at = models.DateTimeField(auto_now=True)
    quiz_best_score = models.IntegerField(default=0)
    time_spent_seconds = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('user', 'story')

class UserNote(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='story_notes')
    story = models.ForeignKey(Story, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'story')