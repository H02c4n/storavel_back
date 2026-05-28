# apps/stories/management/commands/seed_swedish.py
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
    help = 'Fyll databasen med två svenska berättelser: Lejonet & kaninen + Laboratoriet'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🌱 Fyller databasen med svenska berättelser: Lejonet & Kaninen + Laboratoriet...'))

        # 1. Språk
        self.create_languages()

        # 2. Demoanvändare
        demo_user = self.create_users()

        # 3. Taggar
        tags = self.create_tags()

        # 4. Lejonet och kaninen
        rabbit_story = self.create_rabbit_lion_story(demo_user, tags)

        # 5. Laboratorieberättelsen
        lab_story = self.create_laboratory_story(demo_user, tags)

        # 6. Ordlistor för båda berättelserna
        vocab_rabbit = self.create_vocabulary_rabbit()
        vocab_lab = self.create_vocabulary_laboratory()
        all_vocab = {**vocab_rabbit, **vocab_lab}

        # 7. Länka ord till berättelser
        self.link_rabbit_words(rabbit_story, vocab_rabbit)
        self.link_lab_words(lab_story, vocab_lab)

        # 8. Quiz
        self.create_quiz_rabbit(rabbit_story)
        self.create_quiz_laboratory(lab_story)

        # 9. Uppdatera demoanvändaren
        self.update_user_progress(demo_user, rabbit_story, lab_story, all_vocab)

        self.stdout.write(self.style.SUCCESS('✅ Svenska seedningen slutförd!'))
        self.stdout.write(f'   📖 Lejonet och kaninen: /stories/{rabbit_story.slug}')
        self.stdout.write(f'   📖 Laboratoriet:        /stories/{lab_story.slug}')

    # ------------------------------------------------------------
    # Hjälpfunktion: språk
    # ------------------------------------------------------------
    def create_languages(self):
        swedish, _ = Language.objects.get_or_create(
            code='sv',
            defaults={'name': 'Swedish', 'native_name': 'Svenska', 'flag_emoji': '🇸🇪',
                      'script': 'latin', 'rtl': False, 'has_romanization': False,
                      'is_active': True, 'order': 1}
        )
        self.stdout.write(f'  ✅ Språk: Svenska')
        for code in ['en', 'tr', 'es', 'fr']:
            Language.objects.get_or_create(code=code)

    def create_users(self):
        demo, created = User.objects.get_or_create(
            email='demo@storavel.com',
            defaults={'username': 'demo_user', 'display_name': 'Demoanvändare',
                      'is_premium': False, 'is_active': True}
        )
        if created:
            demo.set_password('demo123')
            demo.save()
            UserSettings.objects.get_or_create(user=demo)
            self.stdout.write('  ✅ Demoanvändare skapad (demo@storavel.com / demo123)')
        else:
            self.stdout.write('  ⚠️ Demoanvändare finns redan')
        return demo

    def create_tags(self):
        tag_names = [
            'listig', 'kanin', 'lejon', 'fabel', 'visdom', 'mod', 'slughet',  # kanin
            'laboratorium', 'mysterium', 'docka', 'rädsla', 'nyfikenhet', 'familj', 'överraskning', 'födelsedag'  # lab
        ]
        tags = []
        for name in tag_names:
            tag, _ = StoryTag.objects.get_or_create(name=name, defaults={'slug': slugify(name)})
            tags.append(tag)
        self.stdout.write(f'  ✅ {len(tags)} storytaggar skapade')
        return tags

    # ------------------------------------------------------------
    # Berättelse: Lejonet och den listiga kaninen
    # ------------------------------------------------------------
    def create_rabbit_lion_story(self, user, tags):
        swedish = Language.objects.get(code='sv')
        story, created = Story.objects.get_or_create(
            slug='lejonet-och-den-listiga-kaninen',
            defaults={
                'language': swedish,
                'title': "Lejonet och den listiga kaninen",
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
            story.tags.set([t for t in tags if t.name in ['listig','kanin','lejon','fabel','visdom','mod','slughet']])
            self.stdout.write('  ✅ Berättelse: Lejonet och den listiga kaninen')

        versions = {
            'original': """I en skog levde ett grymt lejon. Varje dag dödade och åt han många djur. De andra djuren var rädda för att lejonet skulle döda dem alla.

Djuren sa till lejonet:
”Låt oss göra en överenskommelse. Om du lovar att bara äta ett djur per dag, så kommer ett av oss till dig varje dag. Då behöver du inte jaga oss.”

Planen lät bra för lejonet, så han gick med på den. Men han sa också:
”Om ni inte kommer varje dag, lovar jag att döda er alla nästa dag!”

Varje dag gick ett djur till lejonet så att han kunde äta det. De andra djuren var då säkra.

Till slut var det kaninens tur. Kaninen gick mycket långsamt den dagen, så lejonet blev arg när den äntligen kom.

Lejonet frågade argt:
”Varför är du sen?”

”Jag gömde mig från ett annat lejon i skogen. Han sa att han är kungen, så jag blev rädd.”

Lejonet sa:
”Jag är den enda kungen här! Ta mig till det andra lejonet!”

Kaninen svarade:
”Jag visar gärna var han bor.”

Kaninen ledde lejonet till en gammal brunn i skogen. Brunnen var djup med vatten längst ner.

”Titta där nere,” sa kaninen. ”Lejonet bor där nere.”

När lejonet tittade ner i brunnen såg han sin egen spegelbild i vattnet. Han trodde att det var det andra lejonet. Han hoppade ner i brunnen och kom aldrig upp igen.

Alla andra djur i skogen blev mycket glada över kaninens smarta trick.""",

            'nutid': """Ett grymt lejon lever i skogen och rör sig mellan träden varje dag. Hans tassar trycker ner mossa och löv, och alla djur hör hans tunga steg långt innan han syns.

Han jagar och äter många djur varje dag. Skogen känns spänd, nästan som om den håller andan. Fåglarna flyger tystare än vanligt, och de mindre djuren gömmer sig i sina hålor.

Djuren samlas till slut och pratar nervöst med lejonet. De föreslår en överenskommelse. Rösterna skakar lite när de säger det.

Lejonet lyssnar, tänker, och hans ögon smalnar. Han går till slut med på planen, men hans röst är mörk och hotfull: han ska straffa dem om de inte kommer.

Varje dag fortsätter samma mönster. Ett djur går långsamt genom skogen, känner doften av jord och rädsla, och går till lejonet.

Till slut är det kaninens tur. Kaninen hoppar mellan rötter och stenar men är mycket långsam. Hjärtat slår snabbt.

När den kommer fram ryter lejonet irriterat. Luften känns varm av hans ilska.

Kaninen berättar om ett annat lejon. Orden är noggrant valda, och lejonets uppmärksamhet skärps direkt.

De går tillsammans genom skogen till en gammal brunn. Luften där är kallare, fuktigare.

När lejonet tittar ner ser han en annan "fiende". Han ryter och kastar sig fram.

Plötsligt försvinner han ner i mörkret.

Skogen blir tyst. Sedan börjar djuren långsamt förstå att faran är borta.""",

            'dåtid': """Det fanns en gång ett grymt lejon som levde i skogen. Jag minns hur hela området kändes tungt när jag tänker tillbaka på det.

Lejonet dödade många djur varje dag. Alla var rädda, hela tiden. Det var som om ingen kunde andas fritt.

Till slut föreslog djuren en plan. De bad lejonet att bara äta ett djur om dagen. Lejonet gick med på det, men han hotade dem också.

Varje dag gick ett djur till honom. Det var alltid någon som gick sin sista väg genom skogen.

Till slut var det kaninens tur. Jag minns hur långsamt den gick, nästan som om den visste att något viktigt skulle hända.

Lejonet blev arg när kaninen kom sent. Hans röst ekade mellan träden.

Kaninens berättelse om ett annat lejon var listig. Lejonet trodde på det direkt.

De gick till brunnen. När lejonet tittade ner, såg han sin egen spegelbild.

Han trodde det var en fiende och hoppade.

Jag minns att allt blev tyst efteråt.

Sedan kändes skogen annorlunda. Lättare. Friare.""",

            'framtid': """Det kommer att finnas ett grymt lejon i skogen. Han kommer att röra sig genom träden varje dag och alla djur kommer att vara rädda.

Han ska fortsätta jaga, och skogen kommer att kännas osäker och spänd.

Djuren kommer att prata tillsammans och de kommer att föreslå en plan. De kommer att hoppas att lejonet ska acceptera den.

Lejonet kommer att gå med på överenskommelsen, men han kommer också att hota dem om de inte följer den.

Varje dag kommer ett djur att gå till honom. Det kommer att kännas tungt och nervöst.

Till slut kommer kaninen att få sin tur. Den kommer att gå långsamt, kanske för att den tänker mycket.

Lejonet kommer att bli arg när den kommer sent.

Kaninen kommer att berätta om ett annat lejon. Det kommer att låta övertygande.

De kommer att gå till en brunn. Lejonet kommer att titta ner.

Han kommer att se något han tror är en fiende.

Och han kommer att hoppa.

Efteråt kommer skogen att bli tystare och tryggare.""",

            'ordförråd': """Berättelse med rikt ordförråd

Ett grymt lejon härskade i en tät skog och spred skräck bland alla djur. Hans aptit var enorm, och hans hänsynslösa beteende skapade ständig panik.

De skrämda djuren förhandlade till slut med lejonet. De föreslog en kompromiss: ett djur skulle frivilligt gå till lejonet varje dag om han slutade jaga slumpmässigt.

Först verkade upplägget rimligt.

Men när kaninens tur kom, tänkte det lilla djuret ut en briljant strategi. Istället för att ge upp hjälplöst manipulerade kaninen lejonets arrogans och lockade honom till en djup brunn.

När lejonet misstog sin egen spegelbild för en rival, hoppade han impulsivt ner i vattnet och försvann för alltid.

Kaninens uppfinningsrikedom räddade hela skogen.

Ordförrådstabell:
- Grym: Extremt elak och våldsam
- Härskade: Styrde fullständigt
- Hänsynslös: Grym och utan skrupler
- Förhandlade: Diskuterade för att nå en överenskommelse
- Kompromiss: En uppgörelse mellan två parter
- Tänkte ut: Planerade smart
- Manipulerade: Styrde på ett listigt sätt
- Arrogans: Överdriven stolthet
- Impulsivt: Handlade utan att tänka
- Uppfinningsrikedom: Kreativ intelligens

Synonymer:
Arg → ilsken, rasande, vred, upprörd, förbannad
Listig → smart, slug, intelligent, fyndig, klurig
Rädd → skrämd, livrädd, nervös, orolig, förskräckt

Användbara fraser:
- ”Bländad av stolthet” (för stolt för att tänka klart)
- ”Tänka snabbt” (agera intelligent i stunden)
- ”En överlevnadsfråga” (nödvändigt för att leva)""",

            'modersmål': """Alltså, det där lejonet i skogen… han var verkligen inget att leka med. Varje dag gick han runt där som om hela skogen var hans egen lilla matsal.

Djuren var livrädda, såklart. Ingen vågade ens knäcka en kvist utan att få panik.

Till slut bara: ”Nej men nu får det vara nog”, och de gick till lejonet och snackade ihop sig om en deal.

Lejonet gick med på det, men han var ju inte direkt någon snäll typ. Han sa typ: ”Kommer ni inte, då är det kört för er allihop.”

Så det rullade på så där ett tag. Ett djur i taget… inte direkt någon drömgrej.

Sen kommer kaninen. Och den där lilla rackaren… den är sen. Lejonet blir skogstokig.

Och kaninen bara kör på med den här historien om ett annat lejon. Och lejonet köper det rakt av, såklart.

De går till brunnen… och ja, du kan ju gissa vad som händer. Boom.

Slut på lejonproblem.""",

            'dialog': """A: Alltså… det här lejonet i skogen, det var helt galet.
B: Ja, verkligen. Alla djuren var ju skiträdda.
A: Precis! Och de bara ”vi måste hitta en lösning”.
B: Och lejonet bara ”okej, men annars… då är det kört”.
A: Exakt.

B: Så varje dag skickade de ett djur.
A: Inte så kul jobb direkt…
B: Nej, verkligen inte.

A: Men sen kom kaninen.
B: Ja, och den var sen också va?
A: Ja! Lejonet blev ju helt galen.

B: Och då hittar kaninen på den här grejen om ett annat lejon…
A: Ärligt talat, rätt smart alltså.
B: Ja, det kan man verkligen säga.

A: Och lejonet går på det!
B: Men hallå? Hur dum får man vara?
A: Haha, precis.

B: Och sen… brunnen.
A: Japp. Och boom, slut på det.""",

            'idiom': """Kaninen lyckades verkligen bryta isen mellan sig själv och lejonet genom att lugnt inleda en dialog.

De andra djuren hade länge varit på helspänn, eftersom de visste att varje dag kunde vara deras sista.

Lejonet trodde att han hade full kontroll, men i själva verket var han ute på djupt vatten när han följde kaninen.

Kaninen och lejonet var i samma båt på väg mot brunnen, även om de hade helt olika mål.

När lejonet hoppade ner i brunnen, var det som att han inte längre hittade sin plats i verkligheten.

Idiomlista:
- Bryta isen (börja prata och minska spänning)
- På helspänn (mycket nervös och vaksam)
- Ute på djupt vatten (i en situation man inte behärskar)
- Sitta i samma båt (ha samma situation)
- Hitta sin plats (förstå sin roll eller position)""",

            'känslor': """Skogen var aldrig tyst egentligen. Inte riktigt. Men den kändes tyst när lejonet gick där.

Varje steg han tog bar på rädsla. Inte bara hos djuren, utan i själva luften.

Djuren levde med en ständig klump i magen. De visste aldrig vem som skulle försvinna nästa dag.

När de föreslog planen fanns det både hopp och skam i deras röster. Hopp, för att något kanske kunde förändras. Skam, för att någon alltid skulle offras.

Och kaninen… den lilla kroppen som gick genom skogen den dagen bar på något större än sig själv. En blandning av rädsla och beslutsamhet.

När lejonet stirrade ner i brunnen fanns ett ögonblick av total tystnad. Ett val som kändes evigt, fast det bara var en sekund.

Och sedan… fallet.

Efteråt var det som om skogen drog ett djupt andetag för första gången på länge. Lättnad, men också ett eko av allt som hänt.""",

            'frågor_svar': """Det finns ett lejon i skogen, eller hur?
Ja, det finns ett lejon i skogen.

Är lejonet snällt?
Nej, lejonet är inte snällt. Han är grym, eller hur? Ja, han är grym.

Äter lejonet många djur?
Ja, han äter många djur varje dag.

Är djuren glada eller rädda?
De är rädda. Väldigt rädda.

Pratar djuren med lejonet?
Ja, de pratar med lejonet. De gör en överenskommelse, eller hur? Ja.

Kommer ett djur till lejonet varje dag?
Ja, ett djur kommer varje dag.

Är det roligt för djuren?
Nej, det är inte roligt.

Kommer kaninen till slut?
Ja, kaninen kommer till slut.

Är kaninen snabb den dagen?
Nej, kaninen är långsam. Väldigt långsam.

Blir lejonet glad eller arg?
Han blir arg! Ja, han blir arg.

Berättar kaninen om ett annat lejon?
Ja, kaninen berättar om ett annat lejon.

Tror lejonet på det?
Ja, han tror på det. Han tror att det är sant.

Går lejonet till brunnen?
Ja, han går till brunnen.

Ser lejonet sig själv i vattnet?
Ja, han ser sig själv.

Hoppar lejonet i brunnen?
Ja, han hoppar i brunnen.

Kommer lejonet upp igen?
Nej, han kommer inte upp igen.

Blir djuren glada?
Ja, de blir mycket glada!

Slut?
Ja, det är slut."""
        }

        for vtype, content in versions.items():
            StoryVersion.objects.get_or_create(story=story, version_type=vtype, defaults={'content': content})
            self.stdout.write(f'    ✅ Version: {vtype}')
        UserStoryProgress.objects.get_or_create(user=user, story=story, defaults={'completed': False})
        return story

    # ------------------------------------------------------------
    # Berättelse: Hemligheten i laboratoriet
    # ------------------------------------------------------------
    def create_laboratory_story(self, user, tags):
        swedish = Language.objects.get(code='sv')
        story, created = Story.objects.get_or_create(
            slug='hemligheten-i-laboratoriet',
            defaults={
                'language': swedish,
                'title': "Hemligheten i laboratoriet",
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
            story.tags.set([t for t in tags if t.name in ['laboratorium','mysterium','docka','rädsla','nyfikenhet','familj','överraskning','födelsedag']])
            self.stdout.write('  ✅ Berättelse: Hemligheten i laboratoriet')

        versions = {
            'original': """Mias pappa hade ett laboratorium hemma i källaren. Mia visste nästan ingenting om det. Varje gång hennes pappa gick in där stängde och låste han dörren noggrant. Hon visste bara att han arbetade med olika projekt för sitt jobb. Men han berättade aldrig vad projekten handlade om.

En kväll gick Mia långsamt fram till dörren till laboratoriet. Hon stannade och tänkte:
”Jag undrar vilken galen uppfinning han arbetar med nu.”

Plötsligt hörde hon ett högt ljud. Det lät som ett ondskefullt skratt. Mia blev rädd och skyndade sig tillbaka till sitt rum.

Nästa kväll kom hennes vän Liz hem till henne. När Liz kom berättade Mia om det märkliga ljudet från natten innan.
”Det var hemskt,” sa Mia nervöst.

”Varför går vi inte in och tittar?” frågade Liz. ”Det kan bli ett spännande äventyr!”

Mia kände sig osäker, men hon gick med på planen. Som vanligt var dörren låst. Flickorna väntade tills Mias pappa gick ut ur laboratoriet för att äta middag.

”Han låste inte dörren!” viskade Liz. ”Kom!”

Laboratoriet var mörkt och kallt. Flickorna gick försiktigt nerför trappan. Mia kände en stark lukt av konstiga kemikalier i luften. Hon började undra vad hennes pappa egentligen skapade där nere.

Plötsligt hörde de det hemska skrattet igen. Det lät ännu värre än kvällen innan. Mia blev livrädd. Tänk om det fanns ett monster där inne?

Hon skrek efter hjälp.

Mias pappa sprang snabbt in i rummet och tände lamporna.
”Åh nej,” sa han. ”Nu har ni upptäckt min hemlighet.”

”Ditt monster försökte döda oss!” sa Mia.

”Monster?” frågade han förvånat. ”Menar du den här?”

Han höll upp en vacker docka. Dockan skrattade högt. Nu lät skrattet inte längre ondskefullt.

”Jag gjorde den till din födelsedag,” sa han vänligt. ”Jag ville ge den till dig senare, men du kan få den redan nu. Jag hoppas att du tycker om den.”

Mia log lättat och kramade dockan.""",

            'nutid': """Mia står framför den stängda dörren till laboratoriet. Ljuset från korridoren faller svagt över det gamla träet, och hon känner hur hjärtat slår lite snabbare. Hennes pappa är där inne igen. Precis som alltid har han låst dörren.

Inifrån hörs dova ljud. Metall som skrapar mot metall. Ett svagt surrande. Något bubblar.

Mia lutar huvudet mot dörren.
”Vad håller han egentligen på med?” tänker hon.

Luften känns kall i korridoren. Hon drar armarna runt kroppen. Plötsligt hörs ett högt skratt från laboratoriet.
Ett mörkt, konstigt skratt.

Mia hoppar till.
Det känns som om hela huset blir tyst efter ljudet. Hon stirrar på dörren några sekunder innan hon snabbt springer tillbaka till sitt rum. Hon försöker intala sig själv att det bara är en maskin. Eller kanske en radio. Men innerst inne känner hon oro.

Nästa kväll kommer Liz hem till henne. Liz slänger av sig jackan och sätter sig på sängen medan Mia berättar allt.
”Alltså, det lät verkligen hemskt,” säger Mia och gnuggar händerna nervöst mot varandra.

Liz spärrar upp ögonen.
”Det här måste vi undersöka.”
”Va? Nej…”
”Jo! Tänk om han bygger en robot. Eller gömmer ett monster där nere.”

Mia skrattar nervöst, men magen knyter sig ändå.

De väntar i köket tills Mias pappa lämnar laboratoriet för att äta middag. När han går därifrån märker Liz något direkt.
”Dörren är öppen.”

Flickorna tittar på varandra.
Sedan smyger de in.

Laboratoriet är mörkt och luktar starkt av kemikalier och varm elektronik. Små lampor blinkar i olika färger. Det känns nästan som att gå in i en annan värld.

Trappan knarrar under deras fötter.
Mia känner hur händerna blir kalla.
”Jag gillar inte det här,” viskar hon.

Plötsligt hörs skrattet igen.
Högre.
Närmare.

Mia fryser till.
I hennes huvud dyker skrämmande bilder upp. Hon föreställer sig ett monster med långa armar och glödande ögon som gömmer sig i mörkret.

Hon kan inte kontrollera rädslan längre.
”HJÄLP!”

Sekunder senare rusar hennes pappa in och tänder lamporna.
Det starka ljuset fyller rummet.

Och där, mitt på arbetsbordet, sitter en liten docka.
Dockan skrattar.

Mias pappa håller upp den försiktigt och ler lite generat.
”Jag byggde den åt dig,” säger han.

Mia känner hur all rädsla försvinner. Hon börjar skratta åt sig själv medan värmen sprider sig genom kroppen.""",

            'dåtid': """När Mia tänkte tillbaka på den kvällen mindes hon först tystnaden i huset. Det hade varit sent, och hela korridoren utanför laboratoriet hade legat i mörker. Hon hade stått framför dörren och funderat över varför hennes pappa alltid höll rummet hemligt.

Sedan hade hon hört skrattet.
Det hade skurit genom huset som en kall vind.

Hon hade blivit så rädd att hon nästan tappade andan innan hon sprang tillbaka till sitt rum. Hela natten hade hon legat vaken och tänkt på ljudet. Ju mer hon tänkte på det, desto farligare hade det låtit i hennes huvud.

När Liz kom nästa kväll hade Mia äntligen berättat allt.
Liz hade först skrattat, men sedan blivit nyfiken.
”Vi måste gå in där,” hade hon sagt med glänsande ögon.

Mia hade egentligen inte velat, men samtidigt hade hon varit desperat efter svar.

När dörren oväntat stod olåst hade det känts som om huset självt bjöd in dem.

Laboratoriet hade varit kallare än resten av huset. Luften hade luktat metall och kemikalier. Skuggorna hade dansat längs väggarna medan flickorna försiktigt gått nerför trappan.

Sedan hade skrattet kommit tillbaka.
Det hade varit ännu värre där nere.

Mia hade känt paniken växa i bröstet. Hon hade varit säker på att något hemskt gömde sig i mörkret.

Så hon hade skrikit.
Och när hennes pappa tänt lamporna hade sanningen varit nästan komisk.

Inget monster.
Ingen galen vetenskapsman.
Bara en docka med ett mekaniskt skratt.

Efteråt hade Mia känt sig både lättad och lite generad. Men mest av allt hade hon känt sig älskad. Hennes pappa hade trots allt arbetat i hemlighet för att göra en speciell present till henne.

Det var den delen hon kom ihåg starkast flera år senare.""",

            'framtid': """I morgon kväll kommer Mia förmodligen att stå framför laboratoriedörren igen. Hon kommer att höra märkliga ljud där inifrån och börja undra vad hennes pappa egentligen arbetar med.

Hon kommer antagligen att tänka:
”Nu gör han säkert ännu ett galet experiment.”

Sedan kommer ett skratt att eka genom huset. Ett högt och obehagligt skratt som kommer att få henne att frysa till av rädsla.

Hon kommer snabbt att gå tillbaka till sitt rum, men hon kommer inte att kunna sluta tänka på ljudet.

Nästa dag ska hennes vän Liz komma på besök. När Mia berättar om skrattet kommer Liz direkt att bli nyfiken.
”Vi kommer att undersöka det där,” kommer Liz att säga självsäkert.

Mia kommer tveka först, men till slut kommer hon ändå att följa med.

De kommer att vänta tills hennes pappa lämnar laboratoriet för middag. När de märker att dörren är olåst kommer de försiktigt att smyga in.

Laboratoriet kommer att kännas mörkt och mystiskt. Flickorna kommer att känna lukten av kemikalier och höra maskiner surra svagt i bakgrunden.

Mia kommer att bli mer och mer nervös.

Och plötsligt kommer skrattet tillbaka.
Det kommer låta så skrämmande att Mia nästan kommer börja gråta. Hon kommer tro att ett monster gömmer sig där nere.

Till slut kommer hon att ropa på hjälp.

Hennes pappa kommer då att springa in och tända lamporna. Han kommer att se förvånad ut när han inser att flickorna upptäckt hans hemlighet.

Sedan kommer han att visa dockan han har byggt.

Mia kommer först känna sig generad över sin rädsla, men sedan kommer hon bli varm och glad när hon förstår att dockan egentligen är en födelsedagspresent skapad med kärlek.""",

            'ordförråd': """Berättelse med rikt ordförråd

Mias pappa hade ett mystiskt laboratorium i husets källare. Dörren var alltid låst, och det väckte Mias nyfikenhet. Hon grubblade ofta över vad han egentligen sysslade med där inne.

En kväll hörde hon ett kusligt skratt bakom dörren. Ljudet var så obehagligt att hon blev skärrad och rusade tillbaka till sitt rum.

När hennes vän Liz fick höra om händelsen blev hon genast ivrig att undersöka saken. Tillsammans smög de ner i laboratoriet där luften var fylld av stickande kemiska dofter och svagt blinkande maskiner.

Plötsligt hördes skrattet igen, och Mia blev övertygad om att något fruktansvärt väntade i mörkret.

Men sanningen visade sig vara helt annorlunda.
Det skrämmande ljudet kom från en mekanisk docka som hennes pappa hade byggt som födelsedagspresent.

Ordförrådstabell:
- Mystisk: hemlighetsfull, svår att förstå
- Grubblade: tänkte djupt och länge
- Kuslig: skrämmande på ett obehagligt sätt
- Skärrad: plötsligt rädd eller chockad
- Ivrig: mycket entusiastisk
- Stickande: stark och skarp lukt eller känsla
- Övertygad: helt säker på något

Synonymgrupper:
Rädd → rädd, skrämd, livrädd, vettskrämd, skärrad
Hemlig → hemlig, dold, mystisk, okänd, förborgad
Gå försiktigt → smyga, tassa, gå ljudlöst, försiktigt närma sig

Användbara fraser:
- ”Väcka någons nyfikenhet” (göra någon intresserad av att veta mer)
- ”Frysa till av rädsla” (bli helt stilla på grund av rädsla)
- ”Visa sig vara” (avslöjas som)

Kontextuella exempel:
Mia blev misstänksam eftersom dörren alltid var låst.
Liz var modigare än Mia och ville utforska laboratoriet.
Det dunkla ljuset gjorde rummet ännu mer skrämmande.
Pappans hemlighet var egentligen kärleksfull och oskyldig.""",

            'modersmål': """Alltså, Mia hade alltid tyckt att hennes pappas laboratorium var lite creepy. Det låg nere i källaren bakom en tung dörr som alltid var låst. Och hennes pappa? Han var superhemlig med allt där inne.

Varje gång han gick ner dit hördes konstiga ljud. Metall som slog mot nåt. Maskiner som surrade. Ibland mumlade han för sig själv också.

Och en kväll hörde Mia något som verkligen fick henne att stelna till.
Ett skratt.
Inte ett vanligt skratt heller, utan ett sånt där överdrivet, nästan filmskurk-aktigt skratt.

Hon bara: ”Nej nope, jag går och lägger mig.”

Dagen efter berättade hon allt för Liz.
Liz älskade ju sånt där.
”Men hallå, vi måste ju kolla!”
”Måste vi verkligen?”
”Ja! Tänk om han bygger nån hemlig robot eller nåt.”

Så de väntade tills hennes pappa gick upp för att äta middag. Och för första gången hade han glömt att låsa dörren.

Båda stod helt tysta några sekunder.
Sen gick de in.

Och alltså… stämningen där nere? Helt sjuk.
Det luktade kemikalier och varm plast. Små lampor blinkade överallt. Det såg ut som en blandning mellan ett science fiction-labb och nåns väldigt kaotiska garage.

Liz försökte spela cool.
Mia? Inte riktigt lika cool.

Sen hörde de skrattet igen.
Högre den här gången.

Mia fick total panik och skrek rakt ut.
Hennes pappa kom rusande nerför trappan och tände lamporna.

Och där stod han… med en docka i händerna.
Dockan skrattade.

Det blev helt tyst.
”Eh… det här är din födelsedagspresent,” sa han lite försiktigt.

Och Mia kände sig typ världens dummaste och lyckligaste person samtidigt.""",

            'dialog': """Liz: Alltså, du såg verkligen rädd ut igår. Vad hände egentligen?
Mia: Du vet laboratoriet som pappa alltid låser?
Liz: Ja?
Mia: Jag stod utanför dörren och då hörde jag världens läskigaste skratt.
Liz: Nej, vad säger du?
Mia: Jo! Det lät som en galen skurk i en skräckfilm.
Liz: Okej, det där måste vi undersöka.
Mia: Men hallå? Tänk om det faktiskt finns något där inne!
Liz: Precis därför måste vi gå ner.
Mia: Ärligt talat känns det här som en dålig idé.
Liz: Det kan man verkligen säga… men också en rolig idé.
Mia: Oj då… dörren är öppen.
Liz: Jaha, och då?
Mia: Då betyder det att vi faktiskt kan gå in.
Liz: Kom nu!
(de går nerför trappan)
Mia: Det luktar jättekonstigt här nere.
Liz: Ja… typ kemikalier eller nåt.
Mia: Hör du det där?
Dockan: HAHAHAHA!
Mia: AAH! Hjälp!
Liz: Men lugna dig!
(Mias pappa springer in)
Pappan: Vad händer här?!
Mia: Ditt monster försökte döda oss!
Pappan: Monster? Nä, det är bara dockan.
Liz: Vänta… den där dockan skrattade alltså?
Pappan: Ja. Jag byggde den till Mias födelsedag.
Mia: Va… seriöst?
Pappan: Självklart.
Liz: Alltså, det här blev mycket mindre läskigt nu.""",

            'idiom': """Mia hade länge känt att något inte stod rätt till med hennes pappas laboratorium. Han höll korten nära kroppen och ville aldrig avslöja vad han arbetade med där inne. Ju mer han försökte hålla allt hemligt, desto mer växte hennes nyfikenhet.

En kväll, när hon stod utanför dörren, hörde hon ett skratt som fick henne att gå på helspänn. Det lät som om någon där inne hade tappat greppet om verkligheten.

När Liz fick höra historien ville hon genast ge sig in i leken.
”Kom igen,” sa hon. ”Vi sitter ju i samma båt nu.”

Mia kände sig ute på djupt vatten, men hon följde ändå med. När dörren råkade stå olåst såg Liz sin chans.

Nere i laboratoriet var stämningen tät. Det luktade kemikalier och gamla maskiner. Flickorna försökte bryta isen genom att skämta lite med varandra, men nervositeten låg hela tiden i luften.

Sedan hördes skrattet igen.
Nu tappade Mia nästan fotfästet helt. Hon var övertygad om att något hemskt väntade runt hörnet.

Men när hennes pappa tände lamporna föll bitarna på plats.
Det visade sig att allt handlade om en docka som han byggt åt henne. Han hade bara försökt ge henne en speciell överraskning.

Efteråt kunde Mia äntligen andas ut. Hela situationen hade egentligen varit ett stort missförstånd.

Idiomlista:
- Hålla korten nära kroppen (vara hemlighetsfull)
- Gå på helspänn (vara mycket nervös)
- Sitta i samma båt (vara i samma situation)
- Vara ute på djupt vatten (vara i en svår situation)
- Bryta isen (minska spänningen)
- Fall på plats (bli tydligt och begripligt)""",

            'känslor': """Huset var tyst den kvällen.
Inte en varm och trygg tystnad, utan en sådan som fick Mia att känna sig ensam trots att hennes pappa fanns bara några meter bort.

Hon stod framför laboratoriedörren och stirrade på handtaget. Ljuset från korridoren darrade svagt över golvet. Bakom dörren hördes maskiner arbeta, som om något levde där inne.

Hennes pappa brukade alltid le mot henne vid middagen. Men den senaste tiden hade han varit disträ, nästan frånvarande. Han försvann ner i laboratoriet varje kväll och kom tillbaka flera timmar senare med trötta ögon och kemikalielukt på händerna.

Mia började undra om han höll på att glida längre bort från henne.

Sedan kom skrattet.
Det skar genom mörkret och fick hennes hjärta att stanna till.

Hon sprang tillbaka till sitt rum och drog täcket över sig, men ljudet ekade fortfarande i huvudet. Hon försökte vara modig, men rädslan växte i henne under hela natten.

När Liz kom nästa dag försökte Mia låta lugn när hon berättade om det som hänt. Men hennes händer darrade fortfarande lite.
”Vi tar reda på sanningen,” sa Liz mjukt.
De orden gav Mia mod.

När de senare smög ner i laboratoriet kändes varje steg tungt. Luften var kall och fylld av främmande lukter. Skuggorna såg nästan levande ut.

Och så hörde de skrattet igen.
Den här gången kände Mia paniken explodera inom sig.
Tänk om hennes pappa hade skapat något farligt?
Tänk om hon inte längre kände personen som bodde i samma hus som henne?

”Hjälp!” skrek hon.

Sekunder senare badade rummet i ljus.
Hennes pappa stod där andfådd och orolig.
Och i hans händer låg ingen maskin för förstörelse.
Ingen fara.
Bara en docka.
En docka som skrattade.

Mia såg på sin pappa. För första gången på flera dagar såg hon värmen i hans ögon igen.
”Jag ville göra något speciellt åt dig,” sa han tyst.

Och i det ögonblicket förstod Mia något viktigt.
Hennes pappa hade aldrig varit långt borta.
Han hade bara försökt skapa något med kärlek.""",

            'frågor_svar': """Mia har en pappa.
Har Mia en pappa? Ja, självklart har Mia en pappa.
Har Mia en hund? Nej, nej. Inte en hund. Hon har en pappa.

Mias pappa har ett laboratorium.
Har han ett laboratorium eller ett kök? Precis! Ett laboratorium.
Är laboratoriet öppet hela tiden? Nej. Det är låst.
Låser pappan dörren? Ja, just det. Han låser dörren.

Vet Mia vad som finns där inne? Nej, hon vet inte.
Är Mia nyfiken? Ja! Väldigt nyfiken.

En kväll står Mia utanför dörren.
Står hon utanför dörren eller under sängen? Exakt. Utanför dörren.
Hör hon ett skratt? Ja!
Är skrattet gulligt? Nej, nej. Det låter läskigt.

Blir Mia lugn? Nej. Hon blir rädd.
Springer hon till köket? Inte till köket, utan till sitt rum.

Nästa dag kommer Liz.
Kommer Liz eller hennes lärare? Precis! Liz kommer.
Berättar Mia om skrattet? Ja, det gör hon.

Vill Liz undersöka laboratoriet? Självklart!
Är Liz modig? Ja. Väldigt modig.
Är Mia lite nervös? Ja, just det.

Flickorna väntar.
Väntar de på bussen? Nej. De väntar på att pappan ska lämna laboratoriet.
Är dörren låst? Nej! Den är öppen.
Går flickorna in? Ja, exakt.

Är laboratoriet ljust? Nej, det är mörkt.
Luktar det gott? Inte direkt. Det luktar kemikalier.
Hör de skrattet igen? Ja!

Blir Mia rädd igen? Ja, väldigt rädd.
Ropar hon på hjälp? Precis! Hon skriker på hjälp.
Kommer hennes pappa springande? Ja, just det.
Tänder han lampan? Ja.

Finns det ett monster där inne? Nej, nej! Inget monster.
Vad finns där? En docka!
Skrattar dockan? Ja, exakt.
Är dockan en födelsedagspresent? Ja! Självklart.
Blir Mia glad till slut? Precis. Hon blir glad och lättad."""
        }

        for vtype, content in versions.items():
            StoryVersion.objects.get_or_create(story=story, version_type=vtype, defaults={'content': content})
            self.stdout.write(f'    ✅ Version: {vtype}')
        UserStoryProgress.objects.get_or_create(user=user, story=story, defaults={'completed': False})
        return story

    # ------------------------------------------------------------
    # Ordlista för Kaninberättelsen (12 ord)
    # ------------------------------------------------------------
    def create_vocabulary_rabbit(self):
        swedish = Language.objects.get(code='sv')
        words_data = [
            {'word': 'grym', 'pos': 'adj', 'def': 'extremt elak och våldsam', 'level': 'B1',
             'trans': {'en':'ferocious','es':'feroz','tr':'vahşi','fr':'féroce'}, 'syn':['elak','brutal']},
            {'word': 'härska', 'pos': 'verb', 'def': 'styra fullständigt', 'level': 'B1',
             'trans': {'en':'dominate','es':'dominar','tr':'egemen olmak','fr':'dominer'}, 'syn':['behärska','regera']},
            {'word': 'hänsynslös', 'pos': 'adj', 'def': 'grym och utan skrupler', 'level': 'B2',
             'trans': {'en':'ruthless','es':'despiadado','tr':'acımasız','fr':'impitoyable'}, 'syn':['obarmhärtig','skoningslös']},
            {'word': 'förhandla', 'pos': 'verb', 'def': 'diskutera för att nå en överenskommelse', 'level': 'B1',
             'trans': {'en':'negotiate','es':'negociar','tr':'pazarlık etmek','fr':'négocier'}, 'syn':['diskutera','medla']},
            {'word': 'kompromiss', 'pos': 'noun', 'def': 'ömsesidig uppgörelse', 'level': 'B2',
             'trans': {'en':'compromise','es':'compromiso','tr':'uzlaşma','fr':'compromis'}, 'syn':['uppgörelse','medling']},
            {'word': 'tänka ut', 'pos': 'verb', 'def': 'planera smart', 'level': 'B2',
             'trans': {'en':'devise','es':'idear','tr':'tasarlamak','fr':'concevoir'}, 'syn':['uppfinna','formulera']},
            {'word': 'arrogans', 'pos': 'noun', 'def': 'överdriven stolthet', 'level': 'B2',
             'trans': {'en':'arrogance','es':'arrogancia','tr':'kibir','fr':'arrogance'}, 'syn':['högfärd','övermod']},
            {'word': 'impulsiv', 'pos': 'adj', 'def': 'handlar utan att tänka', 'level': 'B2',
             'trans': {'en':'impulsive','es':'impulsivo','tr':'düşüncesiz','fr':'impulsif'}, 'syn':['hastig','ogenomtänkt']},
            {'word': 'uppfinningsrikedom', 'pos': 'noun', 'def': 'kreativ intelligens', 'level': 'C1',
             'trans': {'en':'ingenuity','es':'ingenio','tr':'zekâ','fr':'ingéniosité'}, 'syn':['fyndighet','påhittighet']},
            {'word': 'listig', 'pos': 'adj', 'def': 'smart på ett slugt sätt', 'level': 'A2',
             'trans': {'en':'clever','es':'listo','tr':'akıllı','fr':'intelligent'}, 'syn':['slug','smart']},
            {'word': 'livrädd', 'pos': 'adj', 'def': 'extremt rädd', 'level': 'A2',
             'trans': {'en':'terrified','es':'aterrorizado','tr':'dehşete düşmüş','fr':'terrifié'}, 'syn':['skräckslagen','panikslagen']},
            {'word': 'spegelbild', 'pos': 'noun', 'def': 'bild i vatten eller spegel', 'level': 'A2',
             'trans': {'en':'reflection','es':'reflejo','tr':'yansıma','fr':'reflet'}, 'syn':['återspegling','bild']},
        ]
        return self._create_words(swedish, words_data)

    def link_rabbit_words(self, story, vocab_map):
        examples = [
            ('grym', 1, 'Det grymma lejonet terroriserade skogen.'),
            ('härska', 2, 'Lejonet härskade över alla djur.'),
            ('hänsynslös', 3, 'Hans hänsynslösa beteende skrämde alla.'),
            ('förhandla', 4, 'Djuren förhandlade med lejonet.'),
            ('kompromiss', 5, 'De nådde en kompromiss för att överleva.'),
            ('tänka ut', 6, 'Kaninen tänkte ut en smart plan.'),
            ('arrogans', 7, 'Lejonets arrogans ledde till hans undergång.'),
            ('impulsiv', 8, 'Han tog ett impulsivt beslut att hoppa.'),
            ('uppfinningsrikedom', 9, 'Kaninens uppfinningsrikedom räddade skogen.'),
            ('listig', 10, 'Kaninen var listig och modig.'),
            ('livrädd', 11, 'Djuren var livrädda för lejonet.'),
            ('spegelbild', 12, 'Lejonet attackerade sin egen spegelbild.'),
        ]
        for word_text, order, example in examples:
            word = vocab_map.get(word_text)
            if word:
                StoryWord.objects.get_or_create(story=story, word=word, defaults={'example_sentence': example, 'order': order})

    # ------------------------------------------------------------
    # Ordlista för Laboratorieberättelsen (12 ord)
    # ------------------------------------------------------------
    def create_vocabulary_laboratory(self):
        swedish = Language.objects.get(code='sv')
        words_data = [
            {'word': 'mystisk', 'pos': 'adj', 'def': 'hemlighetsfull, svår att förstå', 'level': 'B1',
             'trans': {'en':'mysterious','es':'misterioso','tr':'gizemli','fr':'mystérieux'}, 'syn':['gåtfull','dold']},
            {'word': 'grubbla', 'pos': 'verb', 'def': 'tänka djupt och länge', 'level': 'B1',
             'trans': {'en':'ponder','es':'reflexionar','tr':'derin düşünmek','fr':'méditer'}, 'syn':['funder','begrunda']},
            {'word': 'kuslig', 'pos': 'adj', 'def': 'skrämmande på ett obehagligt sätt', 'level': 'B2',
             'trans': {'en':'eerie','es':'escalofriante','tr':'ürkütücü','fr':'sinistre'}, 'syn':['obehaglig','otäck']},
            {'word': 'skärrad', 'pos': 'adj', 'def': 'plötsligt rädd eller chockad', 'level': 'B2',
             'trans': {'en':'startled','es':'asustado','tr':'irkilmiş','fr':'effrayé'}, 'syn':['chockad','förskräckt']},
            {'word': 'ivrig', 'pos': 'adj', 'def': 'mycket entusiastisk', 'level': 'B1',
             'trans': {'en':'eager','es':'entusiasta','tr':'hevesli','fr':'impatient'}, 'syn':['angelägen','spänd']},
            {'word': 'stickande', 'pos': 'adj', 'def': 'stark och skarp lukt eller känsla', 'level': 'B2',
             'trans': {'en':'pungent','es':'punzante','tr':'keskin','fr':'âcre'}, 'syn':['skarp','brännande']},
            {'word': 'övertygad', 'pos': 'adj', 'def': 'helt säker på något', 'level': 'B1',
             'trans': {'en':'convinced','es':'convencido','tr':'ikna olmuş','fr':'convaincu'}, 'syn':['säker','förvissad']},
            {'word': 'smyga', 'pos': 'verb', 'def': 'gå tyst och försiktigt', 'level': 'A2',
             'trans': {'en':'sneak','es':'escabullirse','tr':'sinsice gitmek','fr':'se faufiler'}, 'syn':['tassa','lisma']},
            {'word': 'dunkel', 'pos': 'adj', 'def': 'svagt upplyst, mörk', 'level': 'A2',
             'trans': {'en':'dim','es':'tenue','tr':'loş','fr':'tamis'}, 'syn':['mörk','skum']},
            {'word': 'försiktig', 'pos': 'adj', 'def': 'noggrant för att undvika fara', 'level': 'A2',
             'trans': {'en':'cautious','es':'cauteloso','tr':'dikkatli','fr':'prudent'}, 'syn':['varsam','aktsam']},
            {'word': 'nyfikenhet', 'pos': 'noun', 'def': 'önskan att veta', 'level': 'B1',
             'trans': {'en':'curiosity','es':'curiosidad','tr':'merak','fr':'curiosité'}, 'syn':['vetgirighet','intresse']},
            {'word': 'lättnad', 'pos': 'noun', 'def': 'känsla när oro försvinner', 'level': 'B1',
             'trans': {'en':'relief','es':'alivio','tr':'rahatlama','fr':'soulagement'}, 'syn':['befrielse','tröst']},
        ]
        return self._create_words(swedish, words_data)

    def link_lab_words(self, story, vocab_map):
        examples = [
            ('mystisk', 1, 'Mias pappa var mystisk med sitt arbete.'),
            ('grubbla', 2, 'Mia grubblade över vad som fanns där inne.'),
            ('kuslig', 3, 'Skrattet lät kusligt.'),
            ('skärrad', 4, 'Mia blev skärrad av ljudet.'),
            ('ivrig', 5, 'Liz var ivrig att gå in.'),
            ('stickande', 6, 'En stickande lukt fyllde laboratoriet.'),
            ('övertygad', 7, 'Mia var övertygad om att det fanns ett monster.'),
            ('smyga', 8, 'Flickorna smög nerför trappan.'),
            ('dunkel', 9, 'Endast dunkelt ljus lyste rummet.'),
            ('försiktig', 10, 'De var försiktiga när de öppnade dörren.'),
            ('nyfikenhet', 11, 'Nyfikenhet drev flickorna in.'),
            ('lättnad', 12, 'Mia kände stor lättnad till slut.'),
        ]
        for word_text, order, example in examples:
            word = vocab_map.get(word_text)
            if word:
                StoryWord.objects.get_or_create(story=story, word=word, defaults={'example_sentence': example, 'order': order})

    # Hjälpfunktion: skapa ord
    def _create_words(self, language, words_data):
        created = {}
        for w in words_data:
            word, _ = Word.objects.get_or_create(
                language=language,
                word=w['word'],
                defaults={'part_of_speech': w['pos'], 'definition': w['def'], 'difficulty_level': w['level']}
            )
            # Översättningar
            for code, trans in w['trans'].items():
                target_lang = Language.objects.get(code=code)
                WordTranslation.objects.get_or_create(word=word, target_language=target_lang, defaults={'translation': trans})
            # Synonymer
            for syn in w['syn']:
                syn_word, _ = Word.objects.get_or_create(
                    language=language, word=syn,
                    defaults={'part_of_speech': w['pos'], 'definition': f'Synonym till {w["word"]}', 'difficulty_level': w['level']}
                )
                WordSynonym.objects.get_or_create(word=word, synonym=syn_word)
            created[w['word']] = word
            self.stdout.write(f'    ✅ Ord: {word.word}')
        return created

    # ------------------------------------------------------------
    # Quiz
    # ------------------------------------------------------------
    def create_quiz_rabbit(self, story):
        quiz, _ = Quiz.objects.get_or_create(story=story, version_type='original',
                                             defaults={'title': 'Lejonet och kaninen - Quiz', 'is_premium': False})
        questions = [
            ('Var bodde lejonet?', 'i en skog'),
            ('Varför var djuren rädda?', 'Han dödade många djur varje dag'),
            ('Vilken överenskommelse gjorde de?', 'Ett djur skulle komma till honom varje dag'),
            ('Vems tur kom efter många dagar?', 'kaninens'),
            ('Varför gick kaninen långsamt?', 'För att han hade en plan'),
            ('Vad berättade kaninen om det andra lejonet?', 'att han påstod sig vara den sanna kungen'),
            ('Vart ledde kaninen lejonet?', 'till en gammal brunn'),
            ('Vad såg lejonet i vattnet?', 'sin egen spegelbild'),
            ('Kände lejonet igen sig själv?', 'Nej'),
            ('Vad hände med lejonet till slut?', 'Han hoppade i brunnen och kom aldrig upp'),
        ]
        for i, (text, correct) in enumerate(questions, 1):
            QuizQuestion.objects.get_or_create(quiz=quiz, order=i,
                defaults={'question_text': text, 'correct_answer': correct, 'question_type': 'fill_blank'})
        self.stdout.write(f'  ✅ Quiz för Kaninen: {quiz.questions.count()} frågor')

    def create_quiz_laboratory(self, story):
        quiz, _ = Quiz.objects.get_or_create(story=story, version_type='original',
                                             defaults={'title': 'Laboratoriemysteriet - Quiz', 'is_premium': False})
        questions = [
            ('Var låg laboratoriet?', 'källaren'),
            ('Vad hörde Mia en kväll?', 'ett skratt'),
            ('Vem var Mias bästa vän?', 'Liz'),
            ('Var dörren låst när flickorna gick in?', 'Nej'),
            ('Vilken lukt fyllde laboratoriet?', 'kemikalier'),
            ('Vad trodde Mia fanns där inne?', 'ett monster'),
            ('Vem kom inspringande efter att Mia skrek?', 'hennes pappa'),
            ('Vad var det som egentligen lät?', 'en docka'),
            ('Varför hade pappan gjort dockan?', 'till hennes födelsedag'),
            ('Kände Mia lättnad till slut?', 'Ja'),
        ]
        for i, (text, correct) in enumerate(questions, 1):
            QuizQuestion.objects.get_or_create(quiz=quiz, order=i,
                defaults={'question_text': text, 'correct_answer': correct, 'question_type': 'fill_blank'})
        self.stdout.write(f'  ✅ Quiz för Laboratoriet: {quiz.questions.count()} frågor')

    # ------------------------------------------------------------
    # Uppdatera demoanvändaren
    # ------------------------------------------------------------
    def update_user_progress(self, user, rabbit_story, lab_story, all_vocab):
        # Lägg till anteckningar (första 10 orden)
        for word_name in list(all_vocab.keys())[:10]:
            word = all_vocab[word_name]
            UserWord.objects.get_or_create(
                user=user, language=word.language, word=word.word,
                defaults={'part_of_speech': word.part_of_speech, 'definition': word.definition,
                          'translation': f'Exempel: {word.word}', 'status': 'learning',
                          'times_reviewed': random.randint(0,2), 'ease_factor': 2.5,
                          'next_review_at': timezone.now() + timedelta(days=random.randint(1,5)),
                          'source_word': word}
            )
        # Framsteg för båda berättelserna
        for story in [rabbit_story, lab_story]:
            prog, _ = UserStoryProgress.objects.get_or_create(user=user, story=story)
            if not prog.completed:
                prog.completed = True
                prog.read_count = 1
                prog.time_spent_seconds = 900 if story == rabbit_story else 720
                prog.save()
        # Global statistik
        user_prog, _ = UserProgress.objects.get_or_create(user=user)
        user_prog.total_stories_read = (user_prog.total_stories_read or 0) + 2
        user_prog.total_xp = (user_prog.total_xp or 0) + 300
        user_prog.last_active_date = timezone.now().date()
        user_prog.save()
        # Daglig aktivitet
        today = timezone.now().date()
        act, _ = DailyActivity.objects.get_or_create(user=user, date=today)
        act.stories_read = (act.stories_read or 0) + 2
        act.xp_earned = (act.xp_earned or 0) + 300
        act.minutes_spent = (act.minutes_spent or 0) + 27
        act.save()
        self.stdout.write('  ✅ Demoanvändare uppdaterad: +2 berättelser, +300 XP, +10 anteckningsord')
