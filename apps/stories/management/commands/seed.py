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
    help = 'Seed the database with stories'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🌱 Seeding combined stories'))

        # 1. Language
        self.create_languages()

        # 2. Demo user
        demo_user = self.create_users()

        # 3. Tags
        tags = self.create_tags()

        # 4. Stories
        rabbit_story = self.create_rabbit_lion_story(demo_user, tags)
        lab_story = self.create_laboratory_story(demo_user, tags)
        dog_bell_story = self.create_dog_bell_story(demo_user, tags)

        # 5. Vocabulary for both stories
        vocab_rabbit = self.create_vocabulary_rabbit()
        vocab_lab = self.create_vocabulary_laboratory()
        vocab_dog = self.create_vocabulary_dog()
        all_vocab = {**vocab_rabbit, **vocab_lab, **vocab_dog}

        # 6. Link words to stories
        self.link_rabbit_words(rabbit_story, vocab_rabbit)
        self.link_lab_words(lab_story, vocab_lab)
        self.link_dog_words(dog_bell_story, vocab_dog)

        # 7. Quizzes
        self.create_quiz_rabbit(rabbit_story)
        self.create_quiz_laboratory(lab_story)
        self.create_quiz_dog(dog_bell_story)

        # 8. Update demo user
        #self.update_user_progress(demo_user, rabbit_story, lab_story, all_vocab)

        self.stdout.write(self.style.SUCCESS('✅ Combined seeding completed!'))

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
            'clever', 'rabbit', 'lion', 'fable', 'wisdom', 'courage', 'trickery', 'dog', 'bell', 'fable', 'lesson', 'village', 'pride', 
            'misunderstanding', 'reputation', 'warning', 'irony',
            'laboratory', 'mystery', 'doll', 'fear', 'curiosity', 'family', 'surprise', 'birthday'
        ]
        tags = []
        for name in tag_names:
            tag, _ = StoryTag.objects.get_or_create(name=name, defaults={'slug': slugify(name)})
            tags.append(tag)
        self.stdout.write(f'  ✅ {len(tags)} story tags created')
        return tags

    # ------------------------------------------------------------
    # Stories
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
            'original': """Mia lived with her father in a quiet house. Her father was a scientist, and he had a laboratory in the basement. The laboratory door was always closed and locked. Whenever her father entered the room, he made sure nobody followed him inside.

Mia often wondered what her father was doing in there. He told her that he worked on important projects, but he never explained anything in detail. This made Mia even more curious.

One evening, Mia walked past the laboratory door. She paused and stared at it quietly.

"I wonder what strange experiment Dad is doing now," she thought.

Suddenly, a loud and frightening laugh came from inside the laboratory.

"Hahaha!"

The sound shocked Mia. Her heart raced, and she quickly hurried back to her bedroom.

The next day, Mia's best friend Liz came to visit. Mia immediately told her about the scary laugh she had heard.

"It sounded terrible," Mia explained nervously.

Liz's eyes widened with excitement. "Then we should investigate!" she said. "Maybe there's something mysterious inside."

Mia felt unsure. She knew her father would not want them entering the laboratory. Still, her curiosity grew stronger.

Later that evening, the girls watched carefully while Mia's father left the laboratory and went upstairs for dinner.

"He forgot to lock the door!" Liz whispered excitedly.

The girls slowly opened the door and stepped inside.

The laboratory was dark and cold. Shelves filled with bottles and strange tools surrounded them. A strong chemical smell floated through the air.

Mia's hands trembled slightly.

"What if Dad is creating something dangerous?" she whispered.

The girls carefully walked farther into the room.

Then suddenly—

"Hahaha!"

The terrible laugh echoed through the laboratory again.

The girls froze in fear.

Mia imagined a horrible monster hiding in the shadows. Panic filled her chest, and she screamed loudly for help.

Within seconds, Mia's father rushed into the room and turned on the lights.

"What happened?" he asked in surprise.

"Your monster tried to attack us!" Mia cried.

"Monster?" her father repeated, looking confused.

Then he picked up a beautiful doll from the worktable.

The doll laughed again.

"Hahaha!"

But now the laugh sounded cheerful instead of evil.

Mia's father smiled warmly.

"I made this doll for your birthday," he explained. "I wanted it to surprise you."

Mia looked at the doll and then started laughing at herself. Liz laughed too.

The laboratory suddenly didn't seem frightening anymore.""",

            'present': """Rain taps softly against the windows while Mia walks slowly through the hallway. The house feels unusually quiet tonight.

At the end of the hallway stands the laboratory door.

Closed.

Locked.

Mia stares at it curiously.

Her father spends hours inside that mysterious room every single day. Whenever he enters, he carefully locks the door behind him. He never explains what he's building or researching.

That secrecy makes Mia's imagination run wild.

Maybe he's inventing robots.

Maybe he's mixing dangerous chemicals.

Or maybe…

Maybe he's creating monsters.

Mia bites her lip nervously as she approaches the door.

"I wonder what he's doing in there right now," she whispers.

Suddenly—

A loud laugh explodes from inside the laboratory.

"Hahaha!"

The sound is deep, strange, and creepy.

Mia jumps backward in shock. Her heart pounds rapidly against her chest. Goosebumps spread across her arms.

"That definitely sounds evil," she thinks.

Without waiting another second, she rushes upstairs to her room and pulls the blanket tightly around herself.

The next evening, Liz arrives at the house carrying a backpack and a huge smile.

"What's wrong?" Liz asks immediately after seeing Mia's worried face.

Mia tells her everything.

"The laugh sounded terrifying," Mia explains. "I swear something horrible is in there."

Instead of looking frightened, Liz becomes excited.

"We should check it out!" she says eagerly.

"What? No way," Mia replies instantly.

But deep inside, Mia wants to know the truth too.

Later that night, the girls sit quietly near the stairs while Mia's father leaves the laboratory and heads toward the kitchen.

Then Liz notices something important.

"The door isn't locked."

The girls exchange nervous glances.

Slowly, they open the door.

Cold air drifts out from the dark basement laboratory. Strange shadows cover the walls. Glass bottles shine beneath dim lights, and the sharp smell of chemicals fills the room.

Mia feels her stomach tighten.

Every step sounds louder than normal.

Creak.

Creak.

Creak.

Then suddenly—

"Hahaha!"

The terrible laugh echoes through the darkness again.

Mia freezes completely.

Her imagination explodes with fear.

"What if there's a monster hiding down here?" she thinks desperately.

Panic takes over.

"HELP!" she screams.

Footsteps thunder down the stairs.

Mia's father bursts into the room and flips on the lights.

Bright light fills the laboratory instantly.

Mia points shakily toward the table.

"Your monster almost killed us!"

Her father blinks in confusion.

"Monster?"

Then he lifts a pretty doll into the air.

The doll laughs sweetly.

"Hahaha!"

Now the sound feels playful instead of terrifying.

Mia's father smiles softly.

"I made this for your birthday," he says kindly. "I wanted it to surprise you."

Mia exhales deeply and starts laughing in relief.

The scary laboratory suddenly feels warm and harmless.""",

            'past': """Years later, Mia still remembered the night she believed her father had created a monster in his laboratory.

At the time, she had been completely convinced something terrifying lived behind that locked door.

Her father had always kept the laboratory private. Every evening, he disappeared downstairs for hours, locking the door carefully behind him. Whenever Mia asked questions, he simply smiled and changed the subject.

Naturally, her curiosity had grown stronger and stronger.

Then one night, everything changed.

Mia had been walking quietly past the laboratory when she suddenly heard a strange laugh echo from inside.

It had sounded dark, unnatural, and frightening.

She had frozen instantly before running back to her room in fear.

The following evening, Mia told her best friend Liz about the experience.

Unlike Mia, Liz had seemed thrilled by the mystery.

"We have to investigate," Liz had insisted.

Mia had hesitated at first, but eventually curiosity overcame her fear.

That night, they waited patiently until Mia's father left the laboratory for dinner. To their surprise, he had forgotten to lock the door.

The girls had slowly stepped into the dark basement laboratory.

Mia still remembered the smell of chemicals in the air and the strange shadows stretching across the room. Every sound had felt dangerous.

Then they heard the laugh again.

Louder.

Scarier.

The girls had panicked immediately.

Mia truly believed a monster was hiding somewhere nearby. Terrified, she screamed for help.

Within moments, her father had rushed downstairs and turned on the lights.

Then the truth became clear.

There was no monster.

Only a beautiful doll sitting on the table.

The doll itself had been making the creepy laugh.

Her father explained that he had secretly been building the doll as a birthday present for Mia.

At first, Mia had felt embarrassed for imagining something so terrible. But soon she and Liz had laughed together about the misunderstanding.

Looking back, Mia realized something important that night:

Fear often becomes much bigger inside our imagination.""",

            'future': """One evening, Mia will walk slowly past her father's mysterious laboratory. The door will be closed as usual, and curiosity will begin growing inside her mind once again.

Her father will continue keeping the laboratory secret. He will never fully explain what he is creating inside, and this mystery will make Mia imagine all kinds of strange possibilities.

As she stands near the door, she will suddenly hear a loud and frightening laugh coming from inside.

The sound will send fear through her entire body.

She will quickly run back to her room, unable to stop thinking about it.

The next day, her friend Liz will come over to visit. After hearing the story, Liz will become excited instead of scared.

"We should go inside and investigate," Liz will suggest.

At first, Mia will hesitate, but eventually she will agree.

Later that evening, the girls will notice something surprising: Mia's father will leave the laboratory without locking the door.

The girls will slowly enter the dark basement room together.

Inside, they will smell strong chemicals and see strange scientific equipment everywhere. The atmosphere will feel cold and mysterious.

Then suddenly, the terrifying laugh will echo through the laboratory again.

Mia will panic.

She will imagine a dangerous monster hiding in the shadows, waiting to attack them.

Frightened, she will scream loudly for help.

Her father will rush into the laboratory and turn on the lights immediately.

Then he will reveal the truth.

The scary sound will not come from a monster at all.

Instead, it will come from a beautiful doll that he has secretly been creating for Mia's birthday.

In the end, the girls will laugh with relief, and Mia will learn that imagination can sometimes create fears much bigger than reality.""",

            'vocabulary': """Vocabulary-Rich Story

Mia's father maintained a secretive laboratory in the basement of their home. His mysterious behavior and constant privacy sparked Mia's curiosity.

One evening, Mia heard a sinister laugh emerging from behind the locked laboratory door. Terrified by the disturbing sound, she fled to her bedroom.

The following night, Mia and her adventurous friend Liz cautiously entered the dim laboratory after discovering the door unlocked.

Inside, strange chemical odors filled the air, and shadows stretched across the room, creating an eerie atmosphere.

When the horrifying laugh echoed once again, Mia became convinced that her father had engineered a dangerous creature.

However, the frightening mystery turned out to be harmless. The "monster" was simply a laughing doll her father had crafted as a birthday surprise.

Vocabulary Table:
- Secretive: Hiding information
- Mysterious: Difficult to understand
- Sinister: Evil or frightening
- Disturbing: Causing worry or fear
- Cautiously: Carefully to avoid danger
- Dim: Not bright
- Eerie: Strange and frightening
- Engineered: Designed or created
- Crafted: Made carefully by hand
- Atmosphere: Feeling or mood

Synonym Groups:
Scary → frightening, terrifying, creepy, horrifying, disturbing
Curious → interested, eager, inquisitive, fascinated, questioning
Secret → hidden, private, confidential, mysterious, concealed

Useful Phrases:
- "Run wild" (imagination becomes uncontrolled)
- "Jump out of your skin" (become extremely frightened suddenly)
- "All in her head" (imagined, not real)""",

            'native': """So Mia's dad has this laboratory in the basement, and honestly, it's the kind of room that automatically feels suspicious.

Like, the door is always locked.

Always.

And every time he goes in there, he acts super secretive about whatever he's working on.

Naturally, Mia's curiosity goes through the roof.

One night she's standing outside the lab thinking, "Okay… what weird experiment is he doing now?"

And then suddenly—

This creepy laugh comes from inside.

Not a normal laugh either. Like full-on horror movie laughter.

Mia freaks out and runs straight back to her room.

The next day her friend Liz comes over, and after hearing the story, Liz is immediately like, "We HAVE to go inside."

Classic brave friend behavior.

At first Mia's nervous, but eventually curiosity wins.

Later that night they notice Mia's dad leaves the lab door unlocked while he goes upstairs for dinner.

Big mistake.

The girls sneak downstairs into the lab, and the whole place feels terrifying. It's dark, smells like chemicals, and there are shadows everywhere.

Then they hear the laugh again.

Louder this time.

At this point Mia is 100% convinced there's some mutant monster hiding down there.

She screams for help.

Her dad comes running downstairs, flips on the lights, and looks completely confused.

Then he picks up this cute little doll.

The doll laughs again.

And suddenly the scary evil laugh just sounds… silly.

Turns out her dad had been secretly building the doll for Mia's birthday.

Honestly, that's kind of sweet.

And also a pretty good reminder that our imagination can make things WAY scarier than they really are.""",

            'dialog': """Sarah: Hey, have you heard the story about Mia and the laboratory?
Daniel: No, what happened?
Sarah: So Mia's dad had this secret laboratory in their basement.
Daniel: That already sounds creepy.
Sarah: Exactly! And he always kept the door locked.
Daniel: Okay yeah, I'd definitely be curious too.
Sarah: Same. One night Mia heard this terrifying laugh coming from inside.
Daniel: No way.
Sarah: Seriously. She got so scared she ran straight back to her room.
Daniel: Honestly, I would've done the same thing.
Sarah: Then the next day her friend Liz comes over.
Daniel: Let me guess… Liz wanted to investigate?
Sarah: Of course. She was like, "This will be fun!"
Daniel: That's always the person who gets everyone into trouble.
Sarah: Exactly! So later they realize Mia's dad forgot to lock the laboratory.
Daniel: Big mistake.
Sarah: Yep. They sneak inside, and the place is dark and smells like chemicals.
Daniel: That sounds like a horror movie already.
Sarah: Then suddenly they hear the evil laugh again.
Daniel: Nope. I'm leaving immediately.
Sarah: Mia basically panics and screams for help.
Daniel: So what was making the sound?
Sarah: A doll.
Daniel: Wait… seriously?
Sarah: Yep! Her dad made it for her birthday.
Daniel: That's actually really sweet.
Sarah: I know, right? They thought it was a monster the whole time.
Daniel: Honestly, imagination makes everything scarier.
Sarah: Exactly.""",

            'idioms': """Mia's father always kept his laboratory under wraps, which only made Mia more curious about what was going on behind the locked door.

One evening, Mia heard a sinister laugh coming from inside the laboratory, and it completely sent chills down her spine.

The next day, when her adventurous friend Liz arrived, she immediately suggested they get to the bottom of the mystery.

At first, Mia was hesitant, but eventually curiosity got the better of her.

When they discovered the laboratory door unlocked, the girls slipped inside quietly. The dark room, strange chemicals, and eerie shadows made Mia feel completely out of her depth.

Then the horrifying laugh echoed through the laboratory once again.

At that moment, Mia's imagination ran wild. She became convinced her father had created some kind of monster.

Panicking, she cried for help.

Seconds later, her father rushed in and cleared everything up. The terrifying sound had actually come from a birthday doll he had been working on for weeks.

In the end, the girls realized they had blown the whole thing out of proportion.

Idiom List:
- Under wraps (kept secret)
- Send chills down your spine (cause fear)
- Get to the bottom of (discover the truth)
- Get the better of someone (control someone emotionally)
- Out of her depth (in a difficult situation)
- Run wild (become uncontrolled)
- Clear things up (explain confusion)
- Blow out of proportion (exaggerate something)""",

            'emotional': """The laboratory door always made Mia uneasy.

Every evening, her father disappeared behind it, locking the door carefully before beginning his mysterious work downstairs. Mia never knew what he was creating, and somehow the silence made everything feel even more frightening.

The unknown filled her imagination with endless possibilities.

One cold evening, Mia stood quietly outside the laboratory door. The hallway lights were dim, and the house felt strangely still.

Then suddenly—

"Hahaha!"

A horrifying laugh burst through the silence.

Mia's entire body froze.

The sound felt unnatural, almost inhuman. Fear rushed through her chest so quickly she could barely breathe.

She ran back to her room, pulling the blanket tightly around herself as her mind filled with terrifying thoughts.

The next day, when Liz visited, Mia finally told someone what she had heard.

But while Mia felt afraid, Liz felt excited.

"We should go inside," Liz whispered with curiosity shining in her eyes.

Mia hesitated. Part of her wanted to refuse.

But another part desperately wanted answers.

That night, they noticed the laboratory door standing slightly open.

For a moment, both girls stood silently at the top of the stairs.

Then slowly, they stepped inside.

The basement felt cold and shadowy. Strange bottles lined the shelves, and the sharp smell of chemicals floated through the dark air.

Every small noise made Mia's heart beat faster.

Then the laugh came again.

Louder.

Closer.

"Hahaha!"

Fear exploded inside her.

In her mind, she imagined glowing eyes hidden in the darkness. She imagined terrible experiments and dangerous monsters waiting nearby.

Unable to control her panic anymore, Mia screamed for help.

Seconds later, her father rushed downstairs and turned on the lights.

Everything changed instantly.

There were no monsters.

No evil experiments.

Only a beautiful doll resting gently on the table.

The doll laughed again softly.

Mia stared in disbelief while her father smiled warmly.

"I made this for your birthday," he said quietly. "I wanted it to surprise you."

At that moment, Mia felt relief wash over her completely. Her fear disappeared, replaced by embarrassment, laughter, and love.

Sometimes the scariest monsters exist only inside our imagination.""",

            'qa': """Mia's father has a laboratory.
Does Mia's father have a laboratory? Yes, yes. He has a laboratory.
Is the laboratory always open? No, no. It is always locked.
Who locks the laboratory? Mia's father locks the laboratory.
Does Mia know what is inside? No. She does not know.
Is she curious? Yes! She is very curious.

One night, Mia hears a strange laugh.
Does Mia hear music? No, no. She hears a strange laugh.
Is the laugh friendly? No! It sounds scary.
Does Mia stay there calmly? No. She runs back to her room.

The next day, Liz visits Mia.
Who visits Mia? Liz visits Mia.
Does Mia tell Liz about the laugh? Yes, yes. She tells Liz everything.
Does Liz become scared? No. Liz becomes excited.
What does Liz want to do? She wants to enter the laboratory.

Later, Mia's father forgets to lock the door.
Is the door locked? No! The door is unlocked.
Do the girls go inside? Yes. They go inside carefully.
Is the laboratory bright? No, no. It is dark.
What do they smell? They smell strange chemicals.

Suddenly, they hear the laugh again.
Do they hear a dog barking? No. They hear the laugh again.
Is Mia afraid? Yes! She is terrified.
What does Mia think? She thinks there is a monster.
Does she scream for help? Yes, yes. She screams loudly.

Who comes into the laboratory? Mia's father comes in.
Does he turn on the lights? Yes. He turns on the lights.
What is making the laugh? A doll is making the laugh.
Is it really a monster? No, no. It is only a doll.
Why did Mia's father make the doll? Because it is a birthday present for Mia.
Is Mia happy at the end? Yes! She is very happy.
That's right. Exactly."""
        }

        for vtype, content in versions.items():
            StoryVersion.objects.get_or_create(story=story, version_type=vtype, defaults={'content': content})
            self.stdout.write(f'    ✅ Version: {vtype}')
        UserStoryProgress.objects.get_or_create(user=user, story=story, defaults={'completed': False})
        return story

    def create_dog_bell_story(self, user, tags):
        english = Language.objects.get(code='en')
        story, created = Story.objects.get_or_create(
            slug='the-dog-with-the-bell',
            defaults={
                'language': english,
                'title': "The Dog with the Bell",
                'level_min': 'A2',
                'level_max': 'B1',
                'story_type': 'narrative',
                'estimated_read_minutes': 12,
                'is_premium': False,
                'is_published': True,
                'order': 10,
            }
        )
        if created:
            story.tags.set(tags)
            self.stdout.write('  ✅ Story: The Dog with the Bell')

        # All versions extracted from the provided document
        versions = {
            'original': """John had a dog that behaved very badly. The dog often bit people, and this caused many problems in the village. John worried deeply because he knew this was not normal behavior for a dog. Whenever villagers saw the dog, they became nervous and tried to stay away from it.

Soon, everyone in the village knew about the dangerous dog. People stopped visiting John’s house because they were afraid of getting bitten. John tried many times to train the dog. He patiently taught him to stay calm and behave properly, but nothing seemed to work. John did not want to hurt or punish the dog, yet he had no idea how to solve the problem.

One day, a friend visited John to discuss the situation. During their conversation, the friend explained that the villagers were very concerned. Then he suggested an idea.

“Why don’t you tie a bell around your dog’s neck?” the friend asked. “That way, people will hear the dog coming and avoid him before he gets too close.”

John thought the suggestion was excellent. If people could hear the dog approaching, they would have enough time to move away safely.

Surprisingly, the dog enjoyed wearing the bell. Every time he walked through the streets, the bell rang loudly. People immediately looked at him when they heard the sound, and the dog mistakenly believed they admired him. The ringing bell made him feel proud and important.

One day, the dog met several other dogs in the village. He proudly showed off his bell, expecting them to be impressed and perhaps even jealous.

Instead, the other dogs laughed.

“You don’t understand,” one of them said. “People aren’t looking at you because they like you. They look at you because the bell warns them that you are nearby. They want to avoid you before you bite them.”

The dog was shocked. He had misunderstood the situation completely.

The story teaches us an important lesson: popularity is not always a good thing when people notice you for negative reasons.""",

            'present': """John lives in a quiet little village with narrow dirt roads, wooden fences, and small gardens full of flowers. But there is one thing in the village that makes everyone uncomfortable: John’s dog.

The dog is large, restless, and unpredictable. Whenever someone walks past John’s house, the dog growls deeply and suddenly rushes forward. Villagers tense up immediately when they see him. Some step back nervously. Others cross the street to avoid him.

John watches all of this with worry in his eyes.

“This has to stop,” he thinks.

Every day, John tries to train the dog. He speaks gently, pats his head, and gives commands in a calm voice.

“Stay calm.”
“Sit.”
“Don’t bite.”

But the dog doesn’t listen for long. The moment another person appears, excitement takes over again.

John feels frustrated but also sad. He loves his dog and doesn’t want to punish him harshly. He believes the dog can change somehow.

One afternoon, John’s friend arrives at his house. They sit outside while the evening wind moves softly through the trees.

“The villagers are worried,” the friend says carefully. “Honestly, people are scared to walk near your house.”

John lowers his head quietly.

Then the friend smiles slightly and says, “Why not put a bell around the dog’s neck? If people hear him coming, they can stay out of his way.”

John suddenly feels hopeful.

“That might actually work,” he says.

The next morning, John ties a shiny little bell around the dog’s neck. The bell jingles brightly every time the dog moves.

Jingle. Jingle. Jingle.

As the dog walks proudly through the village streets, heads turn immediately. Windows open. Children move aside. Villagers step away quickly.

But the dog misunderstands everything.

“They admire me,” he thinks happily.

The bell becomes his favorite thing. He walks with confidence now, almost like a king showing off a golden crown. He enjoys the sound echoing through the streets.

One sunny afternoon, he meets a group of other dogs near the market.

“Look at my bell,” he says proudly.

The other dogs stare for a moment… and then burst into laughter.

“That bell isn’t a decoration,” one dog explains. “It’s a warning.”

The proud smile slowly disappears from John’s dog’s face.

“A warning?” he asks quietly.

“Yes,” another dog says. “People hear the bell and avoid you because they’re afraid you’ll bite them.”

For the first time, the dog understands the truth. The attention he receives is not admiration. It is fear.

The bell still rings softly as he walks away, but now the sound feels very different.""",

            'past': """Years ago, John owned a dog that caused endless trouble in the village. The animal had a terrible habit of biting people without warning. Because of this, everyone became cautious whenever they passed near John’s home.

John remembered how embarrassed he had felt each time someone complained.

“I’m sorry,” he would say repeatedly. “I’m trying to train him.”

And he truly was trying.

He had spent many afternoons teaching the dog commands and rewarding calm behavior. He had spoken patiently and avoided harsh punishment because he believed anger would only make things worse. Still, nothing improved.

Eventually, the dog’s reputation spread throughout the entire village. People warned visitors about him. Children were told not to go near John’s property.

Then one evening, one of John’s friends visited him with an unusual suggestion.

“I spoke with the villagers,” the friend explained. “Everyone’s nervous around your dog. Why don’t you put a bell around his neck? At least people will hear him coming.”

At first, John hesitated. But the more he thought about it, the more reasonable the idea seemed.

The next day, he tied a small brass bell around the dog’s neck.

From that moment on, the village changed.

Whenever the dog walked down the road, the bell announced his arrival long before he appeared. The cheerful ringing echoed through the streets, and people quickly stepped aside.

Ironically, the dog loved the attention.

He had believed the villagers admired him. He proudly walked through town with his head held high, enjoying every glance and reaction.

But his confidence disappeared after meeting several dogs near the center of the village.

The other dogs laughed when they saw the bell.

“You really don’t understand, do you?” one of them had said.

The dog looked confused.

“The bell isn’t making you popular,” another dog explained. “It warns people to stay away from you.”

The truth hit him hard.

For the first time, he realized that attention and respect were not the same thing.

Years later, people in the village still remembered the story of the dog with the bell. And many of them repeated the lesson to their children:

Being noticed means nothing if people notice you for the wrong reasons.""",

            'future': """John will soon face a difficult problem in his peaceful village. His dog will continue biting people, and the villagers will become increasingly afraid. Every time the dog approaches someone, tension will fill the air.

John will worry constantly about the situation. He will try to train the dog with patience and kindness. He will teach commands repeatedly and hope for improvement, but the dog’s behavior will not change easily.

Eventually, the villagers will stop visiting John’s house altogether. Rumors about the dangerous dog will spread quickly from one neighbor to another.

One day, John’s friend will come to speak with him.

“The village is concerned,” the friend will explain seriously. “People need a way to protect themselves. You should put a bell around your dog’s neck.”

John will think carefully before agreeing.

“Yes,” he will finally say. “That may solve the problem.”

Soon afterward, the dog will begin wearing a shiny bell around his neck. Every step he takes will produce a bright jingling sound.

At first, the dog will enjoy it tremendously. Whenever people hear the bell, they will immediately turn their heads or step aside. The dog will mistakenly assume they admire him.

He will become proud and confident. He will parade through the streets believing he has become famous.

Later, he will meet several other dogs who will quickly understand the real reason for the bell.

They will laugh and explain the truth.

“People aren’t impressed by you,” they will tell him. “The bell simply warns them to stay away.”

At that moment, the dog’s confidence will disappear. He will finally realize that attention gained through fear is not real respect.

And perhaps, after understanding this painful truth, the dog will slowly begin to change.""",

            'vocabulary': """John owned an aggressive dog that frequently attacked villagers. The animal’s hostile behavior created anxiety throughout the community. Neighbors became reluctant to visit John because they feared being injured.

John felt troubled and desperate. He attempted to discipline and train the dog, hoping to correct its destructive habit. Despite his persistence and patience, the dog remained uncontrollable.

Eventually, one of John’s acquaintances proposed a practical solution: attaching a bell to the dog’s collar. The bell would function as a warning signal, allowing villagers to avoid dangerous encounters.

Ironically, the dog interpreted the villagers’ reactions incorrectly. He assumed the attention meant admiration and popularity. In reality, people merely wanted to protect themselves.

The other dogs later exposed the truth, forcing him to confront an uncomfortable reality about reputation and social perception.

Vocabulary Table:
- Aggressive: Ready to attack
- Reluctant: Unwilling or hesitant
- Discipline: To train or control behavior
- Persistence: Continued effort
- Encounter: A meeting, often unexpected
- Reputation: Public opinion about someone
- Admiration: Respect or approval
- Perception: Understanding or interpretation

Synonym Groups:
Bad Behavior → aggressive, hostile, violent, troublesome, dangerous
Popular → admired, respected, famous, well-liked, noticed
Avoid → escape, stay away from, keep distance from, evade, steer clear of

Useful Phrases:
- "Spread through the village" (news became known everywhere)
- "Stay away from" (avoid someone or something)
- "Get the wrong idea" (misunderstand a situation)""",

            'native': """So John had this dog, right? And honestly, the dog was kind of a menace.

Not cute-trouble. Not "he chews shoes" trouble.

No, this dog actually bit people.

And everybody in the village knew it.

If people saw the dog coming down the road, they’d instantly move out of the way like a car was speeding toward them. Nobody wanted to visit John anymore, which made things awkward because John was actually a pretty nice guy.

The worst part? He really tried to fix the problem.

He watched training videos, gave commands, stayed patient, tried rewards instead of punishment… nothing worked. The dog just kept acting wild anytime people got close.

Eventually, one of John’s friends sat him down and said, "Listen, man… the villagers are nervous. You need some kind of warning system."

"A warning system?"

"Yeah. Put a bell on the dog."

And weirdly enough… it worked.

The second people heard that little jingling sound, they’d clear the street immediately.

Problem solved.

Well… kind of.

Because the dog absolutely loved the bell.

He strutted around town like he was a celebrity. Every time heads turned, he thought, "Wow. People really notice me."

Meanwhile, people were basically running away from him.

Then one day he runs into a few other dogs, proudly showing off the bell like it’s some luxury accessory.

The other dogs start cracking up.

One of them finally says, "Buddy… you seriously don’t know why you’re wearing that thing?"

The dog’s tail slows down.

"They’re not looking at you because you’re special," the dog explains. "The bell tells people when to escape."

Ouch.

That one hit hard.

And honestly? That’s kind of how life works sometimes. Attention isn’t always admiration.

Sometimes people notice you because they’re trying to avoid you.""",

            'dialog': """Mike: Hey, did you hear about John’s dog?
Sarah: Oh, the one with the bell around his neck?
Mike: Yeah, exactly! Honestly, that dog used to bite everybody.
Sarah: No way. Seriously?
Mike: Seriously. People were actually scared to walk near John’s house.
Sarah: That makes sense. I’d avoid that place too.
Mike: Right? And John kept trying to train the dog, but nothing worked.
Sarah: Did he punish the dog?
Mike: Actually, no. He didn’t want to be cruel. He tried being patient instead.
Sarah: Huh. So where did the bell idea come from?
Mike: One of John’s friends suggested it. He said, "Put a bell on the dog so people can hear him coming."
Sarah: Honestly, that’s kind of smart.
Mike: Exactly. And the funny part is… the dog loved the bell.
Sarah: Wait, really?
Mike: Yeah! Every time people looked at him, he thought they admired him.
Sarah: Oh no…
Mike: I know. Then some other dogs finally told him the truth.
Sarah: Let me guess. People weren’t admiring him?
Mike: Nope. They were avoiding him.
Sarah: That’s brutal.
Mike: Yeah, but it’s a pretty good lesson though.
Sarah: Definitely. Being popular for bad reasons isn’t really popularity.""",

            'idioms': """John’s dog had become a real pain in the neck for the entire village. Everywhere the dog went, people were on edge because they never knew when he might snap and bite someone.

John bent over backward trying to solve the issue. He worked patiently with the dog day after day, hoping the animal would eventually turn over a new leaf. But no matter what he did, the dog simply wouldn’t change his ways.

Finally, one of John’s friends stepped in to lend a hand.

"The villagers asked me to talk to you," he explained. "People are tired of walking on eggshells around your dog. Why not put a bell around his neck so everyone can hear him coming?"

John thought the idea sounded reasonable, so he gave it a shot.

Soon, the bell became impossible to miss. Every time the dog strolled through town, villagers quickly cleared out. Problem solved.

Well… not exactly.

The dog completely got the wrong end of the stick.

Instead of realizing people feared him, he thought he had suddenly become popular. He strutted around proudly, convinced he was the talk of the town for all the right reasons.

Then reality hit him like a ton of bricks.

One afternoon, several dogs burst out laughing when they saw the bell.

"Buddy," one of them said, "that bell isn’t there to make you look good. It’s there so people can stay one step ahead of you."

The dog’s confidence collapsed instantly.

At that moment, he finally realized he wasn’t admired at all. People simply wanted to steer clear of trouble.

Idiom List:
- Pain in the neck (very annoying problem)
- On edge (nervous or anxious)
- Bend over backward (try very hard)
- Turn over a new leaf (change behavior positively)
- Lend a hand (help someone)
- Walk on eggshells (act carefully to avoid problems)
- Give it a shot (try something)
- Talk of the town (famous topic)
- Hit like a ton of bricks (affect someone strongly)
- Steer clear of (avoid)""",

            'emotional': """Every evening, as the sun disappeared behind the hills, John sat quietly outside his house watching his dog.

The village used to feel warm and welcoming. Children once played near his yard. Neighbors used to stop and chat. But slowly, everything changed.

Now people crossed the street when they saw his home.

Doors closed more quickly.

Smiles disappeared.

And every time his dog barked or lunged at someone, John felt a heavy weight inside his chest.

"I don’t know what to do anymore," he whispered one night.

He loved the dog. Despite everything, he truly did. He remembered when the animal had been small and harmless, sleeping peacefully beside the fireplace. Somewhere along the way, something had changed.

Still, John refused to give up on him.

When his friend suggested the bell, John felt both hope and sadness at the same time.

Hope — because maybe people would finally feel safe.

Sadness — because the bell would become a symbol of fear.

The first time the dog wore it, the soft jingling echoed through the streets like a warning carried by the wind.

Jingle. Jingle. Jingle.

Villagers stepped aside immediately.

The dog lifted his head proudly, unaware of the truth. For the first time in a long while, people noticed him everywhere he went.

And deep inside, he liked that feeling.

Maybe he had spent so much time feeling isolated that even fearful attention felt better than being ignored.

But truth has a strange way of finding us.

When the other dogs laughed at him, the sound cut deeper than he expected.

"They aren’t looking at you because they admire you," one dog said softly. "They’re afraid."

In that moment, the world suddenly felt quieter.

The bell still rang around his neck, but now every sound carried a different meaning.

Not popularity.

Not respect.

Just loneliness.

As he slowly walked home beneath the fading evening light, perhaps for the first time, the dog began to understand the pain he had caused others — and the emptiness hidden behind false attention.""",

            'qa': """John had a dog. Did John have a cat? No, no. He didn’t have a cat. He had a dog. That’s right. He had a dog.

Was the dog a good dog? No, no. The dog was not a good dog. The dog was a bad dog.

What did the dog do? Did the dog sing songs? No! The dog didn’t sing songs. The dog bit people. Yes, yes. The dog bit people frequently.

Did people like getting bitten? Of course not! People hated getting bitten.

Who worried about the dog? Did the villagers worry? Yes, they worried too. But especially John worried. That’s right. John was very concerned.

Did John try to teach the dog? Yes! He tried many times.

Did the dog learn? No, no. The dog did not learn.

Was John patient or angry? He was patient. Very patient.

Did patience work? No. It didn’t work.

Then John’s friend visited him. Did his enemy visit him? No! His friend visited him.

What did the friend suggest? Did he suggest buying a bicycle? No, no. He suggested putting a bell around the dog’s neck.

Why put a bell on the dog? To make music? Not exactly. The bell warned people. Yes. People could hear the dog coming.

Did John like the idea? Yes! He thought it was a great idea.

Now the dog wore a bell. Did the dog hate the bell? No! Surprisingly, the dog loved the bell.

Why did he love it? Because people looked at him.

Did the people look at him because they admired him? No, no. That’s the important part.

One day, the dog met other dogs. Did the other dogs cry? No. They laughed.

Why did they laugh?

Because the dog misunderstood everything!

The other dogs explained the truth.

"People hear the bell and avoid you," they said.

Did people avoid him because they loved him? Of course not! They avoided him because they were afraid he would bite him.

Did the dog finally understand? Yes. Finally, he understood.

And what is the lesson?

Being popular for bad reasons is not true popularity.

Exactly. That’s right."""
        }

        for vtype, content in versions.items():
            StoryVersion.objects.get_or_create(story=story, version_type=vtype, defaults={'content': content})
            self.stdout.write(f'    ✅ Version: {vtype}')

        # Mark progress as not completed for demo (or optional)
        UserStoryProgress.objects.get_or_create(user=user, story=story, defaults={'completed': False})
        return story

    # ------------------------------------------------------------
    # Vocabularies
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

    def create_vocabulary_dog(self):
        english = Language.objects.get(code='en')
        words_data = [
            {'word': 'aggressive', 'pos': 'adj', 'def': 'ready to attack', 'level': 'B1',
             'trans': {'es':'agresivo','tr':'saldırgan','fr':'agressif','sv':'aggressiv'}, 'syn':['hostile','violent']},
            {'word': 'reluctant', 'pos': 'adj', 'def': 'unwilling or hesitant', 'level': 'B1',
             'trans': {'es':'reacio','tr':'isteksiz','fr':'réticent','sv':'motvillig'}, 'syn':['hesitant','unwilling']},
            {'word': 'discipline', 'pos': 'verb', 'def': 'to train or control behavior', 'level': 'B1',
             'trans': {'es':'disciplinar','tr':'disipline etmek','fr':'discipliner','sv':'disciplinera'}, 'syn':['train','correct']},
            {'word': 'persistence', 'pos': 'noun', 'def': 'continued effort', 'level': 'B2',
             'trans': {'es':'persistencia','tr':'sebat','fr':'persistance','sv':'uthållighet'}, 'syn':['determination','tenacity']},
            {'word': 'encounter', 'pos': 'noun', 'def': 'an unexpected meeting', 'level': 'B1',
             'trans': {'es':'encuentro','tr':'karşılaşma','fr':'rencontre','sv':'möte'}, 'syn':['meeting','confrontation']},
            {'word': 'reputation', 'pos': 'noun', 'def': 'public opinion about someone', 'level': 'B1',
             'trans': {'es':'reputación','tr':'itibar','fr':'réputation','sv':'rykte'}, 'syn':['name','standing']},
            {'word': 'admiration', 'pos': 'noun', 'def': 'respect and approval', 'level': 'B2',
             'trans': {'es':'admiración','tr':'hayranlık','fr':'admiration','sv':'beundran'}, 'syn':['esteem','praise']},
            {'word': 'perception', 'pos': 'noun', 'def': 'understanding or interpretation', 'level': 'B2',
             'trans': {'es':'percepción','tr':'algı','fr':'perception','sv':'uppfattning'}, 'syn':['view','interpretation']},
            {'word': 'hostile', 'pos': 'adj', 'def': 'unfriendly and aggressive', 'level': 'B2',
             'trans': {'es':'hostil','tr':'düşmanca','fr':'hostile','sv':'fientlig'}, 'syn':['antagonistic','unfriendly']},
            {'word': 'anxiety', 'pos': 'noun', 'def': 'feeling of worry or fear', 'level': 'B1',
             'trans': {'es':'ansiedad','tr':'kaygı','fr':'anxiété','sv':'ångest'}, 'syn':['worry','unease']},
            {'word': 'misunderstand', 'pos': 'verb', 'def': 'fail to interpret correctly', 'level': 'A2',
             'trans': {'es':'malinterpretar','tr':'yanlış anlamak','fr':'mécomprendre','sv':'missförstå'}, 'syn':['misread','confuse']},
            {'word': 'popularity', 'pos': 'noun', 'def': 'state of being liked by many', 'level': 'B1',
             'trans': {'es':'popularidad','tr':'popülerlik','fr':'popularité','sv':'popularitet'}, 'syn':['fame','renown']},
        ]
        return self._create_words(english, words_data)

    # ------------------------------------------------------------
    # Linking words
    # ------------------------------------------------------------
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

    def link_dog_words(self, story, vocab_map):
        examples = [
            ('aggressive', 1, 'The aggressive dog scared everyone in the village.'),
            ('reluctant', 2, 'People were reluctant to walk past John’s house.'),
            ('discipline', 3, 'John tried to discipline the dog with patience.'),
            ('persistence', 4, 'Despite his persistence, the dog did not change.'),
            ('encounter', 5, 'Nobody wanted a dangerous encounter with the dog.'),
            ('reputation', 6, 'The dog developed a terrible reputation.'),
            ('admiration', 7, 'The dog mistakenly thought he earned admiration.'),
            ('perception', 8, 'His perception of the situation was wrong.'),
            ('hostile', 9, 'The dog’s hostile behavior caused anxiety.'),
            ('anxiety', 10, 'The villagers felt constant anxiety.'),
            ('misunderstand', 11, 'The dog completely misunderstood the attention.'),
            ('popularity', 12, 'His popularity was based on fear, not respect.'),
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

    def create_quiz_dog(self, story):
        quiz, _ = Quiz.objects.get_or_create(story=story, version_type='original',
                                             defaults={'title': 'The Dog with the Bell Quiz', 'is_premium': False})
        questions = [
            ('Who owned the dog?', 'John'),
            ('What problem did the dog cause?', 'bit people'),
            ('Were the villagers happy or afraid?', 'afraid'),
            ('Did John successfully train the dog?', 'No'),
            ('What did John’s friend suggest?', 'tie a bell around the dog’s neck'),
            ('Why put a bell on the dog?', 'to warn people'),
            ('Did the dog hate the bell?', 'No'),
            ('Why did the dog like the bell?', 'because people noticed him'),
            ('What did the other dogs tell him?', 'people avoid him because they are afraid'),
            ('What is the lesson of the story?', 'popularity for bad reasons is not true popularity'),
        ]
        for i, (text, correct) in enumerate(questions, 1):
            QuizQuestion.objects.get_or_create(quiz=quiz, order=i,
                defaults={'question_text': text, 'correct_answer': correct, 'question_type': 'fill_blank'})
        self.stdout.write(f'  ✅ Quiz: {quiz.questions.count()} questions')

    # ------------------------------------------------------------
    # Update demo user
    # ------------------------------------------------------------
    """ def update_user_progress(self, user, rabbit_story, lab_story, all_vocab):
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
        self.stdout.write('  ✅ Demo user updated') """
