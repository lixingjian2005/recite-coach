#!/bin/bash
cd "$(dirname "$0")"
echo "Recite Coach — starting local server..."
python3 serve.py || python serve.py
