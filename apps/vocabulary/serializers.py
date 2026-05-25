from rest_framework import serializers
from .models import Word, WordTranslation, WordSynonym

class WordSerializer(serializers.ModelSerializer):
    translations = serializers.SerializerMethodField()
    synonyms = serializers.SerializerMethodField()

    class Meta:
        model = Word
        fields = ['id', 'language', 'word', 'part_of_speech', 'definition', 'romanization', 'audio_url', 'difficulty_level', 'translations', 'synonyms']

    def get_translations(self, obj):
        return {t.target_language.code: t.translation for t in obj.translations.all()}

    def get_synonyms(self, obj):
        return [s.synonym.word for s in obj.synonyms.all()]