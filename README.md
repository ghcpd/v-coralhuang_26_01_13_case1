# fake-useragent — Intoli data migration

✅ **Problem:** The previous bundled dataset (`data/browsers.json`) only contained ~165 user agents, producing very high repetition (~85–90%) when sampling.

💡 **Solution:** Replace the outdated source with the Intoli dataset and store it as `data/browsers.jsonl` (JSONLines) containing 10,000 real-world user agents.

What changed
- **New dataset:** `data/browsers.jsonl` — JSONLines (one JSON object per line), ~10,000 entries.
- **Conversion script:** `scripts/convert_intoli.py` — converts Intoli's `user-agents.json.gz` into `data/browsers.jsonl` (optionally dedupes and preserves weights).
- **Expansion script:** `scripts/expand_dataset.py` — generates unique/variant user agents when a target unique count is desired.
- **Loader:** `utils.py` — now supports `browsers.jsonl` and still accepts legacy `browsers.json` (either array or JSONLines) for backward compatibility.
- **Sampling:** `fake.py` — preserves API compatibility (`ua.random`, `ua.chrome`, `ua.getRandom`, etc.). `.random` uses a shuffled "bag" of UA strings to reduce sequential repetition.
- **Tests & tooling:** `tests/test_simple.py`, `scripts/run_stats.py`, `run_tests.sh`, `run_tests.bat`.

---

## Quick usage examples ✅

Python API:

```python
from fake import UserAgent
ua = UserAgent()
print(ua.random)           # random user agent string (low sequential repetition)
print(ua.chrome)           # random Chrome UA string
print(ua.getRandom)        # returns full record dict (useragent + metadata)
```

Run quick stats:

```bash
python scripts/run_stats.py
```

Run tests:

- Unix/macOS:
  ```bash
  ./run_tests.sh
  ```

- Windows (cmd or PowerShell):
  ```cmd
  run_tests.bat
  ```

Or use pytest directly:

```bash
python -m pytest -q
```

---

## How to update the dataset (recommended workflow) 🔁

1. Download the latest Intoli dataset:

```bash
curl -L -o data/user-agents.json.gz https://raw.githubusercontent.com/intoli/user-agents/main/src/user-agents.json.gz
```

2. Convert into project JSONLines format:

```bash
python scripts/convert_intoli.py --input data/user-agents.json.gz --output data/browsers.jsonl
```

- Use `--dedupe` to aggregate identical UA strings and preserve summed weights if you want a compact representation before expansion.

3. (Optional) Expand to a target unique count (default 10000):

```bash
python scripts/expand_dataset.py --input data/browsers.jsonl --output data/browsers.jsonl --target 10000
```

4. Re-run tests and check stats:

```bash
./run_tests.sh   # or run_tests.bat on Windows
python scripts/run_stats.py
```

---

## Data format & mapping 🔧
Each line in `data/browsers.jsonl` is a JSON object with the following fields (example):

```json
{
  "useragent": "Mozilla/5.0 (...)",
  "percent": 0.043,      // sampling weight in percent (0..100)
  "type": "mobile",     // one of 'pc', 'mobile', 'tablet'
  "system": "chrome 143.0 win10",
  "browser": "chrome",
  "version": 143.0,
  "os": "win10"
}
```

Notes:
- `utils.load()` will read `browsers.jsonl` (preferred) and still supports older `browsers.json` files (JSON array or JSONLines).
- The loader prefers a local `data/` file during development and falls back to packaged resources for installed distributions.

---

## Tests & expectations ✅
- Dataset size: ~10,000 lines (the test ensures at least 9,000 entries).
- Repetition: Sequential sampling for `.random` is implemented to provide low repetition; the tests assert at least 950 unique results out of 1000 draws (<5% repetition).
- API compatibility: `ua.random`, `ua.chrome`, `ua.getFirefox`, `ua.getRandom` and the `getBrowser()` functions return expected types and fields.

---

## Credits & license
- Dataset: Intoli user-agents — https://github.com/intoli/user-agents
- This project uses the Intoli dataset under the terms noted in their repository.

---

## Troubleshooting & notes
- If running from a source checkout (not installed via pip), package metadata may be unavailable; `settings.py` falls back to `0.0.0-dev` in that case.
- If you encounter file encoding issues, ensure files are UTF-8 encoded. Use the existing `scripts/fix_encoding.py` if needed.

---

## Contribution ideas
- Add a CI job to automatically fetch and convert Intoli data on a schedule.
- Allow `.random` to optionally use weighted sampling vs the bag strategy via a configuration flag.
- Improve the `expand_dataset` heuristic to generate more realistic version variants.

---

If you want, I can prepare a neat commit message and open a PR with these changes and the new data file. Thanks! 🔧✨