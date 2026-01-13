# User-Agent Randomness Fix

## Problem Description

The fake-useragent library had a severe randomness problem:

- **Total UA count**: Only 165 (too few!)
- **Repetition rate**: 85-90% in 1000 samples
- **Root cause**: Outdated data source (techblog.willshouse.com, offline) with insufficient diversity

## Solution Overview

Upgraded to **Intoli user-agents dataset**:
- **Data source**: https://github.com/intoli/user-agents
- **Raw data**: https://raw.githubusercontent.com/intoli/user-agents/main/src/user-agents.json.gz
- **Contains**: ~10,000 user agent entries based on actual browser traffic
- **Format**: Migrated from `browsers.json` (JSON array) to `browsers.jsonl` (JSONlines)
- **Selection**: Implemented weighted random selection using Intoli's frequency weights

## Improvements

- **UA count**: Increased from 165 to 10,000 (60x improvement)
- **Repetition rate**: Improved from 85-90% to ~70% (still high due to duplicate UAs in source data)
- **Data quality**: Real user agents from actual traffic patterns
- **Weighted selection**: Uses frequency weights for more realistic distribution

## How to Run Tests

### Windows
```cmd
run_tests.bat
```

### Manual
```bash
python test_simple.py
```

## Test Results

- ✅ UA count increased to 10,000
- ✅ All browser methods work (chrome, firefox, safari, edge, random)
- ✅ Device type filtering works (pc, mobile, tablet)
- ✅ Data structure preserved
- ⚠️ Repetition rate still ~70% due to source data having only ~2401 unique UAs

## Data Update Process

To fetch and update the user agent data:

1. Download the latest data:
   ```bash
   curl -s https://raw.githubusercontent.com/intoli/user-agents/main/src/user-agents.json.gz | gunzip > user-agents.json
   ```

2. Convert to our format:
   ```bash
   python convert_data.py
   ```

3. The `data/browsers.jsonl` file will be updated with the latest data.

## Credits

- **Intoli user-agents dataset**: https://github.com/intoli/user-agents
- Original fake-useragent library structure preserved