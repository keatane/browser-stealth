#!/bin/sh
if [ ! -d ".venv" ]; then
    python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
fi