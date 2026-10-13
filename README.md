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
