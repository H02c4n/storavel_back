from django.contrib import admin
from .models import Word, WordTranslation, WordSynonym, StoryWord

@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    list_display = ('word', 'language', 'part_of_speech', 'difficulty_level')
    list_filter = ('language', 'part_of_speech', 'difficulty_level')
    search_fields = ('word', 'definition', 'romanization')

@admin.register(WordTranslation)
class WordTranslationAdmin(admin.ModelAdmin):
    list_display = ('word', 'target_language', 'translation')
    list_filter = ('target_language',)
    search_fields = ('word__word', 'translation')

@admin.register(WordSynonym)
class WordSynonymAdmin(admin.ModelAdmin):
    list_display = ('word', 'synonym')
    search_fields = ('word__word', 'synonym__word')

@admin.register(StoryWord)
class StoryWordAdmin(admin.ModelAdmin):
    list_display = ('story', 'word', 'order')
    list_filter = ('story__language',)
    search_fields = ('story__title', 'word__word')
    ordering = ('story', 'order')