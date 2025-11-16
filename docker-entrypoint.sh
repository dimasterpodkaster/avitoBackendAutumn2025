#!/bin/sh
set -e

python - << 'EOF'
import os, time, psycopg2

host = os.getenv("POSTGRES_HOST", "db")
db = os.getenv("POSTGRES_DB", "prreview")
user = os.getenv("POSTGRES_USER", "prreview")
password = os.getenv("POSTGRES_PASSWORD", "prreview")

for i in range(30):
    try:
        psycopg2.connect(host=host, dbname=db, user=user, password=password)
        break
    except Exception:
        time.sleep(1)
else:
    raise SystemExit("Database is not available")
EOF

python manage.py migrate --noinput
gunicorn prreview.wsgi:application --bind 0.0.0.0:8080