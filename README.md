# Fix: Upgrade UA dataset to Intoli (JSONLines)

✅ Summary
- Problem: the bundled UA dataset was tiny/outdated which produced very high repetition rates (~85-90%).
- Solution: integrate the Intoli `user-agents` dataset (real-world, ~10k entries), convert it to JSONLines (`data/browsers.jsonl`), and update the loader and tests.

Why this change matters
- Realistic scraping/emulation requires diverse UAs and sampling weights.
- Intoli provides ~10k real UAs with frequency weights and device metadata — this reduces repetition dramatically.

---

## What I changed (high level)
- Added a robust conversion/update script: `data/update_from_intoli.py` 🔧
- Loader now prefers `data/browsers.jsonl` and is backwards-compatible with legacy `data/browsers.json` (array or JSONLines) ✅
- Added a small sample dataset: `data/browsers.jsonl.sample` (used when offline)
- Tests: `tests/test_simple.py` — verifies count, repetition rate, browser APIs and device filtering ✅
- One-command test scripts: `run_tests.sh` (unix) and `run_tests.bat` (Windows) ▶️
- Documentation and usage instructions (this README) ✍️

---

## How to run (one command)
- Windows (PowerShell/cmd):
  - run_tests.bat

- macOS / Linux:
  - ./run_tests.sh

Both scripts run the unit tests and print a short dataset-quality summary (UA count and repetition rate over 1000 samples).

---

## How to update the dataset from Intoli (automated)
1. Ensure network access.
2. Run:

   python data/update_from_intoli.py

This downloads Intoli's compressed dataset, converts each record to the project's schema and writes:
- `data/browsers.jsonl` (full dataset, ~10k records)
- `data/browsers.jsonl.sample` (first ~2k records)

After updating, re-run `run_tests.*` to validate the improvement.

Notes: the conversion preserves Intoli's `weight` as `percent` (normalized * 100) and extracts `device`/`browser`/`os` fields required by the library.

---

## Developer notes / compatibility
- Backwards compatible: loader accepts legacy `browsers.json` (JSON array) and the historical JSONLines variant.
- API compatibility: `ua.random`, `ua.chrome`, `ua.firefox`, `ua.getRandom`, and device filters (`platforms=["mobile"]`) behave the same as before.

---

## Data source & credits
- Source: Intoli — https://github.com/intoli/user-agents (BSD-2-Clause)
- Raw data: https://raw.githubusercontent.com/intoli/user-agents/main/src/user-agents.json.gz

Please keep the Intoli attribution when distributing this dataset.

---

## If something goes wrong
- If your local copy is still small (e.g. < 1k entries), run the update script above.
- If you cannot access the network, the package will fall back to the bundled sample in `data/browsers.jsonl.sample`.

---

If you want, I can (a) run the update script now (requires network), or (b) open a PR with these changes and the full Intoli dataset included. Which would you prefer? 
