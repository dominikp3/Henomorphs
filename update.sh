#!/bin/bash
cd "$(dirname "$0")"
echo Fetching latest version from git repository
git pull
if [ $? -ne 0 ]; then
    echo Failed to pull
    exit
fi
echo Installing or updating dependencies
source .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
if [ $? -ne 0 ]; then
  echo Failed to install / update dependencies
  exit
fi
