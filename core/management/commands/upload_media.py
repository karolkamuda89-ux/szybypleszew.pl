"""Wgrywa pliki z lokalnego folderu media/ do magazynu plikow strony (Cloudflare R2 na serwerze).

Uzycie (na serwerze, z ustawionymi zmiennymi R2_*):
    python manage.py upload_media              # wgrywa brakujace pliki z ./media
    python manage.py upload_media --zrodlo /sciezka/do/media
    python manage.py upload_media --sprawdz    # tylko pokazuje, co by wgral

Pliki, ktore juz sa w R2, sa pomijane – komende mozna uruchamiac wielokrotnie.
Sluzy do jednorazowego przeniesienia zdjec (galeria, firma, blog, sekcja Nowość) przy wdrozeniu.
"""
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Wgrywa pliki z media/ do magazynu plikow (Cloudflare R2).'

    def add_arguments(self, parser):
        parser.add_argument('--zrodlo', default=str(settings.BASE_DIR / 'media'), help='folder z plikami (domyslnie ./media)')
        parser.add_argument('--sprawdz', action='store_true', help='nic nie wgrywaj, tylko pokaz liste')

    def handle(self, *args, **options):
        source = Path(options['zrodlo'])
        if not source.is_dir():
            raise CommandError(f'Nie ma folderu {source}')
        if not getattr(settings, 'R2_BUCKET', ''):
            self.stdout.write(self.style.WARNING('Uwaga: R2 nie jest skonfigurowane – pliki trafia do lokalnego media/.'))

        uploaded = skipped = 0
        for path in sorted(p for p in source.rglob('*') if p.is_file() and p.name != '.gitkeep'):
            name = path.relative_to(source).as_posix()   # np. galeria/min/tesla.webp
            if default_storage.exists(name):
                skipped += 1
                continue
            if options['sprawdz']:
                self.stdout.write(f'  wgralbym: {name}')
                uploaded += 1
                continue
            with path.open('rb') as f:
                saved = default_storage.save(name, File(f))
            if saved != name:
                # nie powinno sie zdarzyc (sprawdzamy exists), ale gdyby – baza wskazuje na oryginalna nazwe
                self.stderr.write(f'  UWAGA: {name} zapisany jako {saved}')
            self.stdout.write(f'  wgrano: {name}')
            uploaded += 1
        verb = 'Do wgrania' if options['sprawdz'] else 'Wgrano'
        self.stdout.write(self.style.SUCCESS(f'{verb}: {uploaded}, pominieto (juz byly): {skipped}.'))
