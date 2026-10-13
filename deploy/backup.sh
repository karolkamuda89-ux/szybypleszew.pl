#!/usr/bin/env bash
# Codzienna kopia bazy danych (cron roota, np.: 30 3 * * * bash /home/szybypleszew/app/deploy/backup.sh)
# Kopie leza w /home/szybypleszew/backups, trzymamy ostatnie 14 dni. Zdjecia sa w Cloudflare R2.
set -euo pipefail
DIR=/home/szybypleszew/backups
mkdir -p "$DIR"
sudo -u postgres pg_dump szybypleszew | gzip > "$DIR/baza-$(date +%F).sql.gz"
find "$DIR" -name 'baza-*.sql.gz' -mtime +14 -delete
