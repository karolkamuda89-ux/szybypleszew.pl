"""Zamiana zdjec (JPG, PNG, ...) na format WebP – lzejszy, a przy tym dobrej jakosci.

Przyklady uzycia (z glownego folderu projektu):

    python scripts/webp.py static/img                 # caly folder razem z podfolderami
    python scripts/webp.py zdjecie.jpg                # pojedynczy plik
    python scripts/webp.py static/img --max 1920      # dodatkowo zmniejsz zdjecia szersze/wyzsze niz 1920 px
    python scripts/webp.py static/img -q 75           # mocniejsza kompresja (domyslnie 82)
    python scripts/webp.py static/img --usun          # usun oryginaly po udanej konwersji
    python scripts/webp.py static/img --nadpisz       # przerob ponownie tez te, ktore maja juz .webp
    python scripts/webp.py zdjecia --out media/galeria  # zapisz WebP w innym folderze

Plik WebP powstaje obok oryginalu, z ta sama nazwa (np. galeria/bus.jpg -> galeria/bus.webp),
albo w folderze podanym w --out (z zachowaniem podfolderow). Domyslnie oryginaly zostaja nietkniete.
"""
import argparse
import sys
from pathlib import Path

from PIL import Image, ImageOps

# Rozszerzenia plikow, ktore skrypt zamienia (wielkosc liter nie ma znaczenia)
OBSLUGIWANE = {'.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff', '.gif'}


def znajdz_zdjecia(sciezki):
    """Zwraca liste par (plik, sciezka wzgledna) z podanych sciezek (pliki lub foldery, rekurencyjnie).

    Sciezka wzgledna sluzy do odtworzenia podfolderow przy zapisie do --out.
    """
    pliki = []
    for sciezka in sciezki:
        p = Path(sciezka)
        if p.is_dir():
            pliki.extend((f, f.relative_to(p)) for f in sorted(p.rglob('*')) if f.suffix.lower() in OBSLUGIWANE)
        elif p.is_file() and p.suffix.lower() in OBSLUGIWANE:
            pliki.append((p, Path(p.name)))
        else:
            print(f'  pomijam: {p} (nie istnieje albo to nie jest obslugiwany obraz)')
    return pliki


def konwertuj(plik, cel, jakosc, max_bok):
    """Zapisuje plik jako WebP pod sciezka `cel`."""
    cel.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(plik) as img:
        # Zdjecia z telefonu czesto sa zapisane "na boku" i obracane tylko przez znacznik EXIF.
        # exif_transpose obraca je fizycznie, zeby w WebP nie lezaly krzywo.
        img = ImageOps.exif_transpose(img)

        # Zachowujemy przezroczystosc (np. PNG z logo), reszte zapisujemy jako zwykle RGB
        if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
            img = img.convert('RGBA')
        else:
            img = img.convert('RGB')

        # Opcjonalne zmniejszenie: dluzszy bok najwyzej max_bok px, proporcje bez zmian.
        # Na strone zdjecia wieksze niz ok. 1920 px to zwykle niepotrzebne megabajty.
        if max_bok and max(img.size) > max_bok:
            img.thumbnail((max_bok, max_bok), Image.LANCZOS)

        # method=6 – najwolniejsza, ale najlepsza kompresja (plik mniejszy przy tej samej jakosci)
        img.save(cel, 'WEBP', quality=jakosc, method=6)


def czytelny_rozmiar(bajty):
    for jednostka in ('B', 'KB', 'MB', 'GB'):
        if bajty < 1024 or jednostka == 'GB':
            return f'{bajty:.0f} {jednostka}' if jednostka == 'B' else f'{bajty:.1f} {jednostka}'
        bajty /= 1024


def main():
    parser = argparse.ArgumentParser(description='Zamiana zdjec na WebP.')
    parser.add_argument('sciezki', nargs='+', help='pliki lub foldery ze zdjeciami')
    parser.add_argument('-q', '--jakosc', type=int, default=82,
                        help='jakosc 1-100 (domyslnie 82 – praktycznie bez widocznej straty)')
    parser.add_argument('--max', dest='max_bok', type=int, default=0,
                        help='maksymalny dluzszy bok w px, np. 1920 (domyslnie bez zmniejszania)')
    parser.add_argument('--usun', action='store_true', help='usun oryginaly po udanej konwersji')
    parser.add_argument('--nadpisz', action='store_true', help='przerob tez pliki, ktore maja juz wersje .webp')
    parser.add_argument('--out', type=Path, default=None,
                        help='folder docelowy (domyslnie WebP zapisuje sie obok oryginalu)')
    args = parser.parse_args()

    if not 1 <= args.jakosc <= 100:
        parser.error('jakosc musi byc w zakresie 1-100')

    pliki = znajdz_zdjecia(args.sciezki)
    if not pliki:
        print('Nie znaleziono zdjec do konwersji.')
        return 1

    przed_suma = po_suma = 0
    zrobione = pominiete = bledy = 0
    for plik, wzgledna in pliki:
        # Gdzie zapisac WebP: obok oryginalu albo w --out z zachowaniem podfolderow
        cel = (args.out / wzgledna).with_suffix('.webp') if args.out else plik.with_suffix('.webp')
        # Domyslnie nie przerabiamy drugi raz plikow, ktore maja juz aktualna wersje WebP
        if cel.exists() and not args.nadpisz and cel.stat().st_mtime >= plik.stat().st_mtime:
            pominiete += 1
            continue
        try:
            przed = plik.stat().st_size
            konwertuj(plik, cel, args.jakosc, args.max_bok)
            po = cel.stat().st_size
        except Exception as exc:  # uszkodzony plik nie powinien przerwac calej konwersji
            bledy += 1
            print(f'  BLAD: {plik}: {exc}')
            continue

        przed_suma += przed
        po_suma += po
        zrobione += 1
        oszczednosc = 100 - po * 100 / przed if przed else 0
        print(f'  {plik.name} -> {cel}  {czytelny_rozmiar(przed)} -> {czytelny_rozmiar(po)} (-{oszczednosc:.0f}%)')
        if args.usun:
            plik.unlink()

    print()
    print(f'Gotowe: {zrobione} skonwertowanych, {pominiete} pominietych (maja juz .webp), {bledy} bledow.')
    if zrobione:
        print(f'Rozmiar: {czytelny_rozmiar(przed_suma)} -> {czytelny_rozmiar(po_suma)} '
              f'(oszczednosc {czytelny_rozmiar(przed_suma - po_suma)}).')
    return 1 if bledy else 0


if __name__ == '__main__':
    sys.exit(main())
