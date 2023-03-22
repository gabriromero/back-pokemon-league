#!/bin/bash

flask db upgrade

flask run --host 0.0.0.0

exec gunicorn --bind 0.0.0.0:80 "app:create_app()"