web: gunicorn safe.wsgi:application
worker: celery -A safe worker --loglevel=info
beat: celery -A safe beat --loglevel=info