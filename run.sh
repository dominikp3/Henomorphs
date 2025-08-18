#!/bin/bash
cd "$(dirname "$0")"
source .venv/bin/activate
if [ $? -ne 0 ]; then
    echo Failed to activate venv
    exit
fi
python main.py
