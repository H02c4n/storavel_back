# apps/languages/models.py
from django.db import models
from django.conf import settings

class Language(models.Model):
    SCRIPT_CHOICES = [
        ('latin', 'Latin'),
        ('arabic', 'Arabic'),
        ('cjk', 'CJK'),
        ('cyrillic', 'Cyrillic'),
    ]
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    native_name = models.CharField(max_length=100)
    flag_emoji = models.CharField(max_length=10, blank=True)
    script = models.CharField(max_length=10, choices=SCRIPT_CHOICES, default='latin')
    rtl = models.BooleanField(default=False)
    has_romanization = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

class UserTargetLanguage(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='target_languages')
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    is_primary = models.BooleanField(default=False)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'language')

    def __str__(self):
        return f"{self.user.email} - {self.language.code}"