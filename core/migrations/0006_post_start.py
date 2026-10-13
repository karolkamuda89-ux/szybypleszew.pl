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
        'excerpt': 'Kamień uderzył w szybę i została mała gwiazdka? Wyjaśniamy, kiedy wystarczy szybka '
                   'naprawa żywicą, a kiedy wymiana szyby jest konieczna.',
        'content': '''Mały odprysk łatwo zbagatelizować – przecież prawie go nie widać. Problem w tym, że szyba ciągle pracuje: nagrzewa się i stygnie, drga na nierównościach, a zimą dochodzą duże różnice temperatur między wnętrzem auta a powietrzem na zewnątrz. Z dnia na dzień z niewinnej gwiazdki może zrobić się długie pęknięcie, a wtedy naprawa nie wchodzi już w grę.

## Kiedy odprysk można naprawić

Naprawa jest zwykle możliwa, gdy:

- uszkodzenie jest niewielkie (mniej więcej do rozmiaru monety),
- odprysk nie leży tuż przy krawędzi szyby,
- nie znajduje się na wprost oczu kierowcy,
- od odprysku nie rozchodzą się jeszcze pęknięcia.

Ostatecznie zawsze oceniamy uszkodzenie na miejscu – wystarczy przyjechać albo przesłać zdjęcie.

## Jak wygląda naprawa

Miejsce uszkodzenia oczyszczamy, a następnie wypełniamy specjalną żywicą, którą utwardzamy. Naprawa trwa krótko, szyba odzyskuje wytrzymałość, a odprysk staje się dużo mniej widoczny. **Na naprawę odprysków po uderzeniu kamienia dajemy bezterminową gwarancję na pęknięcie.**

## Kiedy potrzebna jest wymiana szyby

- gdy od odprysku poszło już pęknięcie,
- gdy uszkodzenie jest duże albo jest ich kilka,
- gdy odprysk leży przy krawędzi lub w polu widzenia kierowcy.

## Co zrobić od razu po uderzeniu kamienia

Zaklej odprysk od zewnątrz kawałkiem przezroczystej taśmy – ochroni go przed brudem i wilgocią, a naprawa będzie skuteczniejsza. Unikaj kierowania gorącego nawiewu prosto na zimną szybę i trzaskania drzwiami. I nie zwlekaj z wizytą – im szybciej, tym większa szansa, że skończy się na naprawie.''',
    },
    {
        'title': 'Jak przygotować szyby auta na zimę',
        'slug': 'jak-przygotowac-szyby-auta-na-zime',
        'date': datetime.datetime(2026, 9, 15, 9, 0, tzinfo=datetime.timezone.utc),
        'excerpt': 'Kilka prostych nawyków, które chronią szybę przed pęknięciem przy mrozie '
                   'i poprawiają widoczność w zimowe poranki.',
        'content': '''Zima to dla szyb najtrudniejszy czas w roku. Mróz, sól, piasek na drogach i gwałtowne zmiany temperatury sprawiają, że drobne uszkodzenia szybko się powiększają. Oto, o czym warto pamiętać.

## Napraw odpryski przed mrozami

Woda, która dostanie się do odprysku, zamarza i rozsadza szkło od środka. Jeśli na szybie jest jakakolwiek gwiazdka, najlepiej naprawić ją jesienią – zanim zrobi się z niej pęknięcie przez pół szyby.

## Nie polewaj szyby gorącą wodą

To najczęstszy zimowy błąd. Nagła zmiana temperatury może sprawić, że szyba pęknie – szczególnie gdy ma już jakiś odprysk. Zamiast tego użyj odmrażacza w sprayu i skrobaczki, a nawiew włączaj stopniowo, zaczynając od niższej temperatury.

## Wymień pióra wycieraczek

Zużyte pióra zostawiają smugi, piszczą i gorzej zbierają śnieg z wodą, a twarde, popękane gumy mogą rysować szybę. Jesień to dobry moment na wymianę – pióra dobierzemy do Twojego auta i od razu zamontujemy.

## Pamiętaj o zimowym płynie do spryskiwaczy

Letni płyn zamarza w zbiorniku i przewodach. Zimowy płyn wlej, zanim przyjdą pierwsze przymrozki.

## Dbaj o czystość szyby od środka

Brudna szyba od wewnątrz szybciej paruje, a pod słońce zimą tworzy uciążliwe odblaski. Raz na jakiś czas przetrzyj ją od środka – poprawi to widoczność i skróci czas odparowywania.''',
    },
    {
        'title': 'Szyba oryginalna czy zamiennik – czym się różnią?',
        'slug': 'szyba-oryginalna-czy-zamiennik',
        'date': datetime.datetime(2026, 9, 1, 9, 0, tzinfo=datetime.timezone.utc),
        'excerpt': 'Kto produkuje szyby montowane w fabryce i na co zwrócić uwagę przy wyborze nowej szyby '
                   'do swojego auta.',
        'content': '''Przy wymianie szyby często pada pytanie: oryginał czy zamiennik? Odpowiedź jest prostsza, niż się wydaje – wystarczy wiedzieć, kto naprawdę produkuje szyby samochodowe.

## Kto produkuje szyby do aut

Producenci samochodów nie robią szyb sami. Zamawiają je u wyspecjalizowanych firm, takich jak **Saint-Gobain Sekurit, Pilkington, AGC Automotive czy Guardian**. Te same firmy produkują szyby na rynek części zamiennych – często na tych samych liniach produkcyjnych. Szyba z logo producenta auta i szyba „zamiennik” renomowanej marki mogą więc różnić się głównie nadrukiem i ceną.

## Na co zwrócić uwagę

- **Wyposażenie szyby** – czujnik deszczu i zmierzchu, podgrzewanie, wyświetlacz HUD, szkło akustyczne czy przyciemnienie. Nowa szyba musi mieć dokładnie te same funkcje.
- **Homologacja** – szyba dopuszczona do ruchu ma w rogu oznaczenie z literą „E” i numerem.
- **Kamera asystentów jazdy** – w wielu nowszych autach za szybą pracuje kamera systemów bezpieczeństwa. Po wymianie szyby może być konieczna jej kalibracja.

## Jak dobrać właściwą szybę

Najpewniej po numerze VIN, który znajdziesz w dowodzie rejestracyjnym. Podaj go przy kontakcie, a dobierzemy szybę z dokładnie takim wyposażeniem, jakie ma Twoje auto. Pracujemy na szybach renomowanych producentów, tych samych, które trafiają do aut w fabryce.''',
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
