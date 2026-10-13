"""Zdjecia na stronie: galeria realizacji i zdjecia firmy.

Pliki WebP leza w media/ w dwoch rozmiarach:
  media/galeria/<plik>.webp      – duze (max 1920 px), otwierane po kliknieciu w powiekszeniu
  media/galeria/min/<plik>.webp  – miniatury (max 800 px) do kafelkow
Zeby dodac zdjecie: wrzuc plik do obu folderow (np. skryptem scripts/webp.py) i dopisz wpis ponizej.

Pole "ksztalt" ustawia rozmiar kafelka w siatce galerii:
  'poziome' – zwykly kafelek, 'pionowe' – wysoki (2 rzedy), 'szerokie' – szeroki (2 kolumny)
Siatka ma 4 kolumny, wiec zeby nie bylo dziur, suma pol (poziome = 1, pionowe/szerokie = 2)
w pierwszych GALLERY_VISIBLE zdjeciach i w calej liscie powinna byc wielokrotnoscia 4.
"""

# Kolejnosc ma znaczenie: pierwsze GALLERY_VISIBLE zdjec widac od razu, reszta po kliknieciu "Pokaz wiecej".
GALLERY = [
    {'plik': 'mercedes-g', 'podpis': 'Mercedes G – wymiana szyby czołowej', 'ksztalt': 'szerokie'},
    {'plik': 'naprawa-odprysku', 'podpis': 'Naprawa odprysku', 'ksztalt': 'pionowe'},
    {'plik': 'tesla', 'podpis': 'Tesla – nowa szyba czołowa', 'ksztalt': 'poziome'},
    {'plik': 'flota-man', 'podpis': 'Flota MAN – wymiana szyb', 'ksztalt': 'poziome'},
    {'plik': 'bmw-seria-4', 'podpis': 'BMW serii 4 – wymiana szyby czołowej', 'ksztalt': 'poziome'},
    {'plik': 'dojazd-do-klienta', 'podpis': 'Dojazd do klienta – ciężarówki', 'ksztalt': 'szerokie'},
    {'plik': 'ferrari', 'podpis': 'Ferrari – wymiana szyby', 'ksztalt': 'poziome'},
    {'plik': 'land-rover-defender', 'podpis': 'Land Rover Defender – wymiana szyby', 'ksztalt': 'poziome'},
    {'plik': 'mustang', 'podpis': 'Ford Mustang – montaż szyby', 'ksztalt': 'pionowe'},
    {'plik': 'porsche', 'podpis': 'Porsche – wymiana szyby czołowej', 'ksztalt': 'poziome'},
    {'plik': 'toyota-supra', 'podpis': 'Toyota Supra – wymiana szyby', 'ksztalt': 'poziome'},
    {'plik': 'ciezarowka-daf', 'podpis': 'Wymiana szyby w ciężarówce u klienta', 'ksztalt': 'poziome'},
    # --- ponizsze widac po kliknieciu "Pokaz wiecej zdjec" ---
    # (kolejnosc dobrana tak, zeby kafelki rozne ksztaltow wypelnily 5 rzedow bez dziur)
    {'plik': 'corvette', 'podpis': 'Corvette – montaż szyby', 'ksztalt': 'pionowe'},
    {'plik': 'odprysk-pomiar', 'podpis': 'Pomiar temperatury szyby przed naprawą odprysku', 'ksztalt': 'pionowe'},
    {'plik': 'auto-sportowe', 'podpis': 'Auto sportowe – wymiana szyby czołowej', 'ksztalt': 'szerokie'},
    {'plik': 'corvette-tyl', 'podpis': 'Corvette – wymiana tylnej szyby', 'ksztalt': 'poziome'},
    {'plik': 'mercedes-s', 'podpis': 'Mercedes S – wymiana szyby', 'ksztalt': 'poziome'},
    {'plik': 'serwis-mobilny', 'podpis': 'Serwis mobilny – wymiana szyby na miejscu', 'ksztalt': 'szerokie'},
    {'plik': 'wklejanie-szyby', 'podpis': 'Wklejanie szyby czołowej', 'ksztalt': 'pionowe'},
    {'plik': 'odprysk-po-naprawie', 'podpis': 'Odprysk po naprawie', 'ksztalt': 'pionowe'},
    {'plik': 'audi', 'podpis': 'Audi – auto zabezpieczone folią przed montażem', 'ksztalt': 'poziome'},
    {'plik': 'odprysk-zywica', 'podpis': 'Naprawa odprysku – nakładanie żywicy', 'ksztalt': 'pionowe'},
    {'plik': 'odprysk-przed-naprawa', 'podpis': 'Odprysk przed naprawą', 'ksztalt': 'poziome'},
    {'plik': 'biuro', 'podpis': 'Nasze biuro w Pleszewie', 'ksztalt': 'szerokie'},
]

# Ile zdjec widac od razu (reszta jest schowana pod przyciskiem)
GALLERY_VISIBLE = 12

# Zdjecia uzyte w innych miejscach strony (folder media/firma/)
PHOTO_HERO = 'firma/siedziba.webp'   # budynek firmy z vanem – baner na gorze strony
PHOTO_ABOUT = 'firma/biuro-recepcja.webp'  # biuro – sekcja "O nas"

# Mapowanie oryginalnych nazw plikow od klienta na nazwy na stronie
# (uzywane tylko przy konwersji zdjec, patrz scripts/zdjecia_klienta.py)
ORIGINALS = {
    'gclasswymiaana.jpg': 'galeria/mercedes-g',
    'odpryskwymianka.jpg': 'galeria/naprawa-odprysku',
    'teslawymiana.jpg': 'galeria/tesla',
    'tiry.jpg': 'galeria/flota-man',
    'bmwwymiana.JPG': 'galeria/bmw-seria-4',
    'tiry2.jpg': 'galeria/dojazd-do-klienta',
    'ferarkawymiana.JPG': 'galeria/ferrari',
    'landwymiana.jpg': 'galeria/land-rover-defender',
    'mustangwymiana.JPG': 'galeria/mustang',
    'porschewymiana.jpg': 'galeria/porsche',
    'suprawymiana.jpg': 'galeria/toyota-supra',
    'tir wymiana.jpg': 'galeria/ciezarowka-daf',
    'corvete2.JPG': 'galeria/corvette',
    'corvetewymiana.JPG': 'galeria/corvette-tyl',
    'mercywmiana.JPG': 'galeria/mercedes-s',
    'audiwymiana.JPG': 'galeria/audi',
    'odprysk2.jpg': 'galeria/odprysk-pomiar',
    'wymianasportoweauto.jpg': 'galeria/auto-sportowe',
    'autowymiana.jpg': 'galeria/wklejanie-szyby',
    'odprysk.jpg': 'galeria/odprysk-przed-naprawa',
    'odpryskfinal.jpg': 'galeria/odprysk-po-naprawie',
    'odprysk5.JPG': 'galeria/odprysk-zywica',
    'tirywymiana.jpg': 'galeria/serwis-mobilny',
    'biuro srodek.JPG': 'galeria/biuro',
    'zdjecie główne firmy.jpg': 'firma/siedziba',
    'biurofirma.jpg': 'firma/biuro-recepcja',
}
