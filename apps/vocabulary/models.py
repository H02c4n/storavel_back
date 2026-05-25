import uuid
from django.db import models
from django.conf import settings

class Word(models.Model):
    POS_CHOICES = [
        ('noun', 'Noun'), ('verb', 'Verb'), ('adjective', 'Adjective'),
        ('adverb', 'Adverb'), ('phrase', 'Phrase'), ('idiom', 'Idiom'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    language = models.ForeignKey('languages.Language', on_delete=models.CASCADE, related_name='words')
    word = models.CharField(max_length=100)
    part_of_speech = models.CharField(max_length=10, choices=POS_CHOICES, default='noun')
    definition = models.TextField()
    romanization = models.CharField(max_length=200, blank=True)
    audio_url = models.URLField(blank=True)
    difficulty_level = models.CharField(max_length=2, choices=[('A1','A1'),('A2','A2'),('B1','B1'),('B2','B2'),('C1','C1'),('C2','C2')], default='A1')

    class Meta:
        unique_together = ('language', 'word')
        indexes = [
            models.Index(fields=['language', 'word']),
        ]

    def __str__(self):
        return f"{self.word} ({self.language.code})"

class WordTranslation(models.Model):
    word = models.ForeignKey(Word, on_delete=models.CASCADE, related_name='translations')
    target_language = models.ForeignKey('languages.Language', on_delete=models.CASCADE)
    translation = models.TextField()

    class Meta:
        unique_together = ('word', 'target_language')

class WordSynonym(models.Model):
    word = models.ForeignKey(Word, on_delete=models.CASCADE, related_name='synonyms')
    synonym = models.ForeignKey(Word, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('word', 'synonym')

class StoryWord(models.Model):
    story = models.ForeignKey('stories.Story', on_delete=models.CASCADE, related_name='story_words')
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    example_sentence = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('story', 'word')
        ordering = ['order']