from django.contrib import admin
from .models import Quiz, QuizQuestion, UserQuizAttempt

class QuizQuestionInline(admin.TabularInline):
    model = QuizQuestion
    extra = 1

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'story', 'version_type', 'is_premium')
    list_filter = ('version_type', 'is_premium', 'story__language')
    search_fields = ('title', 'story__title')
    inlines = [QuizQuestionInline]

@admin.register(QuizQuestion)
class QuizQuestionAdmin(admin.ModelAdmin):
    list_display = ('quiz', 'question_type', 'question_text', 'order')
    list_filter = ('question_type',)
    search_fields = ('question_text', 'correct_answer')

@admin.register(UserQuizAttempt)
class UserQuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('user', 'quiz', 'score', 'correct_answers', 'total_questions', 'created_at')
    list_filter = ('quiz__version_type',)
    search_fields = ('user__email', 'quiz__title')
    readonly_fields = ('id', 'created_at')