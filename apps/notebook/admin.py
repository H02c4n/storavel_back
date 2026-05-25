from django.contrib import admin
from .models import UserWord, UserWordCollection

@admin.register(UserWord)
class UserWordAdmin(admin.ModelAdmin):
    list_display = ('user', 'word', 'language', 'status', 'times_reviewed', 'next_review_at')
    list_filter = ('language', 'status')
    search_fields = ('user__email', 'word', 'definition', 'translation')
    readonly_fields = ('id', 'ease_factor', 'times_reviewed', 'last_reviewed_at', 'next_review_at', 'created_at', 'updated_at')

@admin.register(UserWordCollection)
class UserWordCollectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'color', 'created_at')
    search_fields = ('name', 'user__email')
    filter_horizontal = ('words',)