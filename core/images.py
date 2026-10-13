"""Przetwarzanie zdjec wgrywanych przez panel admina: konwersja do WebP i zmniejszanie.

Ta sama logika co w scripts/webp.py, ale zwraca plik w pamieci (ContentFile),
ktory Django zapisuje potem w media/.
"""
from io import BytesIO

from django.core.files.base import ContentFile
from PIL import Image, ImageOps

JAKOSC = 82        # jakosc WebP – praktycznie bez widocznej straty
DUZE = 1920        # dluzszy bok duzego zdjecia (powiekszenie w lightboxie)
MINIATURA = 800    # dluzszy bok miniatury (kafelek w galerii)


def to_webp(source, max_side):
    """Wczytuje obraz z pliku `source` i zwraca go jako WebP (ContentFile) zmniejszony do max_side px."""
    source.seek(0)
    with Image.open(source) as img:
        # Zdjecia z telefonu bywaja obrocone tylko znacznikiem EXIF – obracamy je fizycznie
        img = ImageOps.exif_transpose(img)
        if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
            img = img.convert('RGBA')   # zachowujemy przezroczystosc
        else:
            img = img.convert('RGB')
        if max(img.size) > max_side:
            img.thumbnail((max_side, max_side), Image.LANCZOS)
        buffer = BytesIO()
        img.save(buffer, 'WEBP', quality=JAKOSC, method=6)
    return ContentFile(buffer.getvalue())
