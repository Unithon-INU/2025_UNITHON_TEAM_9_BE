cd inference || exit
python manage.py runserver 127.0.0.1:8086

# gunicorn inference.wsgi:application --bind 127.0.0.1:8086 --workers 1
