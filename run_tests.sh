#!/usr/bin/env bash
set -euo pipefail

# Generate (or download) the Intoli-based dataset and run tests
python3 scripts/generate_browsers_jsonl.py
python3 -m pytest -q

echo
if [ $? -eq 0 ]; then
  echo "✅ All tests passed"
else
  echo "❌ Some tests failed"
fi