#!/bin/bash
cd /home/botcynococo/repositories/ExchangePanel/
source /home/botcynococo/virtualenv/PardisPanel/3.10/bin/activategit 
git pull origin main
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
touch passenger_wsgi.py
