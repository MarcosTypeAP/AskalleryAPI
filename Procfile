release: python manage.py migrate; python manage.py deleteorphanedmedia --noinput
web: gunicorn djangoNotesApp.wsgi 
