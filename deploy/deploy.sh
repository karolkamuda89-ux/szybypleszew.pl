#!/usr/bin/env bash
# Aktualizacja strony na serwerze jedna komenda (uruchamiac jako root):
#     bash /home/szybypleszew/app/deploy/deploy.sh
# Pobiera najnowszy kod z GitHuba, instaluje zaleznosci, aktualizuje baze i pliki statyczne, restartuje strone.
set -euo pipefail

APP=/home/szybypleszew/app
as_app() { sudo -u szybypleszew -H bash -c "cd $APP && $*"; }

echo '==> Pobieram kod z GitHuba'
as_app 'git pull --ff-only'

echo '==> Instaluje zaleznosci'
as_app 'venv/bin/pip install -q -r requirements.txt'

echo '==> Aktualizuje baze danych'
as_app 'venv/bin/python manage.py migrate --noinput'

echo '==> Zbieram pliki statyczne (CSS/JS/obrazki z numerami wersji)'
as_app 'venv/bin/python manage.py collectstatic --noinput'

echo '==> Sprawdzam ustawienia'
as_app 'venv/bin/python manage.py check --deploy --fail-level ERROR'

echo '==> Restartuje strone'
systemctl restart szybypleszew
sleep 2
systemctl is-active --quiet szybypleszew && echo 'Gotowe – strona dziala.' || { echo 'BLAD: strona nie wstala'; journalctl -u szybypleszew -n 30 --no-pager; exit 1; }
