import random
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from apps.languages.models import Language, UserTargetLanguage
from apps.stories.models import Story, StoryVersion, StoryTag, UserStoryProgress, UserNote
from apps.vocabulary.models import Word, WordTranslation, WordSynonym, StoryWord
from apps.notebook.models import UserWord, UserWordCollection
from apps.quizzes.models import Quiz, QuizQuestion, UserQuizAttempt
from apps.progress.models import UserProgress, DailyActivity, Achievement, UserAchievement
from apps.accounts.models import UserSettings

User = get_user_model()

class Command(BaseCommand):
    help = 'Seed the database with comprehensive sample data for Storavel'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🌱 Seeding database...'))

        # 1. Languages
        self.create_languages()

        # 2. Users
        demo_user = self.create_users()

        # 3. Story Tags
        tags = self.create_tags()

        # 4. Stories & Versions
        sara_story = self.create_sara_story(demo_user, tags)
        emma_story = self.create_emma_story(demo_user, tags)

        # 5. Vocabulary (Words, Translations, Synonyms)
        vocab_words = self.create_vocabulary()

        # 6. StoryWord links (which words appear in which stories)
        self.link_words_to_stories(sara_story, emma_story, vocab_words)

        # 7. Quizzes & Questions
        self.create_quizzes(sara_story, emma_story)

        # 8. User Notebook (saved words, collections, reviews)
        self.create_notebook_data(demo_user, vocab_words)

        # 9. User Progress & Achievements
        self.create_progress_data(demo_user)

        self.stdout.write(self.style.SUCCESS('✅ Seeding completed!'))

    def create_languages(self):
        languages = [
            {'code': 'en', 'name': 'English', 'native_name': 'English', 'flag_emoji': '🇺🇸', 'script': 'latin', 'rtl': False, 'has_romanization': False, 'is_active': True, 'order': 1},
            {'code': 'tr', 'name': 'Turkish', 'native_name': 'Türkçe', 'flag_emoji': '🇹🇷', 'script': 'latin', 'rtl': False, 'has_romanization': False, 'is_active': True, 'order': 2},
            {'code': 'es', 'name': 'Spanish', 'native_name': 'Español', 'flag_emoji': '🇪🇸', 'script': 'latin', 'rtl': False, 'has_romanization': False, 'is_active': True, 'order': 3},
            {'code': 'fr', 'name': 'French', 'native_name': 'Français', 'flag_emoji': '🇫🇷', 'script': 'latin', 'rtl': False, 'has_romanization': False, 'is_active': True, 'order': 4},
        ]
        for lang_data in languages:
            lang, created = Language.objects.get_or_create(code=lang_data['code'], defaults=lang_data)
            self.stdout.write(f'  {"✅" if created else "⚠️"} Language: {lang.name}')

    def create_users(self):
        # Demo user
        demo, created = User.objects.get_or_create(
            email='demo@storavel.com',
            defaults={
                'username': 'demo_user',
                'display_name': 'Demo Learner',
                'is_premium': False,
                'is_active': True,
            }
        )
        if created:
            demo.set_password('demo123')
            demo.save()
            UserSettings.objects.get_or_create(user=demo)
            self.stdout.write('  ✅ Demo user created (demo@storavel.com / demo123)')
        else:
            self.stdout.write('  ⚠️ Demo user already exists')

        # Add target languages for demo user
        english = Language.objects.get(code='en')
        spanish = Language.objects.get(code='es')
        UserTargetLanguage.objects.get_or_create(user=demo, language=english, defaults={'is_primary': True})
        UserTargetLanguage.objects.get_or_create(user=demo, language=spanish, defaults={'is_primary': False})
        return demo

    def create_tags(self):
        tag_names = ['cat', 'pet', 'morning', 'routine', 'family', 'shopping', 'humor', 'daily', 'coffee']
        tags = []
        for name in tag_names:
            tag, _ = StoryTag.objects.get_or_create(name=name, defaults={'slug': slugify(name)})
            tags.append(tag)
        self.stdout.write(f'  ✅ {len(tags)} story tags created')
        return tags

    def create_sara_story(self, user, tags):
        english = Language.objects.get(code='en')
        story, created = Story.objects.get_or_create(
            slug='saras-giant-cat-adventure',
            defaults={
                'language': english,
                'title': "Sara's Giant Cat Adventure",
                'level_min': 'A1',
                'level_max': 'B1',
                'story_type': 'narrative',
                'estimated_read_minutes': 12,
                'is_premium': False,
                'is_published': True,
                'order': 1,
            }
        )
        if created:
            story.tags.set(tags[:4])
            self.stdout.write('  ✅ Story: Sara\'s Giant Cat Adventure')

        versions = {
            'original': """Sara Smith lives in San Francisco and recently went shopping for cat food.

Sara is 30 years old and lives at 3037 Market Street. She has lived there since 1990. She is married to a man named John, and they have been married for seven years.

Sara and John have two children and one enormous cat. Their son, Bob, is five years old, and their daughter, Nancy, is three years old. Their cat, Bubba, is two years old and extremely large. Bubba weighs 258 pounds, or about 117 kilograms.

At 9 a.m., Sara got into her car and drove to a pet store to buy cat food. She purchased 68 bags of cat food for $10 each plus tax. Normally, each bag costs $15, so Sara felt happy because she got a very good deal.

The total price was $680. She paid with her credit card.

On the way home, Sara stopped at a convenience store to buy milk because Bubba loves drinking milk. The milk cost $3 per gallon, and Sara bought 30 gallons.

She paid with a $100 bill and received $10 in change.

Sara finally arrived home at 11 a.m. Bubba was already waiting near the door because he was extremely hungry.""",
            'present': """Sara Smith lives in San Francisco with her husband, John, their two children, and their gigantic cat named Bubba. Every day in Sara's house feels a little unusual because Bubba is not an ordinary cat. He is massive, heavy, and constantly hungry.

This morning, Sara wakes up early because she realizes they are almost out of cat food. Bubba is already walking around the kitchen and meowing loudly for breakfast.

Sara quickly gets ready, grabs her car keys, and heads outside. The morning air in San Francisco feels cool and fresh as she drives through busy streets toward the pet store.

At exactly 9 a.m., she arrives at the store and immediately starts loading bags of cat food into her shopping cart. Other customers stare at her in surprise because she keeps adding more and more bags.

One employee finally asks, "How many cats do you have?"

Sara laughs and explains that she only has one cat — but he is absolutely enormous.

She buys 68 bags of cat food because the store is having a huge discount. Instead of paying the regular price of $15 per bag, she only pays $10 each. Sara feels satisfied because she knows she is saving a lot of money.

After paying by credit card, she carefully carries the heavy bags to her car.

On the drive home, she suddenly remembers that Bubba also loves milk. She stops at a convenience store and buys 30 gallons.

The cashier looks shocked.

"Are you feeding a cat or a tiger?" he jokes.

Sara smiles and says, "Sometimes I wonder the same thing."

By the time Sara arrives home at 11 a.m., she feels tired from all the shopping. But the moment she parks the car, Bubba appears at the front door.

The giant cat looks impatient and hungry.

And judging by the sound of his loud meow, Bubba cannot wait for lunch.""",
            'past': """Last Saturday, Sara Smith had a very unusual shopping trip.

Sara, who lived in San Francisco with her husband John, their two children, and their enormous cat Bubba, realized early in the morning that they were running out of cat food.

Bubba was not a normal cat. At only two years old, he already weighed 258 pounds. Feeding him was almost like feeding a wild animal.

At around 9 a.m., Sara got into her car and drove to the pet store. She expected to buy only a few bags at first, but once she saw the discount, she decided to buy a huge amount.

Each bag normally cost $15, but the store was selling them for only $10. Sara immediately realized it was a fantastic deal.

She filled her cart with 68 bags of cat food while several customers watched in disbelief.

One woman even asked if Sara owned a zoo. Sara laughed and explained that all the food was for one giant cat named Bubba.

After paying $680 by credit card, she carefully packed everything into her car.

While driving home, Sara remembered that Bubba also loved milk, so she stopped at a convenience store. She bought 30 gallons.

The cashier looked completely confused when he saw the amount of milk. When Sara handed him $100 and received $10 in change, he jokingly asked if she had a baby elephant at home.

By the time Sara finally returned home at 11 a.m., she felt exhausted. But Bubba was already waiting at the door. The giant cat looked extremely hungry and immediately started meowing loudly.

At that moment, Sara realized something funny: No matter how much food she bought, Bubba always seemed ready for more.""",
            'future': """Tomorrow morning, Sara Smith will wake up early because Bubba's food supply will almost be empty.

Living with such a gigantic cat will continue to be expensive and exhausting, but Sara will still care deeply for him.

At around 9 a.m., she will get into her car and drive to the pet store once again. Since Bubba eats enormous amounts of food, Sara will probably buy dozens of bags.

Fortunately, the store will be offering another discount. Instead of paying the regular price, she will save money by buying in bulk.

Other customers will probably stare at her shopping cart in confusion.

Someone may even ask, "How many cats do you own?"

Sara will laugh and explain that she only has one cat - a giant cat named Bubba.

After paying hundreds of dollars for cat food, she will stop at a convenience store to buy milk because Bubba absolutely loves it.

The cashier will likely look surprised when Sara places 30 gallons of milk on the counter.

After finishing her shopping, Sara will drive home feeling tired but satisfied.

When she arrives home around 11 a.m., Bubba will already be waiting near the front door.

The huge cat will probably start meowing immediately because he will still be hungry.

Sara will smile, shake her head, and prepare another enormous meal for her giant pet.""",
            'native': """Sara's life would probably seem completely normal - until people met her cat.

She lived in San Francisco with her husband John, their two kids, and Bubba, a cat so ridiculously huge that people sometimes thought she was joking when she talked about him.

But she wasn't joking.

Bubba weighed 258 pounds.

And feeding him was basically a full-time job.

That morning, Sara realized they were almost out of cat food, which was a serious problem because Bubba got angry when he was hungry.

So around 9 a.m., she jumped into her car and headed to the pet store.

Once she got there, she noticed they were running a huge sale. Cat food bags that normally cost $15 were selling for only $10.

Naturally, she went a little crazy.

She loaded 68 bags into her car while people around her stared like she was preparing for the apocalypse.

One guy finally asked, "How many cats do you have?"

Sara smiled and said, "Just one."

The guy looked confused. Very confused.

After paying $680 by credit card and somehow fitting everything into her car, Sara started driving home.

Then she remembered the milk.

Bubba loved milk. A lot.

So she stopped at a convenience store and bought 30 gallons.

The cashier blinked twice before asking, "Ma'am... are you raising a tiger?"

At that point, Sara honestly wasn't sure anymore.

By the time she got home at 11 a.m., she was exhausted.

But Bubba was already sitting by the front door waiting for her.

The moment he saw the food, he let out the loudest meow imaginable.

And somehow, despite buying enough food for what looked like a small zoo, Sara had a feeling Bubba would still want dinner later.""",
        }

        for vtype, content in versions.items():
            obj, created = StoryVersion.objects.get_or_create(story=story, version_type=vtype, defaults={'content': content})
            if created:
                self.stdout.write(f'    ✅ Version: {vtype}')

        # Add progress for demo user
        UserStoryProgress.objects.get_or_create(user=user, story=story, defaults={'completed': False, 'read_count': 0})
        return story

    def create_emma_story(self, user, tags):
        english = Language.objects.get(code='en')
        story, created = Story.objects.get_or_create(
            slug='emmas-morning-routine',
            defaults={
                'language': english,
                'title': "Emma's Morning Routine",
                'level_min': 'A1',
                'level_max': 'A2',
                'story_type': 'narrative',
                'estimated_read_minutes': 8,
                'is_premium': False,
                'is_published': True,
                'order': 2,
            }
        )
        if created:
            story.tags.set([t for t in tags if t.name in ['morning', 'routine', 'daily', 'coffee']])
            self.stdout.write('  ✅ Story: Emma\'s Morning Routine')

        versions = {
            'original': """Every morning, Emma gets up early and goes to the kitchen. She turns on the coffee machine and waits by the window. Outside, birds are singing and the street is still quiet.

When the coffee is ready, she pours it into her favourite mug. This calm moment helps her start the day slowly.

Before leaving for work, Emma writes herself a short note. It is a small but useful habit.""",
            'present': """Every morning, Emma wakes up before the rest of the city. The house is silent, and soft morning light slowly enters through the kitchen window.

She walks quietly to the kitchen, still feeling sleepy, and turns on the coffee machine. While the coffee is brewing, Emma stands near the window and watches the peaceful street outside.

Birds are singing in the trees, and only a few cars pass by. The world still feels calm and unhurried.

Soon, the smell of fresh coffee fills the kitchen. Emma smiles softly as she pours the hot coffee into her favourite mug.

Holding the warm mug in her hands helps her relax before the busy day begins.

Before leaving for work, Emma sits at the table and writes herself a short note. Sometimes it is a reminder. Sometimes it is an encouraging sentence.

This small daily habit helps her feel organized, calm, and focused.""",
            'past': """Yesterday morning, Emma woke up early as usual and quietly walked to the kitchen.

The house was still silent, and the street outside looked peaceful. She turned on the coffee machine and waited by the window while the coffee brewed.

Birds were singing outside, and the cool morning air made everything feel calm.

When the coffee was finally ready, Emma poured it into her favourite mug and slowly took the first sip.

That quiet moment helped her clear her mind before work.

Before leaving the house, Emma wrote herself a short note and placed it inside her bag.

The note simply said: "Stay calm and do your best."

Even though it was a very small action, it made her feel more positive for the rest of the day.""",
            'future': """Tomorrow morning, Emma will wake up early once again before the city becomes noisy.

She will walk into the kitchen, turn on the coffee machine, and stand quietly by the window while waiting.

Outside, birds will be singing, and the streets will still feel calm and empty.

When the coffee is ready, Emma will pour it into her favourite mug and enjoy a peaceful moment before work.

She will probably think about the tasks waiting for her later in the day, but for a few minutes she will simply enjoy the silence.

Before leaving for work, Emma will write herself another short note.

Maybe it will contain a motivational message or a simple reminder.

No matter what she writes, this small habit will continue helping her start each day with a clear and peaceful mind.""",
            'native': """Emma's mornings are simple, but that's exactly why she loves them.

Every day, she wakes up early before the city fully comes alive. The apartment is quiet, the streets outside are still calm, and for a few minutes it feels like the world is moving in slow motion.

The first thing she does is head to the kitchen and turn on the coffee machine.

Then she just waits by the window.

No phone. No emails. No noise.

Just the sound of birds outside and the smell of fresh coffee filling the room.

When the coffee is ready, she pours it into her favourite mug - the old blue one she's had for years.

That small moment has become part of her routine.

It helps her wake up slowly and mentally prepare for the day ahead.

Before leaving for work, Emma always writes herself a quick note.

Sometimes it's a reminder. Sometimes it's something encouraging like "You've got this."

It might seem like a tiny habit, but somehow it makes her mornings feel more organized and a little more peaceful.""",
            'dialog': '''"Wow, you're always up so early."

"Yeah, I actually like mornings."

"Seriously? I hate waking up early."

"Haha, I used to feel the same way."

"So what do you do every morning?"

"Nothing complicated. I wake up, go to the kitchen, and make coffee."

"That sounds relaxing."

"It really is. While the coffee is brewing, I usually stand by the window for a few minutes."

"And just... stare outside?"

"Pretty much."

"Haha. Why?"

"I don't know. It helps me wake up slowly. The street is quiet, birds are singing... it's peaceful."

"That actually sounds nice."

"Yeah, it's kind of my calm moment before work."

"And then?"

"I pour the coffee into my favourite mug and just enjoy the silence."

"You really romanticize mornings."

"Haha, maybe."

"Do you do anything else before work?"

"Yeah, I write myself a short note."

"A note?"

"Yeah. Usually reminders or motivational stuff."

"Like what?"

"Things like 'Stay focused' or 'Don't stress too much.'"

"That's actually a pretty good habit."

"It helps more than you'd think."''',
        }

        for vtype, content in versions.items():
            obj, created = StoryVersion.objects.get_or_create(story=story, version_type=vtype, defaults={'content': content})
            if created:
                self.stdout.write(f'    ✅ Version: {vtype}')

        UserStoryProgress.objects.get_or_create(user=user, story=story, defaults={'completed': False, 'read_count': 0})
        return story

    def create_vocabulary(self):
        english = Language.objects.get(code='en')
        spanish = Language.objects.get(code='es')
        turkish = Language.objects.get(code='tr')
        french = Language.objects.get(code='fr')

        # Define words with all fields
        words_data = [
            {
                'word': 'enormous',
                'part_of_speech': 'adjective',
                'definition': 'very large in size, quantity, or extent',
                'romanization': '',
                'audio_url': '',
                'difficulty_level': 'A2',
                'translations': {'es': 'enorme', 'tr': 'devasa', 'fr': 'énorme'},
                'synonyms': ['huge', 'gigantic', 'massive']
            },
            {
                'word': 'gigantic',
                'part_of_speech': 'adjective',
                'definition': 'extremely large, enormous',
                'romanization': '',
                'audio_url': '',
                'difficulty_level': 'B1',
                'translations': {'es': 'gigantesco', 'tr': 'dev gibi', 'fr': 'gigantesque'},
                'synonyms': ['enormous', 'colossal', 'immense']
            },
            {
                'word': 'purchase',
                'part_of_speech': 'verb',
                'definition': 'to buy something',
                'romanization': '',
                'audio_url': '',
                'difficulty_level': 'B1',
                'translations': {'es': 'comprar', 'tr': 'satın almak', 'fr': 'acheter'},
                'synonyms': ['buy', 'acquire', 'obtain']
            },
            {
                'word': 'starving',
                'part_of_speech': 'adjective',
                'definition': 'extremely hungry',
                'romanization': '',
                'audio_url': '',
                'difficulty_level': 'A2',
                'translations': {'es': 'hambriento', 'tr': 'açlıktan ölmek', 'fr': 'affamé'},
                'synonyms': ['famished', 'ravenous', 'hungry']
            },
            {
                'word': 'discount',
                'part_of_speech': 'noun',
                'definition': 'a reduction in price',
                'romanization': '',
                'audio_url': '',
                'difficulty_level': 'A2',
                'translations': {'es': 'descuento', 'tr': 'indirim', 'fr': 'réduction'},
                'synonyms': ['reduction', 'sale', 'markdown']
            },
            {
                'word': 'exhausted',
                'part_of_speech': 'adjective',
                'definition': 'very tired, drained of energy',
                'romanization': '',
                'audio_url': '',
                'difficulty_level': 'B1',
                'translations': {'es': 'agotado', 'tr': 'bitkin', 'fr': 'épuisé'},
                'synonyms': ['worn out', 'fatigued', 'drained']
            },
            {
                'word': 'peaceful',
                'part_of_speech': 'adjective',
                'definition': 'calm, quiet, and free from disturbance',
                'romanization': '',
                'audio_url': '',
                'difficulty_level': 'A2',
                'translations': {'es': 'pacífico', 'tr': 'huzurlu', 'fr': 'paisible'},
                'synonyms': ['calm', 'tranquil', 'serene']
            },
            {
                'word': 'routine',
                'part_of_speech': 'noun',
                'definition': 'a regular sequence of actions or habits',
                'romanization': '',
                'audio_url': '',
                'difficulty_level': 'A2',
                'translations': {'es': 'rutina', 'tr': 'rutin', 'fr': 'routine'},
                'synonyms': ['habit', 'pattern', 'procedure']
            },
            {
                'word': 'brew',
                'part_of_speech': 'verb',
                'definition': 'to make coffee or tea by steeping in hot water',
                'romanization': '',
                'audio_url': '',
                'difficulty_level': 'B1',
                'translations': {'es': 'preparar (café/té)', 'tr': 'demlemek', 'fr': 'infuser'},
                'synonyms': ['steep', 'infuse', 'prepare']
            },
            {
                'word': 'habit',
                'part_of_speech': 'noun',
                'definition': 'a regular tendency or practice',
                'romanization': '',
                'audio_url': '',
                'difficulty_level': 'A2',
                'translations': {'es': 'hábito', 'tr': 'alışkanlık', 'fr': 'habitude'},
                'synonyms': ['custom', 'routine', 'practice']
            },
            {
                'word': 'bargain',
                'part_of_speech': 'noun',
                'definition': 'a good deal or advantageous purchase',
                'romanization': '',
                'audio_url': '',
                'difficulty_level': 'B1',
                'translations': {'es': 'ganga', 'tr': 'kelepir', 'fr': 'bonne affaire'},
                'synonyms': ['deal', 'discount', 'steal']
            },
            {
                'word': 'stare',
                'part_of_speech': 'verb',
                'definition': 'to look fixedly at something for a long time',
                'romanization': '',
                'audio_url': '',
                'difficulty_level': 'A2',
                'translations': {'es': 'mirar fijamente', 'tr': 'dik dik bakmak', 'fr': 'dévisager'},
                'synonyms': ['gaze', 'glare', 'peer']
            },
        ]

        created_words = []
        for wdata in words_data:
            word, created = Word.objects.get_or_create(
                language=english,
                word=wdata['word'],
                defaults={
                    'part_of_speech': wdata['part_of_speech'],
                    'definition': wdata['definition'],
                    'romanization': wdata['romanization'],
                    'audio_url': wdata['audio_url'],
                    'difficulty_level': wdata['difficulty_level'],
                }
            )
            if created:
                self.stdout.write(f'    ✅ Word: {word.word}')

                # Add translations
                for target_code, translation in wdata['translations'].items():
                    target_lang = Language.objects.get(code=target_code)
                    WordTranslation.objects.get_or_create(
                        word=word,
                        target_language=target_lang,
                        defaults={'translation': translation}
                    )
                # Add synonyms (self-referential)
                for syn_word in wdata['synonyms']:
                    # Find or create synonym word (if not already existing as a separate Word)
                    syn_obj, _ = Word.objects.get_or_create(
                        language=english,
                        word=syn_word,
                        defaults={
                            'part_of_speech': word.part_of_speech,
                            'definition': f"Similar to {word.word}",
                            'difficulty_level': word.difficulty_level
                        }
                    )
                    WordSynonym.objects.get_or_create(word=word, synonym=syn_obj)
            created_words.append(word)
        self.stdout.write(f'  ✅ Vocabulary: {len(created_words)} words with translations and synonyms')
        return {w.word: w for w in created_words}

    def link_words_to_stories(self, sara_story, emma_story, vocab_map):
        # Sara story words with example sentences and order
        sara_words = [
            ('enormous', 1, "Sara has an enormous cat named Bubba."),
            ('gigantic', 2, "Bubba is a gigantic cat."),
            ('purchase', 3, "She purchased 68 bags of cat food."),
            ('starving', 4, "Bubba was starving when Sara arrived home."),
            ('discount', 5, "The store offered a discount on cat food."),
            ('bargain', 6, "Sara got a bargain because each bag was only $10."),
            ('exhausted', 7, "Sara felt exhausted after carrying all the bags."),
            ('stare', 8, "Other customers stared at her shopping cart."),
        ]
        for word_text, order, example in sara_words:
            word = vocab_map.get(word_text)
            if word:
                StoryWord.objects.get_or_create(
                    story=sara_story,
                    word=word,
                    defaults={'example_sentence': example, 'order': order}
                )

        # Emma story words
        emma_words = [
            ('peaceful', 1, "Emma enjoys peaceful mornings by the window."),
            ('routine', 2, "Her morning routine helps her feel organized."),
            ('brew', 3, "She watches the coffee brew while standing by the window."),
            ('habit', 4, "Writing a short note is a useful habit."),
        ]
        for word_text, order, example in emma_words:
            word = vocab_map.get(word_text)
            if word:
                StoryWord.objects.get_or_create(
                    story=emma_story,
                    word=word,
                    defaults={'example_sentence': example, 'order': order}
                )
        self.stdout.write('  ✅ Linked vocabulary to stories')

    def create_quizzes(self, sara_story, emma_story):
        # Sara quiz
        quiz_sara, _ = Quiz.objects.get_or_create(
            story=sara_story,
            version_type='original',
            defaults={'title': 'Sara\'s Cat Adventure Quiz', 'is_premium': False}
        )
        questions_sara = [
            {'text': 'Where does Sara live?', 'correct': 'San Francisco', 'type': 'fill_blank', 'order': 1},
            {'text': 'What is the name of Sara\'s cat?', 'correct': 'Bubba', 'type': 'fill_blank', 'order': 2},
            {'text': 'How much does Bubba weigh?', 'correct': '258 pounds', 'type': 'fill_blank', 'order': 3},
            {'text': 'How many bags of cat food did Sara buy?', 'correct': '68', 'type': 'fill_blank', 'order': 4},
            {'text': 'Is Bubba a small cat?', 'correct': 'No', 'type': 'true_false', 'order': 5},
            {'text': 'Why did Sara stop at the convenience store?', 'correct': 'to buy milk', 'type': 'fill_blank', 'order': 6},
        ]
        for q in questions_sara:
            QuizQuestion.objects.get_or_create(
                quiz=quiz_sara,
                order=q['order'],
                defaults={
                    'question_text': q['text'],
                    'correct_answer': q['correct'],
                    'question_type': q['type'],
                    'options': [],
                    'hint_text': '',
                    'explanation': ''
                }
            )
        self.stdout.write(f'  ✅ Quiz for Sara: {quiz_sara.questions.count()} questions')

        # Emma quiz
        quiz_emma, _ = Quiz.objects.get_or_create(
            story=emma_story,
            version_type='original',
            defaults={'title': 'Emma\'s Morning Routine Quiz', 'is_premium': False}
        )
        questions_emma = [
            {'text': 'What does Emma drink in the morning?', 'correct': 'coffee', 'type': 'fill_blank', 'order': 1},
            {'text': 'Where does Emma stand while waiting for coffee?', 'correct': 'by the window', 'type': 'fill_blank', 'order': 2},
            {'text': 'What does Emma write before leaving for work?', 'correct': 'a note', 'type': 'fill_blank', 'order': 3},
            {'text': 'Does Emma wake up early or late?', 'correct': 'early', 'type': 'fill_blank', 'order': 4},
            {'text': 'Is Emma\'s morning routine stressful?', 'correct': 'No', 'type': 'true_false', 'order': 5},
        ]
        for q in questions_emma:
            QuizQuestion.objects.get_or_create(
                quiz=quiz_emma,
                order=q['order'],
                defaults={
                    'question_text': q['text'],
                    'correct_answer': q['correct'],
                    'question_type': q['type'],
                    'options': [],
                    'hint_text': '',
                    'explanation': ''
                }
            )
        self.stdout.write(f'  ✅ Quiz for Emma: {quiz_emma.questions.count()} questions')

    def create_notebook_data(self, user, vocab_map):
        # Save some words to user's notebook
        words_to_save = ['enormous', 'peaceful', 'routine', 'habit', 'bargain']
        for word_text in words_to_save:
            word = vocab_map.get(word_text)
            if word:
                user_word, created = UserWord.objects.get_or_create(
                    user=user,
                    language=word.language,
                    word=word.word,
                    defaults={
                        'part_of_speech': word.part_of_speech,
                        'definition': word.definition,
                        'translation': f'Example translation for {word.word}',
                        'status': 'learning',
                        'times_reviewed': random.randint(0, 3),
                        'ease_factor': 2.5,
                        'next_review_at': timezone.now() + timedelta(days=random.randint(1, 10)),
                        'source_word': word,
                    }
                )
                if created:
                    self.stdout.write(f'    ✅ Saved to notebook: {word.word}')

        # Create a collection
        collection, _ = UserWordCollection.objects.get_or_create(
            user=user,
            name='Favorites',
            defaults={'description': 'My favorite words', 'color': '#4A7DC8'}
        )
        # Add some words to collection
        for word_text in ['enormous', 'peaceful']:
            word_obj = Word.objects.filter(word=word_text).first()
            if word_obj:
                user_word = UserWord.objects.filter(user=user, word=word_obj.word).first()
                if user_word:
                    collection.words.add(user_word)
        self.stdout.write('  ✅ Notebook collections created')

    def create_progress_data(self, user):
        progress, _ = UserProgress.objects.get_or_create(
            user=user,
            defaults={
                'total_xp': 450,
                'total_stories_read': 3,
                'total_words_learned': 8,
                'total_quiz_attempts': 2,
                'current_streak_days': 5,
                'longest_streak_days': 12,
                'last_active_date': timezone.now().date(),
            }
        )
        # Daily activities for last 7 days
        for i in range(7):
            day = timezone.now().date() - timedelta(days=i)
            DailyActivity.objects.get_or_create(
                user=user,
                date=day,
                defaults={
                    'stories_read': random.randint(0, 2),
                    'words_reviewed': random.randint(5, 20),
                    'quizzes_taken': random.randint(0, 1),
                    'xp_earned': random.randint(20, 100),
                    'minutes_spent': random.randint(5, 30),
                }
            )
        # Achievements
        achievements_data = [
            {'code': 'first_story', 'title': 'First Story', 'description': 'Read your first story', 'xp_reward': 50, 'condition_type': 'stories_read', 'condition_value': 1},
            {'code': 'word_collector', 'title': 'Word Collector', 'description': 'Save 10 words to notebook', 'xp_reward': 100, 'condition_type': 'words_saved', 'condition_value': 10},
            {'code': 'quiz_master', 'title': 'Quiz Master', 'description': 'Score 100% on a quiz', 'xp_reward': 150, 'condition_type': 'perfect_quiz', 'condition_value': 1},
        ]
        for ach_data in achievements_data:
            ach, _ = Achievement.objects.get_or_create(code=ach_data['code'], defaults=ach_data)
            # Grant some achievements to user
            if ach.code == 'first_story':
                UserAchievement.objects.get_or_create(user=user, achievement=ach, defaults={'earned_at': timezone.now() - timedelta(days=10)})
        self.stdout.write('  ✅ Progress data created')
