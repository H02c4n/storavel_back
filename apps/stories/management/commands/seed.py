# apps/stories/management/commands/seed_combined.py
import random
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from apps.languages.models import Language, UserTargetLanguage
from apps.stories.models import Story, StoryVersion, StoryTag, UserStoryProgress
from apps.vocabulary.models import Word, WordTranslation, WordSynonym, StoryWord
from apps.notebook.models import UserWord, UserWordCollection
from apps.quizzes.models import Quiz, QuizQuestion
from apps.progress.models import UserProgress, DailyActivity
from apps.accounts.models import UserSettings

User = get_user_model()

class Command(BaseCommand):
    help = 'Seed the database with two stories: Rabbit & Lion + Laboratory'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🌱 Seeding combined stories: Rabbit & Lion + Laboratory...'))

        # 1. Language
        self.create_languages()

        # 2. Demo user
        demo_user = self.create_users()

        # 3. Tags
        tags = self.create_tags()

        # 4. Rabbit & Lion story
        rabbit_story = self.create_rabbit_lion_story(demo_user, tags)

        # 5. Laboratory story
        lab_story = self.create_laboratory_story(demo_user, tags)

        # 6. Vocabulary for both stories
        vocab_rabbit = self.create_vocabulary_rabbit()
        vocab_lab = self.create_vocabulary_laboratory()
        all_vocab = {**vocab_rabbit, **vocab_lab}

        # 7. Link words to stories
        self.link_rabbit_words(rabbit_story, vocab_rabbit)
        self.link_lab_words(lab_story, vocab_lab)

        # 8. Quizzes
        self.create_quiz_rabbit(rabbit_story)
        self.create_quiz_laboratory(lab_story)

        # 9. Update demo user
        self.update_user_progress(demo_user, rabbit_story, lab_story, all_vocab)

        self.stdout.write(self.style.SUCCESS('✅ Combined seeding completed!'))
        self.stdout.write(f'   📖 Rabbit & Lion: /stories/{rabbit_story.slug}')
        self.stdout.write(f'   📖 Laboratory:    /stories/{lab_story.slug}')

    # ------------------------------------------------------------
    # Helper: languages
    # ------------------------------------------------------------
    def create_languages(self):
        english, _ = Language.objects.get_or_create(
            code='en',
            defaults={'name': 'English', 'native_name': 'English', 'flag_emoji': '🇺🇸',
                      'script': 'latin', 'rtl': False, 'has_romanization': False,
                      'is_active': True, 'order': 1}
        )
        self.stdout.write(f'  ✅ Language: English')
        for code in ['sv', 'tr', 'es', 'fr']:
            Language.objects.get_or_create(code=code)

    def create_users(self):
        demo, created = User.objects.get_or_create(
            email='demo@storavel.com',
            defaults={'username': 'demo_user', 'display_name': 'Demo Learner',
                      'is_premium': False, 'is_active': True}
        )
        if created:
            demo.set_password('demo123')
            demo.save()
            UserSettings.objects.get_or_create(user=demo)
            self.stdout.write('  ✅ Demo user created (demo@storavel.com / demo123)')
        else:
            self.stdout.write('  ⚠️ Demo user already exists')
        return demo

    def create_tags(self):
        tag_names = [
            'clever', 'rabbit', 'lion', 'fable', 'wisdom', 'courage', 'trickery',  # rabbit
            'laboratory', 'mystery', 'doll', 'fear', 'curiosity', 'family', 'surprise', 'birthday'  # lab
        ]
        tags = []
        for name in tag_names:
            tag, _ = StoryTag.objects.get_or_create(name=name, defaults={'slug': slugify(name)})
            tags.append(tag)
        self.stdout.write(f'  ✅ {len(tags)} story tags created')
        return tags

    # ------------------------------------------------------------
    # Story: The Clever Rabbit and the Proud Lion
    # ------------------------------------------------------------
    def create_rabbit_lion_story(self, user, tags):
        english = Language.objects.get(code='en')
        story, created = Story.objects.get_or_create(
            slug='the-clever-rabbit-and-the-proud-lion',
            defaults={
                'language': english,
                'title': "The Clever Rabbit and the Proud Lion",
                'level_min': 'A2',
                'level_max': 'B1',
                'story_type': 'narrative',
                'estimated_read_minutes': 15,
                'is_premium': False,
                'is_published': True,
                'order': 5,
            }
        )
        if created:
            story.tags.set([t for t in tags if t.name in ['clever','rabbit','lion','fable','wisdom','courage','trickery']])
            self.stdout.write('  ✅ Story: The Clever Rabbit and the Proud Lion')

        versions = {
            'original': """In a large green forest, there lived a cruel and powerful lion. Every day, he hunted many animals and ate more than he needed. The animals in the forest were terrified because they believed the lion would eventually kill every creature living there.

One day, the animals gathered together to find a solution. They went to the lion and said, “Please listen to us. We have a deal for you. If you promise to eat only one animal each day, then one animal will come to you daily. You won’t need to hunt anymore.”

The lion liked the idea because it meant he would not have to waste energy chasing animals through the forest. However, he warned them angrily, “If no animal comes one day, I will hunt every one of you the next day!”

From that day forward, the animals followed the agreement. Each day, one animal went sadly to the lion while the others remained safe.

Finally, one day, it became the rabbit’s turn.

Unlike the others, the rabbit walked very slowly toward the lion’s cave. The sun moved across the sky, and the lion became hungrier and angrier while waiting.

When the rabbit finally arrived, the lion roared, “Why are you so late?”

The rabbit bowed nervously and replied, “Your Majesty, I tried to come earlier, but another lion stopped me in the forest. He said he was the true king.”

The lion’s eyes burned with anger. “Another lion? Impossible! I am the only king of this forest. Take me to him immediately!”

The rabbit pretended to be frightened and said softly, “Of course, Your Majesty. I will show you where he lives.”

The rabbit guided the lion deep into the forest until they reached an old stone well filled with water. The rabbit pointed toward the well and whispered, “The other lion lives down there.”

The lion looked into the water and saw his own reflection staring back at him. Believing it was another lion challenging him, he roared loudly. The reflection roared back.

Filled with rage, the lion jumped into the well to attack his enemy.

But the well was deep, and the lion could not escape. He disappeared beneath the water and never returned.

The rabbit hopped back through the forest with a smile. When the other animals heard what had happened, they celebrated joyfully. Thanks to the rabbit’s intelligence and courage, the forest was finally safe.""",

            'present': """The forest is unusually quiet this morning. Birds sing softly from the trees, but beneath the peaceful sounds, fear spreads through every corner of the woods.

A huge lion rules the forest with cruelty. Every day, he hunts endlessly. His heavy paws crush dry leaves beneath him, and his terrifying roar echoes through the trees. The animals tremble whenever they hear it.

The deer hide behind bushes. The monkeys stay silent in the treetops. Even the wolves avoid the lion’s path.

The animals gather near a river, desperate and exhausted. Their eyes are filled with worry.

“We can’t continue living like this,” a deer says nervously.

“He’ll kill all of us eventually,” another animal whispers.

Finally, they decide to speak with the lion.

The lion lies lazily near his cave while warm sunlight shines across his golden fur. He looks powerful, dangerous, and proud.

The animals approach carefully.

One of them says, “Great Lion, we have a proposal. If you stop hunting, one animal will come to you every day for your meal.”

The lion narrows his eyes. He thinks about it. Hunting requires effort. Chasing animals through the forest tires him.

“Hmmm,” he growls deeply. “Very well. But if no animal comes one day, I’ll destroy every creature in this forest.”

The animals agree immediately.

Days pass.

Each morning, one frightened animal walks toward the lion’s cave while the others watch sadly from a distance.

Then one day, it becomes the rabbit’s turn.

The rabbit is small, quiet, and thoughtful. As he walks through the forest, sunlight filters through the leaves above him. A cool wind brushes against his soft fur.

But the rabbit isn’t simply walking.

He’s thinking.

“There must be another way,” he tells himself.

Instead of hurrying, the rabbit moves slowly. Very slowly.

Meanwhile, the lion grows impatient. His stomach growls loudly. He paces back and forth near the cave entrance.

“Where is that rabbit?” he roars furiously.

Hours later, the rabbit finally appears.

The lion’s eyes blaze with anger.

“Why are you late?” he shouts.

The rabbit lowers his ears and pretends to shake with fear.

“Your Majesty,” he says softly, “another lion stopped me on the way here. He claimed that he is the true king of the forest.”

The lion freezes.

Another king?

Impossible.

His pride burns hotter than fire.

“Take me to him NOW!” the lion roars.

The rabbit nods carefully and leads the lion through the forest. They pass tall trees, tangled vines, and dark shadows until they arrive at an old stone well hidden among the grass.

The rabbit points downward.

“He lives there.”

The lion steps closer and looks into the water.

Suddenly, he sees another lion staring back at him.

His own reflection.

But he doesn’t realize it.

The lion roars angrily, and the reflection roars too. Water ripples across the surface.

The lion becomes wild with rage.

Without thinking, he leaps into the well.

A loud splash breaks the silence.

The water swirls violently.

Then everything becomes still.

The rabbit quietly steps back from the well.

A smile slowly spreads across his face.

At sunset, the rabbit returns to the forest and tells the animals what happened. Cheers fill the air. Birds fly upward. The animals dance, laugh, and cry with relief.

For the first time in a long time, the forest finally feels safe.""",

            'past': """I still remember the story the old animals used to tell near the fireflies at night — the story of the rabbit who saved the forest.

Back then, the forest had lived under constant fear. A massive lion had ruled the land with violence and hunger. Every morning, animals woke up wondering whether they would survive another day.

The lion had hunted endlessly. He killed far more animals than he needed, simply because he enjoyed his power. His roar alone had been enough to freeze the blood of every creature nearby.

Eventually, the animals became desperate. They knew they couldn’t keep running forever.

So they gathered together beneath the ancient trees and created a dangerous agreement. They offered the lion one animal each day in exchange for peace.

Surprisingly, the lion accepted.

At first, the arrangement seemed to work. The forest became quieter. Animals no longer spent every moment hiding.

But each day still carried sadness because one animal never returned.

Then the rabbit’s turn came.

The rabbit had appeared calm on the outside, but deep inside, his mind had been racing. He knew that simply accepting death was meaningless.

As he slowly walked through the forest that afternoon, he noticed an old well surrounded by stones and weeds. When he looked into the water, he suddenly saw his own reflection.

That was when the idea came to him.

Later, when he finally arrived at the lion’s cave, the lion had already become furious from hunger.

“Why are you late?” the lion had thundered.

The rabbit bowed respectfully and explained that another lion had blocked his path.

The lion’s pride had exploded instantly. He could not tolerate the idea of a rival.

Without hesitation, he demanded to see this so-called enemy.

The rabbit carefully led him through the forest until they reached the well.

I can almost imagine the moment.

The sunlight must have reflected across the dark water while the angry lion stared downward. Seeing his own face, he truly believed another lion stood below him.

And then, blinded by rage and arrogance, he jumped.

The splash echoed through the forest.

But the lion never climbed out.

When the rabbit returned and told the others what had happened, the entire forest celebrated. Animals cried with happiness. Some laughed in disbelief. Others simply stood silently, finally feeling peace after so much fear.

The rabbit had not defeated the lion with strength.

He had defeated him with intelligence.

And that was the lesson everyone remembered.""",

            'future': """One day, a terrible lion will rule over a peaceful forest. He will hunt constantly, and the animals will become terrified of him. Every creature will fear that sooner or later the lion will destroy them all.

Eventually, the animals will gather together to discuss what they should do. After many worried conversations, they will decide to make a risky agreement with the lion.

They will say, “If you stop hunting us, one animal will come to you every day.”

The lion will accept because the arrangement will make his life easier. Still, he will warn them harshly, “If no animal comes, I’ll hunt every one of you.”

For a while, the plan will work. Each day, one animal will sacrifice itself while the others survive.

Then the rabbit’s turn will arrive.

Unlike the other animals, the rabbit will not panic completely. While walking slowly through the forest, he will begin thinking carefully. He will realize that the lion’s greatest weakness is not hunger — it is pride.

The rabbit will purposely arrive late.

The lion will become furious after waiting for hours.

“Why will you arrive so late?” the lion will roar.

The rabbit will pretend to be terrified and say, “Another lion stopped me. He claimed he was the true king.”

The moment the lion hears those words, his anger will explode.

“No one else will rule my forest!” he will shout.

The rabbit will then guide the lion to an old well hidden deep in the woods.

When the lion looks into the water, he will see his own reflection. However, he will mistake it for another lion challenging him.

Driven by rage, he will jump into the well to attack the rival.

But he will never escape.

Soon afterward, the rabbit will return to the forest with wonderful news. The animals will celebrate with excitement, relief, and gratitude.

In the future, the story of the clever rabbit will continue teaching generations an important lesson:

Intelligence will often defeat strength.""",

            'vocabulary': """Vocabulary-Rich Story

A ferocious lion dominated a dense forest and terrorized every creature living there. His appetite was enormous, and his ruthless behavior created constant panic among the animals.

The frightened creatures eventually negotiated with the lion. They proposed a compromise: one animal would voluntarily present itself each day if the lion agreed to stop hunting randomly.

At first, the arrangement appeared reasonable.

However, when the rabbit’s turn arrived, the small animal devised a brilliant strategy. Instead of surrendering helplessly, the rabbit manipulated the lion’s arrogance and lured him toward a deep well.

Mistaking his own reflection for a rival, the lion impulsively leaped into the water and disappeared forever.

The rabbit’s ingenuity rescued the entire forest.

Vocabulary Table:
- Ferocious: Extremely fierce or violent
- Dominated: Controlled completely
- Ruthless: Cruel and without mercy
- Negotiated: Discussed to reach an agreement
- Compromise: An agreement between two sides
- Devised: Planned cleverly
- Manipulated: Controlled cleverly
- Arrogance: Excessive pride
- Impulsively: Acting without thinking
- Ingenuity: Creative intelligence

Synonym Groups:
Angry → furious, irritated, enraged, annoyed, outraged
Clever → intelligent, brilliant, sharp, wise, resourceful
Afraid → terrified, frightened, nervous, anxious, fearful

Useful Phrases:
- "Blinded by pride" (too proud to think clearly)
- "Think on your feet" (react quickly and intelligently)
- "A matter of survival" (necessary to stay alive)""",

            'native': """So there’s this lion living in the forest, right? And honestly, the guy’s completely out of control.

Every single day he’s hunting animals, killing way more than he needs, just because he can. The whole forest is basically living in survival mode. Nobody feels safe anymore.

Eventually the animals get together and say, “Okay, we need a plan before this dude wipes all of us out.”

So they approach the lion very carefully and offer him a deal.

They’re like, “Look, if you stop hunting randomly, we’ll send you one animal every day. You won’t even have to chase anybody.”

And surprisingly, the lion goes for it. I mean, from his perspective, it’s free food with zero effort.

But then he adds, “If nobody shows up one day, I’m hunting everybody tomorrow.” Classic tyrant behavior.

So the system starts working. Every day one animal goes, and the rest stay alive another day.

Then eventually it’s the rabbit’s turn.

Now this rabbit? Smart little guy.

Instead of rushing over there terrified, he takes his sweet time. Just walks slowly through the forest thinking everything through.

By the time he arrives, the lion is absolutely furious.

“Why are you late?!” the lion roars.

And the rabbit goes, “Actually… there’s a problem. Another lion stopped me. He says HE’S the king of the forest.”

Huge mistake.

The second the lion hears that, his ego completely explodes.

“There’s another lion?! Take me to him!”

So the rabbit leads him to this old well in the middle of the forest.

He points down and says, “He’s in there.”

The lion looks into the water… sees his own reflection… and completely loses it.

He roars. The reflection roars back.

And without thinking for even one second, the lion jumps straight into the well trying to attack the “other lion.”

Gone. That’s it.

The rabbit casually hops back to the others and basically says, “Problem solved.”

And honestly? The entire forest probably slept peacefully for the first time in years.""",

            'dialog': """Emma: Hey, do you remember that story about the rabbit and the lion?
Jake: Oh yeah! The clever rabbit tricking the lion, right?
Emma: Exactly. Honestly, it’s one of my favorite old stories.
Jake: Same here. The lion was terrifying though.
Emma: Totally. He kept killing animals every day, and everyone in the forest was scared.
Jake: Then the animals made that deal with him, didn’t they?
Emma: Yeah. They basically said, “Look, we’ll send you one animal every day if you stop hunting.”
Jake: Which honestly sounds terrible… but I guess they were desperate.
Emma: Exactly. At least most of them could survive that way.
Jake: And then it became the rabbit’s turn.
Emma: Right! But the rabbit was smart. He didn’t just accept his fate.
Jake: He showed up late on purpose, didn’t he?
Emma: Yep. And the lion was already angry because he’d been waiting so long.
Jake: I can imagine him roaring like crazy.
Emma: Seriously. Then the rabbit tells him there’s another lion in the forest.
Jake: Which was genius because the lion was super arrogant.
Emma: Exactly! The lion couldn’t handle the idea of another king.
Jake: So the rabbit takes him to the well…
Emma: …and the lion sees his own reflection.
Jake: But he thinks it’s another lion!
Emma: Yep. Then he jumps into the well trying to attack himself.
Jake: Honestly, that’s kind of hilarious.
Emma: It is. But it also teaches a good lesson.
Jake: Intelligence beats strength?
Emma: Exactly.""",

            'idioms': """The lion had ruled the forest for years, and all the animals were constantly on edge. Every day felt like a fight for survival, and nobody knew who would be next.

Eventually, the animals realized they were all in the same boat. If they didn’t come up with a solution quickly, the lion would wipe them out one by one.

To buy some time, they struck a deal with the lion. One animal would come to him each day so he wouldn’t need to hunt anymore.

At first, things seemed manageable.

Then the rabbit’s turn came.

Unlike the others, the rabbit didn’t panic or lose his head. Instead, he thought on his feet and came up with a clever plan.

When he finally arrived late, the lion flew off the handle.

The rabbit calmly explained that another lion had stopped him and claimed to rule the forest.

That comment pushed all the lion’s buttons.

The lion immediately demanded to confront his rival. He was so blinded by pride that he couldn’t see the trap right in front of him.

The rabbit led him to a deep well and told him the other lion was inside.

The lion looked into the water, saw his own reflection, and without missing a beat, jumped into the well.

In the end, the lion’s massive ego became his downfall.

Meanwhile, the rabbit saved the forest and proved that brains can beat brawn.

Idiom List:
- On edge (nervous or anxious)
- In the same boat (in the same difficult situation)
- Buy some time (delay something temporarily)
- Think on your feet (react quickly and intelligently)
- Fly off the handle (become suddenly angry)
- Push someone’s buttons (annoy or provoke someone)
- Blinded by pride (too proud to think clearly)
- Without missing a beat (immediately and smoothly)
- Brains over brawn (intelligence is better than strength)""",

            'emotional': """Fear had become part of everyday life in the forest.

The animals no longer sang freely in the mornings. Even the wind moving through the trees seemed quieter, heavier somehow — as if the entire forest itself was holding its breath.

The lion ruled with terror.

Every roar sent waves of panic through the woods. Mothers pulled their children close. Deer froze in silence. Small animals hid beneath roots and bushes, praying they would survive another day.

No one felt safe.

When the animals finally gathered together beneath the moonlight, despair filled their eyes. They were exhausted from living in fear.

Then came the painful agreement.

One animal each day.

A sacrifice for everyone else.

And somehow, that became their only hope.

Days passed slowly. Every sunrise brought sadness to another family.

Then one morning, the rabbit’s name was chosen.

The other animals looked at him with sympathy. Some lowered their heads. Others quietly cried.

But the rabbit said nothing.

As he walked through the forest alone, his small heart beat rapidly inside his chest. He was frightened — deeply frightened — but beneath that fear, another feeling slowly grew.

Determination.

“There has to be another way,” he whispered to himself.

The sunlight filtered softly through the trees as he wandered deeper into the forest. Then suddenly, he stopped beside an old forgotten well.

He looked into the water.

And in that silent moment, an idea appeared.

Hours later, when the rabbit finally stood before the lion, the enormous beast exploded with rage.

“WHY ARE YOU LATE?”

The roar shook the ground beneath the rabbit’s feet.

For a moment, fear nearly consumed him.

But he stayed calm.

“There was… another lion,” the rabbit answered quietly. “He said he was the true king.”

The lion’s eyes burned with fury.

The rabbit could almost feel the monster’s pride swallowing his judgment.

When they reached the old well, the forest became strangely silent.

The lion stared into the darkness below.

Then he saw it.

Another lion staring back.

His breathing became heavier. His anger exploded beyond control.

And then—

He jumped.

A violent splash shattered the silence.

Water crashed against the stone walls.

Then… nothing.

The rabbit stood there trembling. Not from fear anymore, but from relief.

For the first time in many months, the forest was free.

When the rabbit returned home, the animals surrounded him with tears, laughter, and disbelief. Some hugged him tightly. Others simply stared in amazement.

The smallest animal in the forest had defeated the strongest.

Not with violence.

Not with power.

But with courage, wisdom, and hope.""",

            'qa': """There is a big lion in the forest.
Is there a big lion in the forest? Yes, yes. There is a big lion in the forest.
Is there a tiger in the forest? No, no. There is not a tiger. There is a lion.
Is the lion small? No! The lion is big.

The lion kills many animals every day.
Does the lion kill many animals? Yes. He kills many animals every day.
Do the animals feel safe? No, no. They feel afraid.
Why are they afraid? Because the lion kills animals every day.

The animals make a plan.
Do the animals make a pizza? No, no. They do not make a pizza.
What do they make? They make a plan.
Do they talk to the lion? Yes. They talk to the lion.

The animals say, “Please eat only one animal each day.”
Do they ask the lion to eat one animal or one hundred animals? One animal. Just one animal each day.

The lion agrees.
Is the lion happy with the plan? Yes. The lion agrees with the plan.
Why does he agree? Because he does not want to hunt every day.

Every day, one animal goes to the lion.
Do all the animals go together? No. One animal goes each day.

Then one day, it is the rabbit’s turn.
Whose turn is it? It is the rabbit’s turn.
Is it the elephant’s turn? No, no. It is the rabbit’s turn.

The rabbit walks slowly.
Does the rabbit run quickly? No. He walks slowly.
Why does he walk slowly? Because he has a plan.

The lion becomes angry.
Is the lion calm? No! He becomes angry.
Why is the lion angry? Because the rabbit is late.

The rabbit says, “Another lion stopped me.”
Does the rabbit say another rabbit stopped him? No, no. Another lion stopped him.

The lion becomes furious.
Why? Because the other lion says he is the king.
Does the lion like that? Of course not! He hates that idea.

The rabbit takes the lion to a well.
Where does the rabbit take the lion? To a deep well.

What does the lion see in the water? He sees his own reflection.
Does he know it is his reflection? No, no. He thinks it is another lion.

The lion jumps into the well.
Does the rabbit jump into the well? No! The lion jumps into the well.
Why does he jump? Because he wants to attack the “other lion.”

Does the lion come out? No. He never comes out.

Are the animals happy afterward? Yes, yes! They are very happy.
Why are they happy? Because the clever rabbit saves the forest.
That’s right. Exactly."""
        }

        for vtype, content in versions.items():
            StoryVersion.objects.get_or_create(story=story, version_type=vtype, defaults={'content': content})
            self.stdout.write(f'    ✅ Version: {vtype}')
        UserStoryProgress.objects.get_or_create(user=user, story=story, defaults={'completed': False})
        return story

    # ------------------------------------------------------------
    # Story: The Secret Inside the Laboratory
    # ------------------------------------------------------------
    def create_laboratory_story(self, user, tags):
        english = Language.objects.get(code='en')
        story, created = Story.objects.get_or_create(
            slug='the-secret-inside-the-laboratory',
            defaults={
                'language': english,
                'title': "The Secret Inside the Laboratory",
                'level_min': 'A2',
                'level_max': 'B1',
                'story_type': 'narrative',
                'estimated_read_minutes': 12,
                'is_premium': False,
                'is_published': True,
                'order': 6,
            }
        )
        if created:
            story.tags.set([t for t in tags if t.name in ['laboratory','mystery','doll','fear','curiosity','family','surprise','birthday']])
            self.stdout.write('  ✅ Story: The Secret Inside the Laboratory')

        versions = {
            'original': """Mia lived with her father in a quiet house...""",
            'present': """Rain taps softly against the windows...""",
            'past': """Years later, Mia still remembered...""",
            'future': """One evening, Mia will walk slowly...""",
            'vocabulary': """Mia's father maintained a secretive laboratory...""",
            'native': """So Mia's dad has this laboratory in the basement...""",
            'dialog': """Sarah: Hey, have you heard the story about Mia and the laboratory?...""",
            'idioms': """Mia's father always kept his laboratory under wraps...""",
            'emotional': """The laboratory door always made Mia uneasy...""",
            'qa': """Mia's father has a laboratory. Does Mia's father have a laboratory?..."""
        }
        for vtype, content in versions.items():
            StoryVersion.objects.get_or_create(story=story, version_type=vtype, defaults={'content': content})
            self.stdout.write(f'    ✅ Version: {vtype}')
        UserStoryProgress.objects.get_or_create(user=user, story=story, defaults={'completed': False})
        return story

    # ------------------------------------------------------------
    # Vocabulary for Rabbit story (12 words)
    # ------------------------------------------------------------
    def create_vocabulary_rabbit(self):
        english = Language.objects.get(code='en')
        words_data = [
            {'word': 'ferocious', 'pos': 'adj', 'def': 'extremely fierce', 'level': 'B1',
             'trans': {'es':'feroz','tr':'vahşi','fr':'féroce','sv':'grym'}, 'syn':['fierce','savage']},
            {'word': 'dominate', 'pos': 'verb', 'def': 'to control completely', 'level': 'B1',
             'trans': {'es':'dominar','tr':'egemen olmak','fr':'dominer','sv':'dominera'}, 'syn':['control','rule']},
            {'word': 'ruthless', 'pos': 'adj', 'def': 'cruel without mercy', 'level': 'B2',
             'trans': {'es':'despiadado','tr':'acımasız','fr':'impitoyable','sv':'skoningslös'}, 'syn':['merciless','heartless']},
            {'word': 'negotiate', 'pos': 'verb', 'def': 'discuss to reach agreement', 'level': 'B1',
             'trans': {'es':'negociar','tr':'pazarlık etmek','fr':'négocier','sv':'förhandla'}, 'syn':['bargain','mediate']},
            {'word': 'compromise', 'pos': 'noun', 'def': 'mutual agreement', 'level': 'B2',
             'trans': {'es':'compromiso','tr':'uzlaşma','fr':'compromis','sv':'kompromiss'}, 'syn':['settlement','concession']},
            {'word': 'devise', 'pos': 'verb', 'def': 'plan cleverly', 'level': 'B2',
             'trans': {'es':'idear','tr':'tasarlamak','fr':'concevoir','sv':'utforma'}, 'syn':['invent','formulate']},
            {'word': 'arrogance', 'pos': 'noun', 'def': 'excessive pride', 'level': 'B2',
             'trans': {'es':'arrogancia','tr':'kibir','fr':'arrogance','sv':'arrogans'}, 'syn':['haughtiness','conceit']},
            {'word': 'impulsive', 'pos': 'adj', 'def': 'acting without thinking', 'level': 'B2',
             'trans': {'es':'impulsivo','tr':'düşüncesiz','fr':'impulsif','sv':'impulsiv'}, 'syn':['rash','hasty']},
            {'word': 'ingenuity', 'pos': 'noun', 'def': 'creative intelligence', 'level': 'C1',
             'trans': {'es':'ingenio','tr':'zekâ','fr':'ingéniosité','sv':'påhittighet'}, 'syn':['cleverness','resourcefulness']},
            {'word': 'clever', 'pos': 'adj', 'def': 'intelligent quick-witted', 'level': 'A2',
             'trans': {'es':'listo','tr':'akıllı','fr':'intelligent','sv':'smart'}, 'syn':['smart','sharp']},
            {'word': 'terrified', 'pos': 'adj', 'def': 'extremely frightened', 'level': 'A2',
             'trans': {'es':'aterrorizado','tr':'dehşete düşmüş','fr':'terrifié','sv':'skräckslagen'}, 'syn':['horrified','petrified']},
            {'word': 'reflection', 'pos': 'noun', 'def': 'image in mirror/water', 'level': 'A2',
             'trans': {'es':'reflejo','tr':'yansıma','fr':'reflet','sv':'reflektion'}, 'syn':['image','likeness']},
        ]
        return self._create_words(english, words_data)

    def link_rabbit_words(self, story, vocab_map):
        examples = [
            ('ferocious', 1, 'The ferocious lion terrorized the forest.'),
            ('dominate', 2, 'The lion dominated all the animals.'),
            ('ruthless', 3, 'His ruthless behavior frightened everyone.'),
            ('negotiate', 4, 'The animals negotiated with the lion.'),
            ('compromise', 5, 'They reached a compromise to survive.'),
            ('devise', 6, 'The rabbit devised a clever plan.'),
            ('arrogance', 7, "The lion's arrogance caused his downfall."),
            ('impulsive', 8, 'He made an impulsive decision to jump.'),
            ('ingenuity', 9, "The rabbit's ingenuity saved the forest."),
            ('clever', 10, 'The rabbit was clever and brave.'),
            ('terrified', 11, 'The animals were terrified of the lion.'),
            ('reflection', 12, 'The lion attacked his own reflection.'),
        ]
        for word_text, order, example in examples:
            word = vocab_map.get(word_text)
            if word:
                StoryWord.objects.get_or_create(story=story, word=word, defaults={'example_sentence': example, 'order': order})

    # ------------------------------------------------------------
    # Vocabulary for Laboratory story (12 words)
    # ------------------------------------------------------------
    def create_vocabulary_laboratory(self):
        english = Language.objects.get(code='en')
        words_data = [
            {'word': 'secretive', 'pos': 'adj', 'def': 'hiding information', 'level': 'B1',
             'trans': {'es':'reservado','tr':'gizemli','fr':'secret','sv':'hemlighetsfull'}, 'syn':['mysterious','private']},
            {'word': 'mysterious', 'pos': 'adj', 'def': 'difficult to understand', 'level': 'B1',
             'trans': {'es':'misterioso','tr':'gizemli','fr':'mystérieux','sv':'mystisk'}, 'syn':['enigmatic','puzzling']},
            {'word': 'sinister', 'pos': 'adj', 'def': 'evil or frightening', 'level': 'B2',
             'trans': {'es':'siniestro','tr':'uğursuz','fr':'sinistre','sv':'hotfull'}, 'syn':['menacing','creepy']},
            {'word': 'disturbing', 'pos': 'adj', 'def': 'causing worry', 'level': 'B2',
             'trans': {'es':'inquietante','tr':'rahatsız edici','fr':'perturbant','sv':'störande'}, 'syn':['troubling','alarming']},
            {'word': 'cautiously', 'pos': 'adv', 'def': 'carefully to avoid danger', 'level': 'B1',
             'trans': {'es':'con cautela','tr':'dikkatlice','fr':'prudemment','sv':'försiktigt'}, 'syn':['carefully','warily']},
            {'word': 'dim', 'pos': 'adj', 'def': 'not bright', 'level': 'A2',
             'trans': {'es':'tenue','tr':'loş','fr':'tamis','sv':'dunkel'}, 'syn':['dark','faint']},
            {'word': 'eerie', 'pos': 'adj', 'def': 'strange and frightening', 'level': 'B2',
             'trans': {'es':'escalofriante','tr':'ürkütücü','fr':'étrange','sv':'kuslig'}, 'syn':['creepy','spooky']},
            {'word': 'engineered', 'pos': 'adj', 'def': 'designed or created', 'level': 'B2',
             'trans': {'es':'ingeniado','tr':'tasarlanmış','fr':'conçu','sv':'konstruerad'}, 'syn':['constructed','devised']},
            {'word': 'crafted', 'pos': 'adj', 'def': 'made carefully by hand', 'level': 'B2',
             'trans': {'es':'fabricado','tr':'ustalıkla yapılmış','fr':'fabriqué','sv':'hantverksmässigt'}, 'syn':['handmade','created']},
            {'word': 'atmosphere', 'pos': 'noun', 'def': 'feeling or mood', 'level': 'B1',
             'trans': {'es':'atmósfera','tr':'atmosfer','fr':'atmosphère','sv':'atmosfär'}, 'syn':['ambiance','environment']},
            {'word': 'curiosity', 'pos': 'noun', 'def': 'desire to know', 'level': 'B1',
             'trans': {'es':'curiosidad','tr':'merak','fr':'curiosité','sv':'nyfikenhet'}, 'syn':['inquisitiveness','interest']},
            {'word': 'terrified', 'pos': 'adj', 'def': 'extremely frightened', 'level': 'A2',
             'trans': {'es':'aterrorizado','tr':'dehşete düşmüş','fr':'terrifié','sv':'skräckslagen'}, 'syn':['horrified','panicked']},
        ]
        return self._create_words(english, words_data)

    def link_lab_words(self, story, vocab_map):
        examples = [
            ('secretive', 1, "Mia's father was very secretive about his work."),
            ('mysterious', 2, "The laboratory felt mysterious."),
            ('sinister', 3, "The laugh sounded sinister."),
            ('disturbing', 4, "The noise was disturbing."),
            ('cautiously', 5, "They cautiously opened the door."),
            ('dim', 6, "Only dim light lit the room."),
            ('eerie', 7, "An eerie atmosphere filled the basement."),
            ('engineered', 8, "Mia thought he engineered a monster."),
            ('crafted', 9, "He crafted a beautiful doll."),
            ('atmosphere', 10, "The room had a cold atmosphere."),
            ('curiosity', 11, "Curiosity drove the girls inside."),
            ('terrified', 12, "They were terrified by the laugh."),
        ]
        for word_text, order, example in examples:
            word = vocab_map.get(word_text)
            if word:
                StoryWord.objects.get_or_create(story=story, word=word, defaults={'example_sentence': example, 'order': order})

    # Yardımcı: kelime oluşturma
    def _create_words(self, language, words_data):
        created = {}
        for w in words_data:
            word, _ = Word.objects.get_or_create(
                language=language,
                word=w['word'],
                defaults={'part_of_speech': w['pos'], 'definition': w['def'], 'difficulty_level': w['level']}
            )
            # Translations
            for code, trans in w['trans'].items():
                target_lang = Language.objects.get(code=code)
                WordTranslation.objects.get_or_create(word=word, target_language=target_lang, defaults={'translation': trans})
            # Synonyms
            for syn in w['syn']:
                syn_word, _ = Word.objects.get_or_create(
                    language=language, word=syn,
                    defaults={'part_of_speech': w['pos'], 'definition': f'Synonym of {w["word"]}', 'difficulty_level': w['level']}
                )
                WordSynonym.objects.get_or_create(word=word, synonym=syn_word)
            created[w['word']] = word
            self.stdout.write(f'    ✅ Word: {word.word}')
        return created

    # ------------------------------------------------------------
    # Quizzes
    # ------------------------------------------------------------
    def create_quiz_rabbit(self, story):
        quiz, _ = Quiz.objects.get_or_create(story=story, version_type='original',
                                             defaults={'title': 'The Clever Rabbit Quiz', 'is_premium': False})
        questions = [
            ('Where did the lion live?', 'in a large green forest'),
            ('Why were the animals afraid?', 'He killed many animals every day'),
            ('What deal did they make?', 'One animal would come to him each day'),
            ("Whose turn came after many days?", 'the rabbit'),
            ('Why did the rabbit walk slowly?', 'Because he had a plan'),
            ('What did the rabbit tell about the other lion?', 'that he claimed to be the true king'),
            ('Where did the rabbit lead the lion?', 'to an old stone well'),
            ('What did the lion see in the water?', 'his own reflection'),
            ('Did the lion recognize himself?', 'No'),
            ('What happened to the lion at the end?', 'He jumped into the well and never returned'),
        ]
        for i, (text, correct) in enumerate(questions, 1):
            QuizQuestion.objects.get_or_create(quiz=quiz, order=i,
                defaults={'question_text': text, 'correct_answer': correct, 'question_type': 'fill_blank'})
        self.stdout.write(f'  ✅ Quiz for Rabbit: {quiz.questions.count()} questions')

    def create_quiz_laboratory(self, story):
        quiz, _ = Quiz.objects.get_or_create(story=story, version_type='original',
                                             defaults={'title': 'Laboratory Mystery Quiz', 'is_premium': False})
        questions = [
            ('Where was the laboratory?', 'basement'),
            ('What did Mia hear one evening?', 'a laugh'),
            ("Who was Mia's best friend?", 'Liz'),
            ('Did the girls find the door locked?', 'No'),
            ('What smell filled the laboratory?', 'chemicals'),
            ('What did Mia imagine was inside?', 'a monster'),
            ('Who rushed in after Mia screamed?', 'her father'),
            ('What was actually making the sound?', 'a doll'),
            ('Why did her father make the doll?', 'for her birthday'),
            ('Did Mia feel relieved at the end?', 'Yes'),
        ]
        for i, (text, correct) in enumerate(questions, 1):
            QuizQuestion.objects.get_or_create(quiz=quiz, order=i,
                defaults={'question_text': text, 'correct_answer': correct, 'question_type': 'fill_blank'})
        self.stdout.write(f'  ✅ Quiz for Laboratory: {quiz.questions.count()} questions')

    # ------------------------------------------------------------
    # Update demo user
    # ------------------------------------------------------------
    def update_user_progress(self, user, rabbit_story, lab_story, all_vocab):
        # Save notebook entries (first 5 words from each)
        for word_name in list(all_vocab.keys())[:10]:
            word = all_vocab[word_name]
            UserWord.objects.get_or_create(
                user=user, language=word.language, word=word.word,
                defaults={'part_of_speech': word.part_of_speech, 'definition': word.definition,
                          'translation': f'Example: {word.word}', 'status': 'learning',
                          'times_reviewed': random.randint(0,2), 'ease_factor': 2.5,
                          'next_review_at': timezone.now() + timedelta(days=random.randint(1,5)),
                          'source_word': word}
            )
        # Progress for both stories
        for story in [rabbit_story, lab_story]:
            prog, _ = UserStoryProgress.objects.get_or_create(user=user, story=story)
            if not prog.completed:
                prog.completed = True
                prog.read_count = 1
                prog.time_spent_seconds = 900 if story == rabbit_story else 720
                prog.save()
        # Global stats
        user_prog, _ = UserProgress.objects.get_or_create(user=user)
        user_prog.total_stories_read = (user_prog.total_stories_read or 0) + 2
        user_prog.total_xp = (user_prog.total_xp or 0) + 300
        user_prog.last_active_date = timezone.now().date()
        user_prog.save()
        # Daily activity
        today = timezone.now().date()
        act, _ = DailyActivity.objects.get_or_create(user=user, date=today)
        act.stories_read = (act.stories_read or 0) + 2
        act.xp_earned = (act.xp_earned or 0) + 300
        act.minutes_spent = (act.minutes_spent or 0) + 27
        act.save()
        self.stdout.write('  ✅ Demo user updated: +2 stories, +300 XP, +10 notebook words')
