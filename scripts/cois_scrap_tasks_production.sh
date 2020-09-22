#!/usr/bin/env bash

export WORKON_HOME=/var/envs
export PROJECT_HOME=/var/www
export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3
export VIRTUALENVWRAPPER_HOOK_DIR=/var/envs/bin
export PIP_RESPECT_VIRTUALENV=true
export COMPANIFY_MODE=local

source /var/envs/mealpaper/bin/activate

cd /var/www/mealpaper/mealpaper/

celery --app=apps.property.celery:app worker --loglevel=INFO