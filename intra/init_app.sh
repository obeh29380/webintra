#!/bin/sh
python manage.py makemigrations
python manage.py migrate
python manage.py register_workstatus data/work_status.json
python manage.py runserver 0.0.0.0:8000