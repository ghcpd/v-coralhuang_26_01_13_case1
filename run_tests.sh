#!/usr/bin/env bash
set -euo pipefail

echo "Running unit tests..."
python -m unittest discover -v tests

echo
python - <<'PY'
from utils import load
from fake import UserAgent

data = load()
print(f"UA count: {len(data)}")
ua = UserAgent()
samples = [ua.random for _ in range(1000)]
unique = len(set(samples))
print(f"Generated 1000 samples — unique: {unique}, repetition_rate: {(1000-unique)/1000:.3f}")
PY

echo
echo "To update the dataset from Intoli: python data/update_from_intoli.py"
