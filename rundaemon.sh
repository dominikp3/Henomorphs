#!/bin/bash
cd "$(dirname "$0")"
source .venv/bin/activate
if [ $? -ne 0 ]; then
    exit 100
fi
python daemon.py $1 $2 $3
