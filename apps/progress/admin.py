from django.contrib import admin
from .models import UserProgress, DailyActivity, Achievement, UserAchievement

@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'language', 'total_stories_read', 'total_words_learned', 'total_xp', 'current_streak_days')
    search_fields = ('user__email',)
    readonly_fields = ('total_stories_read', 'total_words_learned', 'total_xp', 'current_streak_days', 'longest_streak_days', 'last_active_date')

@admin.register(DailyActivity)
class DailyActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'stories_read', 'words_reviewed', 'quizzes_taken', 'xp_earned')
    list_filter = ('date',)
    search_fields = ('user__email',)

@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('code', 'title', 'xp_reward', 'condition_type', 'condition_value')
    search_fields = ('code', 'title')

@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    list_display = ('user', 'achievement', 'earned_at')
    list_filter = ('achievement',)
    search_fields = ('user__email', 'achievement__title')
    readonly_fields = ('earned_at',)