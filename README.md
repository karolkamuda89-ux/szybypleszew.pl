# szybypleszew.pl

Projekt Django.

## Uruchomienie lokalne

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Zmienne środowiskowe — patrz `.env.example`.

## Zamiana zdjęć na WebP

Skrypt `scripts/webp.py` zamienia zdjęcia (JPG, PNG, …) na lżejszy format WebP.
Plik `.webp` powstaje obok oryginału, oryginały domyślnie zostają.

```bash
python scripts/webp.py static/img              # cały folder z podfolderami
python scripts/webp.py static/img --max 1920   # + zmniejsz zdjęcia większe niż 1920 px
python scripts/webp.py static/img -q 75        # mocniejsza kompresja (domyślnie 82)
python scripts/webp.py static/img --usun       # usuń oryginały po konwersji
```

Pełna lista opcji: `python scripts/webp.py --help`.

## Panel admina i galeria

Galerię realizacji edytuje się w panelu: `http://localhost:8000/admin/` → **Galeria – realizacje**.

- Jedna realizacja = jeden kafelek (opis, rozmiar kafelka, kolejność, widoczność).
- Do realizacji można dodać kilka zdjęć naraz (pole „Dodaj zdjęcia”). Na stronie przewija się je strzałkami.
- Wgrane zdjęcia są automatycznie zamieniane na WebP (duże 1920 px + miniatura 800 px).

Pierwsze uruchomienie:

```bash
python manage.py migrate
python manage.py createsuperuser      # konto do logowania w panelu
python manage.py import_gallery       # wczytanie startowej galerii z core/gallery.py
```

## Wdrożenie (serwer Hetzner, Ubuntu)

Strona działa jako: **nginx** (serwer WWW, HTTPS, pliki statyczne) → **Gunicorn** (Django) → **PostgreSQL** (baza).
Zdjęcia z panelu trafiają do **Cloudflare R2**, więc nie znikają przy aktualizacjach ani przenosinach serwera.

Pliki konfiguracyjne są w folderze `deploy/`:

| Plik | Do czego |
|---|---|
| `szybypleszew.service` | usługa systemd – uruchamia Gunicorna i podnosi stronę po restarcie serwera |
| `nginx-szybypleszew.conf` | konfiguracja nginx (limit wgrywanych plików 50 MB, cache, kompresja) |
| `deploy.sh` | aktualizacja strony jedną komendą: `bash /home/szybypleszew/app/deploy/deploy.sh` |
| `backup.sh` | codzienna kopia bazy (14 dni wstecz) – do crona |

Zmienne środowiskowe na serwerze (plik `/home/szybypleszew/app/.env`, wzór w `.env.example`):
`DJANGO_DEBUG=False`, `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS`, `DATABASE_URL`, `GOOGLE_PLACES_API_KEY`,
dane poczty (`EMAIL_*`) i Cloudflare R2 (`R2_*`).

Pierwsze wgranie zdjęć do R2: `python manage.py upload_media`, potem `python manage.py import_gallery`.
