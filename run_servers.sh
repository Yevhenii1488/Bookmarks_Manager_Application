#!/bin/bash

# Запуск Django (бэкенд) на порту 8000
python manage.py runserver 8000

# Переход в папку со статикой
cd staticfiles

# python3 manage.py collectstatic

# Запуск фронтенда (статики) на порту 3000
python -m http.server 3000
