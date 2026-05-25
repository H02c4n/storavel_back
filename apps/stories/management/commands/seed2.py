import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.utils import timezone
from django.contrib.auth import get_user_model

from apps.languages.models import Language, UserTargetLanguage
from apps.stories.models import (
    Story,
    StoryVersion,
    StoryTag,
    UserStoryProgress,
)
from apps.vocabulary.models import (
    Word,
    WordTranslation,
    WordSynonym,
    StoryWord,
)
from apps.quizzes.models import (
    Quiz,
    QuizQuestion,
)
from apps.progress.models import (
    UserProgress,
    DailyActivity,
)
from apps.accounts.models import UserSettings

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed Allen vs Tom Cruise Story'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🌱 Seeding Allen Story...'))

        self.create_languages()

        demo_user = self.create_demo_user()

        tags = self.create_tags()

        allen_story = self.create_allen_story(demo_user, tags)

        vocab_words = self.create_vocabulary()

        self.link_words_to_story(allen_story, vocab_words)

        self.create_quiz(allen_story)

        self.create_progress(demo_user, allen_story)

        self.stdout.write(self.style.SUCCESS('✅ Allen Story Seed Completed!'))

    # ---------------------------------------------------
    # LANGUAGES
    # ---------------------------------------------------

    def create_languages(self):
        languages = [
            {
                'code': 'en',
                'name': 'English',
                'native_name': 'English',
                'flag_emoji': '🇺🇸',
                'script': 'latin',
                'rtl': False,
                'has_romanization': False,
                'is_active': True,
                'order': 1,
            },
            {
                'code': 'tr',
                'name': 'Turkish',
                'native_name': 'Türkçe',
                'flag_emoji': '🇹🇷',
                'script': 'latin',
                'rtl': False,
                'has_romanization': False,
                'is_active': True,
                'order': 2,
            },
        ]

        for lang_data in languages:
            Language.objects.get_or_create(
                code=lang_data['code'],
                defaults=lang_data
            )

    # ---------------------------------------------------
    # USER
    # ---------------------------------------------------

    def create_demo_user(self):

        user, created = User.objects.get_or_create(
            email='demo@storavel.com',
            defaults={
                'username': 'demo_user',
                'display_name': 'Demo User',
                'is_active': True,
                'is_premium': False,
            }
        )

        if created:
            user.set_password('demo123')
            user.save()

            UserSettings.objects.get_or_create(user=user)

        english = Language.objects.get(code='en')

        UserTargetLanguage.objects.get_or_create(
            user=user,
            language=english,
            defaults={
                'is_primary': True
            }
        )

        return user

    # ---------------------------------------------------
    # TAGS
    # ---------------------------------------------------

    def create_tags(self):

        tag_names = [
            'race',
            'motorcycle',
            'cars',
            'action',
            'san-francisco',
            'humor',
            'adventure',
            'competition',
            'police',
        ]

        tags = []

        for name in tag_names:

            tag, _ = StoryTag.objects.get_or_create(
                name=name,
                defaults={
                    'slug': slugify(name)
                }
            )

            tags.append(tag)

        return tags

    # ---------------------------------------------------
    # STORY
    # ---------------------------------------------------

    def create_allen_story(self, user, tags):

        english = Language.objects.get(code='en')

        story, created = Story.objects.get_or_create(
            slug='allen-vs-tom-cruise-race',
            defaults={
                'language': english,
                'title': 'The Unexpected Race on Van Ness',
                'level_min': 'A2',
                'level_max': 'B2',
                'story_type': 'narrative',
                'estimated_read_minutes': 15,
                'is_premium': False,
                'is_published': True,
                'order': 3,
            }
        )

        if created:
            story.tags.set(tags)

        versions = {

            'original': """
It is 5 o'clock and Allen is riding his motorcycle in San Francisco.

He rides down Van Ness Street and stops at a red light.

Suddenly, a red Ferrari pulls up next to him.

The driver wears dark sunglasses.

Allen looks over and realizes the driver is Tom Cruise.

Tom smirks and says, "When the light turns green, let's race."

Allen smiles and says, "Alright, you're on."

Tom laughs. "I'm gonna smoke you."

Allen replies, "You wish."

Both of them rev their engines loudly.

The light finally turns green.

They launch forward at top speed.

Tom starts winning at first.

But suddenly, police lights appear behind him.

The police pull Tom over.

Allen rides past him laughing.

"Better luck next time!" Allen shouts.

Allen wins the race.
""",

            'present': """
It's late afternoon in San Francisco, and Allen rides his motorcycle through busy traffic on Van Ness Street.

The cool wind hits his face while the city glows with evening light.

At a red light, a beautiful red Ferrari slowly pulls up beside him.

The driver wears black sunglasses and looks extremely confident.

Allen glances over.

Then he realizes something shocking.

It's Tom Cruise.

Tom gives him a confident smile.

"When the light turns green, let's race," he says.

Allen immediately accepts the challenge.

Both engines roar loudly while people nearby stare at them.

The light turns green.

They explode forward through the street.

The Ferrari quickly takes the lead.

Allen pushes harder and harder.

Then suddenly, flashing blue and red police lights appear behind Tom.

Police sirens scream through the street.

Tom slows down as police officers pull him over.

Allen speeds past him laughing loudly.

He raises his hand and yells, "Better luck next time!"
""",

            'past': """
Last evening, Allen experienced the strangest race of his life.

He was riding his motorcycle through San Francisco when a red Ferrari stopped beside him at a traffic light.

The driver looked familiar.

After a second, Allen realized it was Tom Cruise.

Tom challenged him to a race.

Allen accepted immediately.

Both men revved their engines while waiting for the light.

When the signal finally changed, they raced down Van Ness Street at incredible speed.

At first, Tom was winning easily.

His Ferrari moved like lightning through the city.

But suddenly, police lights appeared behind him.

The police quickly pulled him over.

Allen rode past laughing and shouted, "Better luck next time!"

Even though Allen didn't technically beat the Ferrari with speed, he still became the winner.
""",

            'future': """
Tomorrow evening, Allen will probably ride through San Francisco again on his motorcycle.

As he waits at a traffic light on Van Ness Street, another sports car may appear beside him.

If Tom Cruise appears again, he will probably challenge Allen to another race.

Allen will most likely accept the challenge immediately.

The engines will roar loudly while people watch from the sidewalks.

When the light turns green, both vehicles will shoot forward through the city.

Tom's Ferrari will probably move ahead first.

However, police officers may notice the dangerous race.

If police lights appear again, Tom may get pulled over once more.

Allen will likely laugh and enjoy another unexpected victory.
""",

            'native': """
Allen was just enjoying a normal ride through San Francisco when things suddenly got crazy.

He stopped at a red light on Van Ness and noticed a bright red Ferrari pulling up beside him.

The driver looked way too cool to be normal.

Dark sunglasses. Perfect smile. Total movie-star energy.

Allen looked closer and nearly lost his mind.

It was Tom Cruise.

Tom leaned over and casually said, "Let's race when the light turns green."

Allen laughed. "You're on."

Both engines started roaring while people nearby watched the scene like it was a movie.

Then the light changed.

Boom.

Both vehicles took off instantly.

The Ferrari jumped ahead fast.

Allen honestly thought he had no chance.

But seconds later, police sirens exploded behind Tom.

Blue and red lights flashed everywhere.

Tom had to pull over immediately.

Meanwhile, Allen rode past laughing like an idiot.

"Better luck next time!" he yelled before disappearing into traffic.
""",

            'dialog': """
"Dude, you won't believe what happened yesterday."

"What happened?"

"I raced Tom Cruise."

"No way."

"I swear."

"Where?"

"On Van Ness Street in San Francisco."

"You're kidding."

"A red Ferrari pulled up next to me."

"And it was actually Tom Cruise?"

"Yep."

"What did he say?"

"He challenged me to a race."

"And you said yes?"

"Of course."

"Haha. Then what happened?"

"We took off the second the light turned green."

"Who was winning?"

"He was."

"So how did you win?"

"Police lights."

"No way!"

"Yep. They pulled him over."

"That's legendary."
"""
        }

        for vtype, content in versions.items():

            StoryVersion.objects.get_or_create(
                story=story,
                version_type=vtype,
                defaults={
                    'content': content
                }
            )

        UserStoryProgress.objects.get_or_create(
            user=user,
            story=story,
            defaults={
                'completed': False,
                'read_count': 0,
            }
        )

        return story

    # ---------------------------------------------------
    # VOCABULARY
    # ---------------------------------------------------

    def create_vocabulary(self):

        english = Language.objects.get(code='en')
        turkish = Language.objects.get(code='tr')

        words_data = [

            {
                'word': 'race',
                'definition': 'a speed competition',
                'part_of_speech': 'noun',
                'difficulty_level': 'A2',
                'translation': 'yarış',
                'synonyms': ['competition', 'contest'],
            },

            {
                'word': 'motorcycle',
                'definition': 'a two-wheeled vehicle',
                'part_of_speech': 'noun',
                'difficulty_level': 'A1',
                'translation': 'motosiklet',
                'synonyms': ['bike'],
            },

            {
                'word': 'rev',
                'definition': 'to increase engine speed',
                'part_of_speech': 'verb',
                'difficulty_level': 'B1',
                'translation': 'gaza basmak',
                'synonyms': ['accelerate'],
            },

            {
                'word': 'smirk',
                'definition': 'a confident smile',
                'part_of_speech': 'verb',
                'difficulty_level': 'B1',
                'translation': 'sırıtmak',
                'synonyms': ['grin'],
            },

            {
                'word': 'speed',
                'definition': 'to move quickly',
                'part_of_speech': 'verb',
                'difficulty_level': 'A2',
                'translation': 'hız yapmak',
                'synonyms': ['zoom', 'rush'],
            },

            {
                'word': 'sirens',
                'definition': 'warning sounds from emergency vehicles',
                'part_of_speech': 'noun',
                'difficulty_level': 'A2',
                'translation': 'sirenler',
                'synonyms': ['alarms'],
            },

            {
                'word': 'challenge',
                'definition': 'an invitation to compete',
                'part_of_speech': 'noun',
                'difficulty_level': 'A2',
                'translation': 'meydan okuma',
                'synonyms': ['dare'],
            },

            {
                'word': 'victory',
                'definition': 'success in a competition',
                'part_of_speech': 'noun',
                'difficulty_level': 'B1',
                'translation': 'zafer',
                'synonyms': ['triumph', 'win'],
            },
        ]

        created_words = []

        for data in words_data:

            word, created = Word.objects.get_or_create(
                language=english,
                word=data['word'],
                defaults={
                    'part_of_speech': data['part_of_speech'],
                    'definition': data['definition'],
                    'difficulty_level': data['difficulty_level'],
                }
            )

            WordTranslation.objects.get_or_create(
                word=word,
                target_language=turkish,
                defaults={
                    'translation': data['translation']
                }
            )

            for syn in data['synonyms']:

                syn_word, _ = Word.objects.get_or_create(
                    language=english,
                    word=syn,
                    defaults={
                        'part_of_speech': data['part_of_speech'],
                        'definition': f'Similar to {data["word"]}',
                        'difficulty_level': data['difficulty_level'],
                    }
                )

                WordSynonym.objects.get_or_create(
                    word=word,
                    synonym=syn_word
                )

            created_words.append(word)

        return {w.word: w for w in created_words}

    # ---------------------------------------------------
    # STORY WORDS
    # ---------------------------------------------------

    def link_words_to_story(self, story, vocab_map):

        story_words = [

            ('race', 1, 'Tom Cruise challenged Allen to a race.'),

            ('motorcycle', 2, 'Allen rode his motorcycle through San Francisco.'),

            ('rev', 3, 'Both men revved their engines loudly.'),

            ('smirk', 4, 'Tom smirked confidently before the race.'),

            ('speed', 5, 'Allen sped past Tom after the police arrived.'),

            ('sirens', 6, 'Police sirens suddenly appeared behind Tom.'),

            ('challenge', 7, 'Allen accepted the challenge immediately.'),

            ('victory', 8, 'Allen celebrated his unexpected victory.'),
        ]

        for word_text, order, example in story_words:

            word = vocab_map.get(word_text)

            if word:

                StoryWord.objects.get_or_create(
                    story=story,
                    word=word,
                    defaults={
                        'example_sentence': example,
                        'order': order,
                    }
                )

    # ---------------------------------------------------
    # QUIZ
    # ---------------------------------------------------

    def create_quiz(self, story):

        quiz, _ = Quiz.objects.get_or_create(
            story=story,
            version_type='original',
            defaults={
                'title': 'Allen vs Tom Cruise Quiz',
                'is_premium': False,
            }
        )

        questions = [

            {
                'text': 'Where was Allen riding his motorcycle?',
                'correct': 'San Francisco',
                'type': 'fill_blank',
                'order': 1,
            },

            {
                'text': 'What kind of car did Tom Cruise drive?',
                'correct': 'Ferrari',
                'type': 'fill_blank',
                'order': 2,
            },

            {
                'text': 'Who challenged Allen to a race?',
                'correct': 'Tom Cruise',
                'type': 'fill_blank',
                'order': 3,
            },

            {
                'text': 'What color was the Ferrari?',
                'correct': 'Red',
                'type': 'fill_blank',
                'order': 4,
            },

            {
                'text': 'Did police officers stop Allen?',
                'correct': 'No',
                'type': 'true_false',
                'order': 5,
            },

            {
                'text': 'Who won the race?',
                'correct': 'Allen',
                'type': 'fill_blank',
                'order': 6,
            },
        ]

        for q in questions:

            QuizQuestion.objects.get_or_create(
                quiz=quiz,
                order=q['order'],
                defaults={
                    'question_text': q['text'],
                    'correct_answer': q['correct'],
                    'question_type': q['type'],
                    'options': [],
                    'hint_text': '',
                    'explanation': '',
                }
            )

    # ---------------------------------------------------
    # PROGRESS
    # ---------------------------------------------------

    def create_progress(self, user, story):

        UserProgress.objects.get_or_create(
            user=user,
            defaults={
                'total_xp': 250,
                'total_stories_read': 1,
                'total_words_learned': 8,
                'total_quiz_attempts': 1,
                'current_streak_days': 3,
                'longest_streak_days': 5,
                'last_active_date': timezone.now().date(),
            }
        )

        for i in range(7):

            DailyActivity.objects.get_or_create(
                user=user,
                date=timezone.now().date() - timedelta(days=i),
                defaults={
                    'stories_read': random.randint(0, 2),
                    'words_reviewed': random.randint(5, 15),
                    'quizzes_taken': random.randint(0, 1),
                    'xp_earned': random.randint(20, 80),
                    'minutes_spent': random.randint(10, 30),
                }
            )