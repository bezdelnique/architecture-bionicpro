#!/usr/bin/env bash
set -e

echo 'prepare env'
python -m venv venv
source ./venv/bin/activate
echo 'package install'
pip install -r requirements.txt
echo 'syncing'
python pgsync.py
