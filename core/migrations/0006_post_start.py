"""Trzy startowe wpisy na blogu (wczesniej byly tylko zapowiedziami "Wkrotce" w szablonie).

Tresc do przejrzenia i edycji w panelu admina (Blog – wpisy). Zdjecia dodaje sie w panelu.
"""
import datetime

from django.db import migrations

POSTS = [
    {
        'title': 'Odprysk na szybie – naprawić czy wymienić?',
        'slug': 'odprysk-na-szybie-naprawic-czy-wymienic',
        'date': datetime.datetime(2026, 10, 1, 9, 0, tzinfo=datetime.timezone.utc),
        'excerpt': 'Kamień uderzył w szybę i została mała gwiazdka? Podpowiadamy, kiedy wystarczy naprawa, a kiedy trzeba wymienić szybę.',
        'content': '''Mały odprysk łatwo zlekceważyć, bo prawie go nie widać. Tylko że szyba cały czas pracuje. Nagrzewa się, stygnie, drga na dziurach. Zimą dochodzi różnica temperatur między ciepłym wnętrzem a mrozem na zewnątrz. Z małej gwiazdki potrafi z dnia na dzień zrobić się długie pęknięcie, a wtedy naprawa już nie wchodzi w grę.

## Kiedy da się naprawić

Zwykle wtedy, gdy:

- odprysk jest mały (mniej więcej jak moneta),
- nie jest tuż przy krawędzi szyby,
- nie jest na wprost oczu kierowcy,
- nie idą od niego jeszcze pęknięcia.

Zawsze oceniamy to na miejscu. Wystarczy podjechać albo wysłać nam zdjęcie.

## Jak wygląda naprawa

Czyścimy uszkodzenie, wypełniamy je specjalną żywicą i utwardzamy. Trwa to krótko, szyba wraca do wytrzymałości, a odprysk prawie znika. **Na naprawę odprysku po kamieniu dajemy bezterminową gwarancję na pęknięcie.**

## Kiedy trzeba wymienić szybę

- gdy od odprysku poszło już pęknięcie,
- gdy uszkodzenie jest duże albo jest ich kilka,
- gdy odprysk jest przy krawędzi albo w polu widzenia kierowcy.

## Co zrobić od razu po uderzeniu kamienia

Zaklej odprysk od zewnątrz kawałkiem przezroczystej taśmy, żeby nie wszedł tam brud i woda. Nie dmuchaj gorącym nawiewem na zimną szybę i nie trzaskaj drzwiami. No i nie odkładaj tego na później. Im szybciej przyjedziesz, tym większa szansa, że skończy się na naprawie.''',
    },
    {
        'title': 'Jak przygotować szyby auta na zimę',
        'slug': 'jak-przygotowac-szyby-auta-na-zime',
        'date': datetime.datetime(2026, 9, 15, 9, 0, tzinfo=datetime.timezone.utc),
        'excerpt': 'Kilka prostych rzeczy, dzięki którym szyba przetrwa mrozy bez pęknięcia, a rano szybciej odparujesz auto.',
        'content': '''Zima to dla szyb najgorszy czas w roku. Mróz, sól i piasek na drodze oraz nagłe zmiany temperatury sprawiają, że małe uszkodzenia szybko się powiększają. Oto, o czym warto pamiętać.

## Napraw odpryski przed mrozami

Woda dostaje się do odprysku, zamarza i rozsadza szkło od środka. Jeśli masz na szybie jakąś gwiazdkę, napraw ją jesienią, zanim zrobi się z niej pęknięcie przez pół szyby.

## Nie polewaj szyby gorącą wodą

To najczęstszy zimowy błąd. Nagła zmiana temperatury potrafi pęknąć szybę, zwłaszcza gdy ma już odprysk. Lepiej użyć odmrażacza w sprayu i skrobaczki, a nawiew włączać stopniowo, od chłodniejszego.

## Wymień pióra wycieraczek

Stare pióra zostawiają smugi, piszczą i słabo zbierają mokry śnieg. Twarda, popękana guma może nawet rysować szybę. Jesień to dobry moment na nowe pióra. Mamy je u siebie, dobierzemy do auta i od razu założymy.

## Wlej zimowy płyn do spryskiwaczy

Letni płyn zamarza w zbiorniku i w przewodach. Zimowy wlej, zanim przyjdą pierwsze przymrozki.

## Umyj szybę od środka

Brudna szyba od środka szybciej paruje, a pod słońce robi się na niej mocny odblask. Przetrzyj ją raz na jakiś czas, a rano szybciej odparujesz auto.''',
    },
    {
        'title': 'Szyba oryginalna czy zamiennik – czym się różnią?',
        'slug': 'szyba-oryginalna-czy-zamiennik',
        'date': datetime.datetime(2026, 9, 1, 9, 0, tzinfo=datetime.timezone.utc),
        'excerpt': 'Kto naprawdę robi szyby do samochodów i na co patrzeć przy wyborze nowej szyby.',
        'content': '''Przy wymianie szyby często pada pytanie: oryginał czy zamiennik? Odpowiedź jest prostsza, niż się wydaje. Wystarczy wiedzieć, kto naprawdę robi szyby do samochodów.

## Kto produkuje szyby

Producenci aut nie robią szyb sami. Zamawiają je w wyspecjalizowanych firmach, takich jak **Saint-Gobain Sekurit, Pilkington, AGC Automotive czy Guardian**. Te same firmy robią szyby na rynek części zamiennych, często na tych samych liniach. Szyba z logo marki auta i dobry zamiennik różnią się więc głównie nadrukiem i ceną.

## Na co zwrócić uwagę

- **Wyposażenie szyby.** Czujnik deszczu i zmierzchu, podgrzewanie, wyświetlacz HUD, szkło wyciszające, przyciemnienie. Nowa szyba musi mieć dokładnie to samo.
- **Homologacja.** Szyba dopuszczona do ruchu ma w rogu oznaczenie z literą „E” i numerem.
- **Kamera za szybą.** W wielu nowszych autach za szybą pracuje kamera asystentów jazdy. Po wymianie szyby czasem trzeba ją skalibrować.

## Jak dobrać dobrą szybę

Najpewniej po numerze VIN z dowodu rejestracyjnego. Podaj go, kiedy dzwonisz, a dobierzemy szybę z takim samym wyposażeniem, jakie ma Twoje auto. Montujemy szyby tych samych producentów, którzy dostarczają je do fabryk.''',
    },
]


def create_posts(apps, schema_editor):
    Post = apps.get_model('core', 'Post')
    for data in POSTS:
        if Post.objects.filter(slug=data['slug']).exists():
            continue
        Post.objects.create(
            title=data['title'], slug=data['slug'], excerpt=data['excerpt'], content=data['content'],
            published_at=data['date'], is_published=True)


def remove_posts(apps, schema_editor):
    apps.get_model('core', 'Post').objects.filter(slug__in=[p['slug'] for p in POSTS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_post'),
    ]

    operations = [
        migrations.RunPython(create_posts, remove_posts),
    ]
