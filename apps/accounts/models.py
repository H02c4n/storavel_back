import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from cloudinary.models import CloudinaryField

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True, blank=True)
    display_name = models.CharField(max_length=150, blank=True)
    avatar = CloudinaryField('avatar', blank=True, null=True)
    bio = models.TextField(blank=True)
    native_language = models.ForeignKey('languages.Language', on_delete=models.SET_NULL, null=True, blank=True)
    is_premium = models.BooleanField(default=False)
    timezone = models.CharField(max_length=50, default='UTC')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email.split('@')[0]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email

class UserSettings(models.Model):
    FONT_SIZE_CHOICES = [('sm', 'Small'), ('md', 'Medium'), ('lg', 'Large')]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='settings')
    dark_mode = models.BooleanField(default=False)
    ui_language = models.CharField(max_length=10, default='en')
    notifications_enabled = models.BooleanField(default=True)
    streak_reminder_time = models.TimeField(null=True, blank=True)
    font_size = models.CharField(max_length=2, choices=FONT_SIZE_CHOICES, default='md')
    show_romanization = models.BooleanField(default=True)
    auto_play_audio = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.email} settings"