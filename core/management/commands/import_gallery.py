"""Import obecnej galerii (lista GALLERY z core/gallery.py) do bazy danych.

Uzycie: python manage.py import_gallery

Tworzy po jednej realizacji na kazde zdjecie z listy, korzystajac z plikow juz lezacych
w magazynie plikow (media/ lokalnie albo Cloudflare R2 na serwerze) – nic nie jest ponownie konwertowane.
Na serwerze najpierw wgraj zdjecia do R2: python manage.py upload_media Realizacje o tym samym opisie,
ktore juz sa w bazie, sa pomijane – komende mozna bezpiecznie uruchomic kilka razy.
"""
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand

from core.gallery import GALLERY
from core.models import GalleryItem, GalleryPhoto


class Command(BaseCommand):
    help = 'Importuje zdjecia z core/gallery.py do galerii w panelu admina.'

    def handle(self, *args, **options):
        created = skipped = 0
        for position, foto in enumerate(GALLERY, start=1):
            if GalleryItem.objects.filter(title=foto['podpis']).exists():
                skipped += 1
                continue
            image = f"galeria/{foto['plik']}.webp"
            thumb = f"galeria/min/{foto['plik']}.webp"
            # default_storage = lokalny media/ albo Cloudflare R2 (zaleznie od ustawien)
            if not default_storage.exists(image):
                self.stderr.write(f'Brak pliku {image} w magazynie plikow – pomijam')
                continue
            item = GalleryItem.objects.create(title=foto['podpis'], shape=foto['ksztalt'], order=position * 10)
            # Przypisanie nazwy pliku (bez wgrywania) – plik juz istnieje w media/
            GalleryPhoto.objects.create(item=item, image=image, thumbnail=thumb, order=10)
            created += 1
        self.stdout.write(self.style.SUCCESS(f'Dodano {created} realizacji, pominieto {skipped} (juz byly w bazie).'))
