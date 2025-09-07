#!/bin/bash
set -e

# Create venv if not exists
if [ ! -d ".env" ]; then
  python3 -m venv .env
fi

# Activate venv
source .env/bin/activate

pip install --upgrade pip
pip install -r requirements.txt