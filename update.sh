#!/bin/bash
cd "$(dirname "$0")"

if [ "$1" != "--skip-pull" ]; then
    echo Fetching latest version from git repository
    git pull
    if [ $? -ne 0 ]; then
        echo Failed to pull
        exit
    fi
fi

source .venv/bin/activate
if [ $? -ne 0 ]; then
    echo Failed to activate venv
    exit
fi

echo Installing or updating dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt
if [ $? -ne 0 ]; then
  echo Failed to install / update dependencies
  exit
fi
