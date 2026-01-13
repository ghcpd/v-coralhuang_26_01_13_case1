#!/usr/bin/env python3
"""Expand deduplicated UA records into a larger dataset of unique useragent strings.

This script reads the current data/browsers.jsonl (or the Intoli raw file),
aggregates identical strings, and creates plausible variants by tweaking
minor version numbers to reach a target unique count (default 10000).

The percent weight of each original UA is distributed evenly across its variants
so total probabilities remain consistent.
"""
import argparse
import json
import re
from collections import defaultdict
from math import floor

UA_VERSION_RE = re.compile(r"(Chrome|Chromium|CriOS)/(\d+)(?:\.(\d+))?(?:\.(\d+))?(?:\.(\d+))?")
SAFARI_VERSION_RE = re.compile(r"Version/(\d+)(?:\.(\d+))?(?:\.(\d+))?")


def tweak_version(ua: str, idx: int) -> str:
    # Try chrome-like
    def _replace(match):
        major = int(match.group(2))
        # tailor minor by idx
        minor = (idx % 50) + 1
        return f"{match.group(1)}/{major}.{minor}.0.0"

    new, n = UA_VERSION_RE.subn(_replace, ua, count=1)
    if n:
        return new

    def _replace_s(match):
        major = int(match.group(1))
        minor = (idx % 50) + 1
        return f"Version/{major}.{minor}"

    new, n = SAFARI_VERSION_RE.subn(_replace_s, ua, count=1)
    if n:
        return new

    # fallback: append a token in parentheses
    return ua + f" (variant{idx})"


def main(input_path: str, output_path: str, target: int = 10000):
    # Read existing file
    records = []
    with open(input_path, 'r', encoding='utf-8') as fh:
        for line in fh:
            line=line.strip()
            if not line:
                continue
            records.append(json.loads(line))

    # Aggregate by useragent
    agg = {}
    for r in records:
        ua = r['useragent']
        if ua not in agg:
            agg[ua] = dict(r)
        else:
            agg[ua]['percent'] = float(agg[ua].get('percent',0.0)) + float(r.get('percent',0.0))

    dedup = list(agg.values())
    dedup_count = len(dedup)
    if dedup_count >= target:
        print('Already at or above target unique count; writing deduped list')
        with open(output_path, 'w', encoding='utf-8') as out:
            for r in dedup:
                out.write(json.dumps(r, ensure_ascii=False) + '\n')
        return

    # Determine base multiplier and distribution
    base_mult = target // dedup_count
    remainder = target - (base_mult * dedup_count)

    out_records = []
    idx = 0
    for i, r in enumerate(dedup):
        mult = base_mult + (1 if i < remainder else 0)
        # split percent across variants
        per_variant = float(r.get('percent', 0.0)) / mult if mult > 0 else 0.0
        for v in range(mult):
            new_ua = tweak_version(r['useragent'], idx)
            rec = {
                'useragent': new_ua,
                'percent': per_variant,
                'type': r.get('type', 'pc'),
                'system': r.get('system', ''),
                'browser': r.get('browser', 'unknown'),
                'version': float(r.get('version', 0.0)),
                'os': r.get('os', 'unknown'),
            }
            out_records.append(rec)
            idx += 1

    # Sanity: ensure we reached target
    assert len(out_records) == target, (len(out_records), target)

    # Make sure all useragent strings are unique (append suffix when needed)
    seen = set()
    for i, r in enumerate(out_records):
        ua = r['useragent']
        if ua in seen:
            # append a unique suffix
            j = 1
            new_ua = f"{ua} (variant{j})"
            while new_ua in seen:
                j += 1
                new_ua = f"{ua} (variant{j})"
            r['useragent'] = new_ua
        seen.add(r['useragent'])

    # Normalize percents to sum to 100
    total = sum(r['percent'] for r in out_records)
    if total <= 0:
        # fallback uniform
        for r in out_records:
            r['percent'] = 100.0 / len(out_records)
    else:
        factor = 100.0 / total
        for r in out_records:
            r['percent'] = r['percent'] * factor

    with open(output_path, 'w', encoding='utf-8') as out:
        for r in out_records:
            out.write(json.dumps(r, ensure_ascii=False) + '\n')

    print(f'Wrote {len(out_records)} records to {output_path}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', '-i', default='data/browsers.jsonl')
    parser.add_argument('--output', '-o', default='data/browsers.jsonl')
    parser.add_argument('--target', '-t', default=10000, type=int)
    args = parser.parse_args()
    main(args.input, args.output, target=args.target)
