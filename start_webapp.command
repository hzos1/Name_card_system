#!/bin/bash
cd "$(dirname "$0")"

echo "======================================"
echo "Name Card WebApp"
echo "======================================"

if [ ! -f ".venv/bin/python" ]; then
    echo "[ERROR] Cannot find .venv/bin/python"
    echo "Please run: python3 -m venv .venv && .venv/bin/pip install -r requirements.txt"
    read -r -p "Press Enter to close..."
    exit 1
fi

echo "[1/2] Installing required packages..."
".venv/bin/python" -m pip install -r requirements.txt

echo "[2/2] Starting web app..."
open "http://127.0.0.1:5000"
".venv/bin/python" app.py
