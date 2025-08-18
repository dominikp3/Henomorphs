#!/bin/bash
cd "$(dirname "$0")"

function nopy
{
    echo Python not found. Ensure You have python and pip correctly installed and added to PATH
    exit
}

command -v python >/dev/null 2>&1 || nopy
command -v pip >/dev/null 2>&1 || nopy

if [ -d ".venv" ]; then
    read -p "venv is already exist. Delete and reinstall? [y/n]: " input
    if [ "$input" != "y" ]; then
        exit
    else
        rm -rf .venv
    fi
fi

echo Creating venv
python -m venv .venv
if [ $? -ne 0 ]; then
    echo Failed to create venv
    exit
fi
echo Executing update script
source update.sh --skip-pull
