from django.contrib import admin
from .models import StoryTag, Story, StoryVersion, UserStoryProgress, UserNote

@admin.register(StoryTag)
class StoryTagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'language', 'level_min', 'level_max', 'story_type', 'is_published', 'is_premium', 'order')
    list_filter = ('language', 'story_type', 'level_min', 'level_max', 'is_published', 'is_premium')
    search_fields = ('title', 'slug')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('tags',)
    readonly_fields = ('id',)

@admin.register(StoryVersion)
class StoryVersionAdmin(admin.ModelAdmin):
    list_display = ('story', 'version_type', 'word_count', 'created_at')
    list_filter = ('version_type',)
    search_fields = ('story__title', 'content')
    readonly_fields = ('id', 'word_count')

@admin.register(UserStoryProgress)
class UserStoryProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'story', 'completed', 'read_count', 'quiz_best_score')
    list_filter = ('completed',)
    search_fields = ('user__email', 'story__title')
    readonly_fields = ('last_read_at',)

@admin.register(UserNote)
class UserNoteAdmin(admin.ModelAdmin):
    list_display = ('user', 'story', 'created_at', 'updated_at')
    search_fields = ('user__email', 'story__title', 'content')