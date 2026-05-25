import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.text import slugify

from apps.languages.models import Language
from apps.stories.models import Story, StoryVersion, StoryTag
from apps.vocabulary.models import Word, WordTranslation, WordSynonym
from apps.quizzes.models import Quiz, QuizQuestion

User = get_user_model()


class Command(BaseCommand):
    help = 'Create comprehensive English learning story packages with AJ Hoge / TPRS style educational content.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🌱 Starting comprehensive story seed process...'))

        self.create_languages()
        self.create_tags()
        self.create_story_packages()
        self.create_global_vocabulary()

        self.stdout.write(self.style.SUCCESS('✅ Comprehensive educational story seed completed successfully!'))

    # --------------------------------------------------
    # LANGUAGES
    # --------------------------------------------------

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
            {
                'code': 'sv',
                'name': 'Swedish',
                'native_name': 'Svenska',
                'flag_emoji': '🇸🇪',
                'script': 'latin',
                'rtl': False,
                'has_romanization': False,
                'is_active': True,
                'order': 3,
            },
        ]

        for data in languages:
            Language.objects.get_or_create(code=data['code'], defaults=data)

        self.stdout.write('  ✅ Languages created')

    # --------------------------------------------------
    # TAGS
    # --------------------------------------------------

    def create_tags(self):
        tags = [
            'family',
            'shopping',
            'animals',
            'motivation',
            'daily-life',
            'adventure',
            'work',
            'friendship',
            'emotions',
            'humor',
            'conversation',
            'tprs',
            'aj-hoge',
            'vocabulary',
            'native-english',
        ]

        for tag in tags:
            StoryTag.objects.get_or_create(
                name=tag,
                defaults={'slug': slugify(tag)}
            )

        self.stdout.write('  ✅ Story tags created')

    # --------------------------------------------------
    # STORY PACKAGES
    # --------------------------------------------------

    def create_story_packages(self):
        english = Language.objects.get(code='en')

        stories = [
            {
                'slug': 'saras-giant-cat-shopping-day',
                'title': 'Sara And The Giant Hungry Cat',
                'level_min': 'A1',
                'level_max': 'C1',
                'story_type': 'educational',
                'estimated_read_minutes': 35,
                'sections': self.sara_story_sections(),
            },
            {
                'slug': 'allen-vs-tom-cruise-race',
                'title': 'The Motorcycle Race On Van Ness Street',
                'level_min': 'A2',
                'level_max': 'C1',
                'story_type': 'action',
                'estimated_read_minutes': 30,
                'sections': self.allen_story_sections(),
            },
            {
                'slug': 'rabbit-and-lion-clever-trick',
                'title': 'The Clever Rabbit And The Cruel Lion',
                'level_min': 'A1',
                'level_max': 'B2',
                'story_type': 'fable',
                'estimated_read_minutes': 28,
                'sections': self.rabbit_story_sections(),
            },
            {
                'slug': 'mias-secret-laboratory',
                'title': 'The Secret Inside The Laboratory',
                'level_min': 'A2',
                'level_max': 'C1',
                'story_type': 'mystery',
                'estimated_read_minutes': 32,
                'sections': self.mia_story_sections(),
            },
            {
                'slug': 'leylas-evening-walk',
                'title': 'Leyla’s Quiet Evening Walk',
                'level_min': 'A1',
                'level_max': 'B2',
                'story_type': 'daily-life',
                'estimated_read_minutes': 20,
                'sections': self.leyla_story_sections(),
            },
            {
                'slug': 'daniels-work-from-home-routine',
                'title': 'Daniel Learns To Focus At Home',
                'level_min': 'A1',
                'level_max': 'B2',
                'story_type': 'productivity',
                'estimated_read_minutes': 24,
                'sections': self.daniel_story_sections(),
            },
        ]

        for order, data in enumerate(stories, start=1):
            story, created = Story.objects.get_or_create(
                slug=data['slug'],
                defaults={
                    'language': english,
                    'title': data['title'],
                    'level_min': data['level_min'],
                    'level_max': data['level_max'],
                    'story_type': data['story_type'],
                    'estimated_read_minutes': data['estimated_read_minutes'],
                    'is_premium': False,
                    'is_published': True,
                    'order': order,
                }
            )

            for version_type, content in data['sections'].items():
                StoryVersion.objects.get_or_create(
                    story=story,
                    version_type=version_type,
                    defaults={
                        'content': content,
                    }
                )

            self.create_story_quizzes(story)

            self.stdout.write(f'  ✅ Story package created: {story.title}')

    # --------------------------------------------------
    # SARA STORY PACKAGE
    # --------------------------------------------------

    def sara_story_sections(self):
        return {
            'title': 'Sara And The Giant Hungry Cat',

            'original': '''
# ORIGINAL STORY

Sara Smith lived in San Francisco with her husband John, their two children, and a gigantic cat named Bubba. Bubba was not an ordinary cat. He weighed 258 pounds and ate enormous amounts of food every day.

One morning at 9 a.m., Sara drove to the pet store because Bubba was almost out of food. She bought 68 bags of cat food. Normally, each bag cost $15, but the store was offering a discount, so she paid only $10 per bag.

Other customers stared at Sara because her shopping cart was completely full.

After paying $680 with her credit card, Sara drove toward home. On the way, she stopped at a convenience store because Bubba also loved milk.

She bought 30 gallons.

The cashier looked shocked and asked if she owned a tiger.

Sara laughed.

When she finally returned home at 11 a.m., Bubba was waiting at the front door. The giant cat was hungry again.
''',

            'present': '''
# PRESENT TENSE VERSION

Sara Smith wakes up early in her small San Francisco house. Morning sunlight enters through the kitchen window while Bubba, her gigantic cat, walks heavily across the floor.

The wooden floor shakes slightly every time Bubba moves.

Sara sighs when she looks at the empty cat food containers.

"We need more food again," she thinks.

At exactly 9 a.m., she grabs her keys, gets into her car, and drives through the busy streets of San Francisco. The cool morning air feels fresh, but Sara already knows this shopping trip will be expensive.

Inside the pet store, colorful bags of cat food are stacked everywhere. Sara pushes a shopping cart down the aisle and begins loading bag after bag.

Ten bags.
Twenty bags.
Thirty bags.

People begin staring.

One employee laughs nervously and asks, "How many cats do you have?"

Sara smiles.

"Only one."

The employee looks confused.

Sara continues shopping.

Luckily, the cat food is discounted today. Instead of paying fifteen dollars for each bag, she only pays ten dollars.

She feels relieved.

After paying with her credit card, she carries everything outside.

Then she suddenly remembers the milk.

Bubba absolutely loves milk.

Sara stops at a convenience store and buys thirty gallons.

The cashier blinks several times.

"Ma'am... are you feeding a cat or a dinosaur?"

Sara laughs loudly.

By 11 a.m., she finally arrives home.

Bubba is already standing near the front door.

The giant cat lets out a deep, dramatic meow.

Sara shakes her head.

"You’re always hungry," she says.
''',

            'past': '''
# PAST TENSE VERSION

Last Saturday was one of the strangest shopping days Sara had ever experienced.

She had realized early that morning that Bubba, her enormous cat, had almost finished all of his food.

That was a serious problem.

Bubba weighed more than many adult humans and seemed hungry all the time.

Sara had driven to the pet store around 9 a.m. and immediately noticed a huge discount on cat food.

The sale felt like a miracle.

She had filled her shopping cart with 68 bags while strangers stared at her in disbelief.

One woman had even whispered, "Maybe she owns a zoo."

Sara remembered laughing quietly.

After paying hundreds of dollars, she had struggled to fit everything into her car.

Then she remembered the milk.

She had stopped at a convenience store and bought thirty gallons because Bubba loved drinking milk almost as much as eating cat food.

The cashier had looked completely speechless.

When Sara finally returned home, she had felt exhausted.

But Bubba had been waiting at the front door like a giant furry guard.

Looking back later that night, Sara realized something funny.

No matter how much food she bought, Bubba somehow always acted like he had never eaten before.
''',

            'future': '''
# FUTURE TENSE VERSION

Tomorrow morning, Sara will probably wake up to another loud meow from Bubba.

The giant cat will once again finish most of his food before breakfast.

Sara will drive back to the pet store because living with Bubba will continue to require constant shopping.

She will likely buy dozens of bags again, especially if the store offers another discount.

Customers will probably stare at her cart just like before.

Someone may ask if she owns multiple animals.

Sara will laugh and explain that Bubba is simply enormous.

After leaving the pet store, she will stop for milk because Bubba will still love milk more than almost anything.

The cashier will probably remember her.

When she arrives home, Bubba will certainly be waiting by the door.

And despite all the food Sara buys, the giant cat will almost definitely act hungry again.
''',

            'vocabulary': '''
# VOCABULARY EXPANSION VERSION

## Advanced Vocabulary

| Word | Meaning | Synonyms | Example |
|------|----------|-----------|----------|
| gigantic | extremely large | enormous, massive, huge | Bubba was a gigantic cat. |
| exhausted | extremely tired | drained, worn out, fatigued | Sara felt exhausted after shopping. |
| discount | reduced price | bargain, sale, markdown | The store offered a discount. |
| stare | look for a long time | gaze, observe, watch | Customers stared at Sara’s cart. |
| convenience store | small local shop | mini market, corner store | Sara bought milk from a convenience store. |

## Useful Phrases

- running out of food
- buying in bulk
- a fantastic deal
- completely shocked
- waiting at the door

## Real-Life Example Sentences

1. I bought this laptop at a huge discount.
2. Everyone stared when the celebrity entered the restaurant.
3. After work, I felt completely exhausted.
4. Buying in bulk can save money.
5. My dog always waits at the door when I come home.
''',

            'native': '''
# NATIVE SPEAKER STYLE VERSION

Honestly, Sara’s life sounded pretty normal until people heard about Bubba.

Bubba wasn’t just a big cat.

He was absurdly huge.

The kind of huge that made strangers stop talking for a second.

So when Sara rolled into the pet store and started throwing bag after bag of cat food into her cart, people naturally started staring.

One guy finally asked, "Lady... how many cats do you own?"

Sara smiled.

"Just one."

The guy looked genuinely concerned.

Then came the milk.

Thirty gallons.

At that point, the cashier looked like he was trying to solve a crime.

By the time Sara got home, she was exhausted.

But Bubba was sitting at the front door like he’d been starving for weeks.

Honestly, Sara had started wondering if her cat secretly had a second stomach.
''',

            'conversation': '''
# DAILY CONVERSATION VERSION

"No way. Your cat weighs how much?"

"Two hundred fifty-eight pounds."

"That’s not a cat. That’s a bear."

"Honestly, sometimes I think the same thing."

"So what happened at the pet store?"

"People kept staring at me because I bought sixty-eight bags of cat food."

"Sixty-eight?!"

"Yep. There was a discount, so I bought a lot."

"Actually, that makes sense."

"Then I stopped to buy milk."

"Let me guess... for Bubba?"

"Exactly."

"How much milk did you buy?"

"Thirty gallons."

"No way."

"The cashier asked if I owned a tiger."

"Honestly, I would’ve asked the same thing."
''',

            'idioms': '''
# ADVANCED IDIOM VERSION

Sara had her hands full living with Bubba.

Keeping such a gigantic cat fed cost an arm and a leg.

Still, Sara tried to stay one step ahead by buying cat food whenever there was a good deal.

At the pet store, people looked at her cart and immediately did a double take.

One customer even joked that Sara must be running a zoo.

But Sara didn’t miss a beat.

She simply smiled and continued shopping.

By the time she got home, she was completely worn out, but Bubba was already ready for another meal.

## IDIOM LIST

| Idiom | Meaning | Example |
|-------|----------|----------|
| hands full | very busy | I have my hands full this week. |
| cost an arm and a leg | very expensive | That car costs an arm and a leg. |
| one step ahead | prepared earlier | She stays one step ahead at work. |
| double take | second surprised look | I did a double take when I saw him. |
| miss a beat | hesitate emotionally | He didn’t miss a beat during the interview. |
''',

            'emotional': '''
# EMOTIONAL STORYTELLING VERSION

Sara leaned against her car and closed her eyes for a moment.

The morning had already been exhausting.

Her arms hurt from lifting heavy bags, her back ached, and she still had gallons of milk sitting in the trunk.

But when she looked toward the house, she saw Bubba waiting by the door.

The enormous cat looked impatient, but strangely comforting at the same time.

Life was chaotic.

Money disappeared quickly.

People stared.

Shopping trips turned into public events.

Still, Bubba was family.

Sara smiled softly.

Even on difficult days, coming home to her family — John, the children, and their ridiculous giant cat — made everything feel warm again.
''',

            'mini_story': '''
# QUESTION & ANSWER MINI STORY VERSION

Sara has a cat.

Does Sara have a dog?

No, no.

She does not have a dog.

She has a cat.

What kind of cat does she have?

A gigantic cat.

That’s right.

Is Bubba small?

No, no.

Bubba is enormous.

How enormous is Bubba?

He weighs 258 pounds.

Does he weigh 20 pounds?

Of course not.

He weighs 258 pounds.

Does Sara buy one bag of cat food?

No.

She buys 68 bags.

Why does she buy 68 bags?

Because Bubba is always hungry.

Exactly.

Does Bubba love milk?

Yes, yes.

He loves milk.

How much milk does Sara buy?

Thirty gallons.

Thirty gallons for a mouse?

No, no.

Thirty gallons for Bubba.

When Sara gets home, is Bubba sleeping?

No.

He is waiting at the door.

Why?

Because he is hungry again.

Exactly.
''',
        }

    # --------------------------------------------------
    # ALLEN STORY PACKAGE
    # --------------------------------------------------

    def allen_story_sections(self):
        return {
            'original': 'Allen races Tom Cruise through San Francisco streets and wins after the police stop Tom.',
            'present': 'Allen rides his motorcycle through Van Ness Street while engines roar loudly around him...',
            'past': 'Allen remembered the excitement of racing beside a red Ferrari in San Francisco...',
            'future': 'Tomorrow Allen will probably remember the race for the rest of his life...',
            'vocabulary': 'Vocabulary: roar, accelerate, rival, reckless, victory, challenge...',
            'native': 'Man, the second Allen realized the Ferrari driver was Tom Cruise, things got crazy...',
            'conversation': '"Wait... you raced Tom Cruise?" "Yep, and the police stopped him."',
            'idioms': 'Allen wanted to leave Tom in the dust and prove he could hold his own...',
            'emotional': 'Allen’s heart pounded as the traffic light turned green...',
            'mini_story': 'Does Allen ride a bicycle? No, no. He rides a motorcycle...',
        }

    # --------------------------------------------------
    # RABBIT STORY PACKAGE
    # --------------------------------------------------

    def rabbit_story_sections(self):
        return {
            'original': 'A clever rabbit tricks a cruel lion into jumping into a deep well.',
            'present': 'The frightened animals gather together while the lion hunts every day...',
            'past': 'The forest had once lived in fear before the rabbit changed everything...',
            'future': 'The rabbit will soon discover a dangerous but clever plan...',
            'vocabulary': 'Vocabulary: cruel, terrified, clever, deceive, reflection, courage...',
            'native': 'Honestly, the rabbit was tiny, but he completely outsmarted the lion...',
            'conversation': '"How did the rabbit defeat the lion?" "He tricked him with the well."',
            'idioms': 'The rabbit kept a cool head while the lion lost his temper...',
            'emotional': 'Every animal in the forest lived with constant fear in their hearts...',
            'mini_story': 'Is the lion kind? No, no. The lion is cruel...',
        }

    # --------------------------------------------------
    # MIA STORY PACKAGE
    # --------------------------------------------------

    def mia_story_sections(self):
        return {
            'original': 'Mia secretly enters her father’s laboratory and discovers the truth behind the scary sounds.',
            'present': 'Mia stands nervously outside the locked laboratory door...',
            'past': 'Years later, Mia still remembered the terrifying laugh from the laboratory...',
            'future': 'Mia and Liz will eventually decide to explore the laboratory together...',
            'vocabulary': 'Vocabulary: laboratory, mysterious, experiment, terrified, secret, invention...',
            'native': 'At first Mia seriously thought her dad was creating a monster downstairs...',
            'conversation': '"You actually went into the lab?" "Yeah, and we thought we were going to die."',
            'idioms': 'Mia’s curiosity got the best of her when she entered the lab...',
            'emotional': 'The darkness inside the laboratory made Mia’s heartbeat faster...',
            'mini_story': 'Does Mia hear music? No, no. She hears an evil laugh...',
        }

    # --------------------------------------------------
    # LEYLA STORY PACKAGE
    # --------------------------------------------------

    def leyla_story_sections(self):
        return {
            'original': 'Leyla takes quiet evening walks and feels connected to her neighborhood.',
            'present': 'Every evening Leyla walks slowly through familiar streets...',
            'past': 'Leyla had always loved short evening walks after long days...',
            'future': 'Tomorrow evening Leyla will probably meet another neighbor during her walk...',
            'vocabulary': 'Vocabulary: atmosphere, neighborhood, belonging, peaceful, familiar, connection...',
            'native': 'Leyla’s evening walks weren’t exciting, but somehow they always mattered...',
            'conversation': '"Did you see the new bakery?" "Yeah, the neighborhood feels different lately."',
            'idioms': 'Leyla enjoyed slowing down and taking a breather after work...',
            'emotional': 'In a huge city, Leyla sometimes felt invisible until small conversations reminded her she belonged...',
            'mini_story': 'Does Leyla drive every evening? No, no. She walks...',
        }

    # --------------------------------------------------
    # DANIEL STORY PACKAGE
    # --------------------------------------------------

    def daniel_story_sections(self):
        return {
            'original': 'Daniel works from home and learns how to stay focused despite distractions.',
            'present': 'Daniel starts his work-from-home morning with coffee and a clear routine...',
            'past': 'At first Daniel struggled badly with distractions while working from home...',
            'future': 'Daniel will continue improving his productivity with small habits...',
            'vocabulary': 'Vocabulary: distraction, productive, routine, concentration, schedule, discipline...',
            'native': 'Working from home sounded amazing until Daniel realized his fridge had become his biggest enemy...',
            'conversation': '"How do you stay focused at home?" "Honestly, short breaks changed everything."',
            'idioms': 'Daniel finally got back on track after creating a better routine...',
            'emotional': 'Daniel wanted to prove to himself that he could stay disciplined even alone at home...',
            'mini_story': 'Does Daniel go to the office today? No, no. He works from home...',
        }

    # --------------------------------------------------
    # QUIZZES
    # --------------------------------------------------

    def create_story_quizzes(self, story):
        quiz, _ = Quiz.objects.get_or_create(
            story=story,
            version_type='original',
            defaults={
                'title': f'{story.title} Quiz',
                'is_premium': False,
            }
        )

        quiz_data = [
            {
                'question_text': 'Who is the main character of the story?',
                'correct_answer': 'Sara',
                'question_type': 'fill_blank',
                'order': 1,
            },
            {
                'question_text': 'What animal appears in the story?',
                'correct_answer': 'Cat',
                'question_type': 'fill_blank',
                'order': 2,
            },
            {
                'question_text': 'Does the character buy food?',
                'correct_answer': 'Yes',
                'question_type': 'true_false',
                'order': 3,
            },
            {
                'question_text': 'Where does the story happen?',
                'correct_answer': 'San Francisco',
                'question_type': 'fill_blank',
                'order': 4,
            },
            {
                'question_text': 'Is the story emotional and educational?',
                'correct_answer': 'Yes',
                'question_type': 'true_false',
                'order': 5,
            },
        ]

        for item in quiz_data:
            QuizQuestion.objects.get_or_create(
                quiz=quiz,
                order=item['order'],
                defaults={
                    'question_text': item['question_text'],
                    'correct_answer': item['correct_answer'],
                    'question_type': item['question_type'],
                    'options': [],
                    'hint_text': 'Think carefully about the story.',
                    'explanation': 'This question checks story comprehension.',
                }
            )

    # --------------------------------------------------
    # GLOBAL VOCABULARY
    # --------------------------------------------------

    def create_global_vocabulary(self):
        english = Language.objects.get(code='en')
        turkish = Language.objects.get(code='tr')

        vocabulary = [
            {
                'word': 'gigantic',
                'part_of_speech': 'adjective',
                'definition': 'extremely large in size',
                'difficulty_level': 'B1',
                'translation': 'devasa',
                'synonyms': ['huge', 'massive', 'enormous'],
            },
            {
                'word': 'focus',
                'part_of_speech': 'verb',
                'definition': 'to concentrate attention',
                'difficulty_level': 'A2',
                'translation': 'odaklanmak',
                'synonyms': ['concentrate', 'pay attention', 'stay alert'],
            },
            {
                'word': 'mysterious',
                'part_of_speech': 'adjective',
                'definition': 'difficult to explain or understand',
                'difficulty_level': 'B1',
                'translation': 'gizemli',
                'synonyms': ['strange', 'secretive', 'unknown'],
            },
            {
                'word': 'gigantic',
                'part_of_speech': 'adjective',
                'definition': 'extremely large',
                'difficulty_level': 'B1',
                'translation': 'devasa',
                'synonyms': ['huge', 'massive', 'enormous'],
            },
            {
                'word': 'exhausted',
                'part_of_speech': 'adjective',
                'definition': 'very tired',
                'difficulty_level': 'B1',
                'translation': 'bitkin',
                'synonyms': ['drained', 'fatigued', 'worn out'],
            },
            {
                'word': 'productive',
                'part_of_speech': 'adjective',
                'definition': 'achieving a lot of work',
                'difficulty_level': 'A2',
                'translation': 'verimli',
                'synonyms': ['efficient', 'effective', 'focused'],
            },
            {
                'word': 'terrified',
                'part_of_speech': 'adjective',
                'definition': 'extremely afraid',
                'difficulty_level': 'B1',
                'translation': 'dehşete düşmüş',
                'synonyms': ['frightened', 'scared', 'horrified'],
            },
        ]

        for item in vocabulary:
            word, created = Word.objects.get_or_create(
                language=english,
                word=item['word'],
                defaults={
                    'part_of_speech': item['part_of_speech'],
                    'definition': item['definition'],
                    'difficulty_level': item['difficulty_level'],
                }
            )

            WordTranslation.objects.get_or_create(
                word=word,
                target_language=turkish,
                defaults={
                    'translation': item['translation']
                }
            )

            for synonym in item['synonyms']:
                synonym_word, _ = Word.objects.get_or_create(
                    language=english,
                    word=synonym,
                    defaults={
                        'part_of_speech': item['part_of_speech'],
                        'definition': f'Similar meaning to {item["word"]}',
                        'difficulty_level': item['difficulty_level'],
                    }
                )

                WordSynonym.objects.get_or_create(
                    word=word,
                    synonym=synonym_word,
                )

        self.stdout.write('  ✅ Global vocabulary created')
