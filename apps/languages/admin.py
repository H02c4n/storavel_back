from django.contrib import admin
from .models import Language, UserTargetLanguage

@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'native_name', 'script', 'rtl', 'is_active', 'order')
    list_filter = ('is_active', 'script', 'rtl')
    search_fields = ('code', 'name', 'native_name')
    ordering = ('order', 'name')

@admin.register(UserTargetLanguage)
class UserTargetLanguageAdmin(admin.ModelAdmin):
    list_display = ('user', 'language', 'is_primary', 'added_at')
    list_filter = ('is_primary', 'language')
    search_fields = ('user__email', 'user__username', 'language__name')