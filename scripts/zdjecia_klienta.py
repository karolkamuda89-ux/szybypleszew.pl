"""Jednorazowa konwersja zdjec od klienta do media/ (WebP, nowe nazwy z core/gallery.py).

Uzycie (z glownego folderu projektu):
    python scripts/zdjecia_klienta.py "C:/sciezka/do/folderu/ze/zdjeciami"

Dla kazdego zdjecia z mapy ORIGINALS tworzy:
  media/<nazwa>.webp        – duza wersja (max 1920 px)
  media/galeria/min/...     – miniatura do kafelkow galerii (max 800 px), tylko dla galerii
"""
import sys
from pathlib import Path

# Pozwala zaimportowac core.gallery i scripts/webp.py przy uruchamianiu z glownego folderu
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'scripts'))

from core.gallery import ORIGINALS  # noqa: E402
from webp import konwertuj, czytelny_rozmiar  # noqa: E402

MEDIA = ROOT / 'media'
JAKOSC = 82
DUZE = 1920
MINIATURA = 800


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        return 1
    zrodlo = Path(sys.argv[1])
    przed = po = 0
    brakujace = []
    for oryginal, nazwa in ORIGINALS.items():
        plik = zrodlo / oryginal
        if not plik.exists():
            brakujace.append(oryginal)
            continue
        duzy = MEDIA / f'{nazwa}.webp'
        konwertuj(plik, duzy, JAKOSC, DUZE)
        przed += plik.stat().st_size
        po += duzy.stat().st_size
        info = f'{czytelny_rozmiar(plik.stat().st_size)} -> {czytelny_rozmiar(duzy.stat().st_size)}'
        # Miniatury tylko dla zdjec z galerii (kafelki); zdjecia firmy sa wyswietlane w jednym rozmiarze
        if nazwa.startswith('galeria/'):
            mini = MEDIA / 'galeria' / 'min' / f'{Path(nazwa).name}.webp'
            konwertuj(plik, mini, JAKOSC, MINIATURA)
            info += f' (miniatura {czytelny_rozmiar(mini.stat().st_size)})'
        print(f'  {oryginal} -> media/{nazwa}.webp  {info}')
    print(f'\nRazem: {czytelny_rozmiar(przed)} -> {czytelny_rozmiar(po)} (bez miniatur)')
    if brakujace:
        print('Brakujace pliki:', ', '.join(brakujace))
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
