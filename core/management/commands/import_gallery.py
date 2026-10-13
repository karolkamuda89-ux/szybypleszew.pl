"""Import obecnej galerii (lista GALLERY z core/gallery.py) do bazy danych.

Uzycie: python manage.py import_gallery

Tworzy po jednej realizacji na kazde zdjecie z listy, korzystajac z plikow juz lezacych
w media/galeria/ (nic nie jest ponownie konwertowane). Realizacje o tym samym opisie,
ktore juz sa w bazie, sa pomijane – komende mozna bezpiecznie uruchomic kilka razy.
"""
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from core.gallery import GALLERY
from core.models import GalleryItem, GalleryPhoto


class Command(BaseCommand):
    help = 'Importuje zdjecia z core/gallery.py do galerii w panelu admina.'

    def handle(self, *args, **options):
        media = Path(settings.MEDIA_ROOT)
        created = skipped = 0
        for position, foto in enumerate(GALLERY, start=1):
            if GalleryItem.objects.filter(title=foto['podpis']).exists():
                skipped += 1
                continue
            image = f"galeria/{foto['plik']}.webp"
            thumb = f"galeria/min/{foto['plik']}.webp"
            if not (media / image).exists():
                self.stderr.write(f'Brak pliku media/{image} – pomijam')
                continue
            item = GalleryItem.objects.create(title=foto['podpis'], shape=foto['ksztalt'], order=position * 10)
            # Przypisanie nazwy pliku (bez wgrywania) – plik juz istnieje w media/
            GalleryPhoto.objects.create(item=item, image=image, thumbnail=thumb, order=10)
            created += 1
        self.stdout.write(self.style.SUCCESS(f'Dodano {created} realizacji, pominieto {skipped} (juz byly w bazie).'))
