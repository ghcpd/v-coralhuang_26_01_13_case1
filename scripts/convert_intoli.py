#!/usr/bin/env python3
"""Convert Intoli user-agents JSON (gz) to JSONLines formatted for this project.

Writes to data/browsers.jsonl with one JSON object per line using the project's
schema (lowercase keys):
  useragent, percent, type, system, browser, version, os

This does best-effort mapping of Intoli fields.
"""
import argparse
import gzip
import json
import re
from typing import Any, Dict

BROWSER_PATTERNS = {
    "chrome": re.compile(r"(Chrome|Chromium|CriOS)/(\d+(?:\.\d+)*)"),
    "firefox": re.compile(r"Firefox/(\d+(?:\.\d+)*)"),
    "safari": re.compile(r"Version/(\d+(?:\.\d+)*)"),
    "edge": re.compile(r"Edg/(\d+(?:\.\d+)*)"),
    "opera": re.compile(r"(Opera|OPR)/(\d+(?:\.\d+)*)"),
    "ie": re.compile(r"MSIE (\d+(?:\.\d+)*)|Trident/.*rv:(\d+(?:\.\d+)*)"),
}

OS_PATTERNS = {
    "win": re.compile(r"Windows NT|Win32|Win64|WOW64|Win" , re.I),
    "macos": re.compile(r"Macintosh|Mac OS X|Mac_PowerPC", re.I),
    "linux": re.compile(r"Linux", re.I),
    "android": re.compile(r"Android", re.I),
    "ios": re.compile(r"iPhone|iPad|iPod|iOS", re.I),
}


def extract_browser_and_version(ua: str, item: Dict[str, Any]) -> (str, float):
    # Try explicit fields first
    for key in ("browserName", "browser", "name", "family"):
        val = item.get(key)
        if isinstance(val, str) and val:
            name = val.lower()
            # Extract any number in version fields
            version = item.get("browserVersion") or item.get("version") or item.get("browserVersionRaw")
            if isinstance(version, str):
                m = re.search(r"(\d+(?:\.\d+)*)", version)
                if m:
                    try:
                        return name, float(m.group(1))
                    except Exception:
                        return name, 0.0
            return name, 0.0

    # Fallback to regex over UA string
    for name, pattern in BROWSER_PATTERNS.items():
        m = pattern.search(ua)
        if m:
            # group may contain version in group 2 or 1
            ver = None
            for g in m.groups()[::-1]:
                if g:
                    ver = g
                    break
            try:
                return name, float(ver.split(".")[0]) if ver else 0.0
            except Exception:
                return name, 0.0
    return "unknown", 0.0


def detect_os(ua: str, item: Dict[str, Any]) -> str:
    for key in ("os", "platform", "operatingSystem", "osName"):
        val = item.get(key)
        if isinstance(val, str) and val:
            v = val.lower()
            if "windows" in v:
                return "win10"
            if "mac" in v or "darwin" in v:
                return "macos"
            if "linux" in v:
                return "linux"
            if "android" in v:
                return "android"
            if "ios" in v or "iphone" in v or "ipad" in v:
                return "ios"
    # Fallback regex on UA
    for name, pattern in OS_PATTERNS.items():
        if pattern.search(ua):
            if name == "win":
                return "win10"
            return name
    return "unknown"


def map_device_type(item: Dict[str, Any], ua: str) -> str:
    # Intoli uses deviceCategory with values desktop/mobile/tablet
    dc = item.get("deviceCategory") or item.get("device") or item.get("deviceType")
    if isinstance(dc, str):
        d = dc.lower()
        if d == "desktop":
            return "pc"
        if d in ("mobile", "tablet"):
            return d
    # Fallback to UA parsing
    if "Mobile" in ua or "Android" in ua or "iPhone" in ua:
        return "mobile"
    if "iPad" in ua or "Tablet" in ua:
        return "tablet"
    return "pc"


def map_percent(item: Dict[str, Any]) -> float:
    # Intoli provides probabilities 0..1 under keys such as probability
    for key in ("probability", "prob", "weight", "frequency"):
        val = item.get(key)
        if val is None:
            continue
        try:
            f = float(val)
            # If the value looks like 0..1 probability
            if 0.0 <= f <= 1.0:
                return f * 100.0
            # Otherwise assume it's already percent
            return f
        except Exception:
            continue
    return 100.0


def main(input_path: str, output_path: str, dedupe: bool = False):
    # Read gz or plain JSON
    text = None
    if input_path.endswith('.gz'):
        with gzip.open(input_path, 'rt', encoding='utf-8') as fh:
            text = fh.read()
    else:
        with open(input_path, 'r', encoding='utf-8') as fh:
            text = fh.read()

    items = json.loads(text)
    if dedupe:
        # Aggregate entries by useragent string to avoid duplicate UA strings causing
        # skewed sampling. We'll sum percent and pick most common values for other
        # categorical fields.
        agg = {}
        for it in items:
            ua = it.get('userAgent') or it.get('useragent') or it.get('ua') or ''
            if not ua:
                continue
            browser, version = extract_browser_and_version(ua, it)
            percent = map_percent(it)
            device_type = map_device_type(it, ua)
            os_val = detect_os(ua, it)
            system = f"{browser} {version} {os_val}"
            if ua not in agg:
                agg[ua] = {
                    "useragent": ua,
                    "percent": float(percent),
                    "type_counts": {device_type: 1},
                    "browser_counts": {browser: 1},
                    "version_candidates": {version: 1},
                    "os_counts": {os_val: 1},
                }
            else:
                a = agg[ua]
                a["percent"] += float(percent)
                a["type_counts"][device_type] = a["type_counts"].get(device_type, 0) + 1
                a["browser_counts"][browser] = a["browser_counts"].get(browser, 0) + 1
                a["version_candidates"][version] = a["version_candidates"].get(version, 0) + 1
                a["os_counts"][os_val] = a["os_counts"].get(os_val, 0) + 1

        def pick_most_common(counts: dict):
            return max(counts.items(), key=lambda x: x[1])[0]

        with open(output_path, 'w', encoding='utf-8') as out:
            for ua, a in agg.items():
                browser = pick_most_common(a["browser_counts"])
                device_type = pick_most_common(a["type_counts"])
                os_val = pick_most_common(a["os_counts"])
                # pick median-ish version by choosing the candidate with highest count then highest value
                versions = a["version_candidates"]
                version = max(sorted(versions.items(), key=lambda x: (x[1], x[0])))[0]
                record = {
                    "useragent": ua,
                    "percent": float(a["percent"]),
                    "type": device_type,
                    "system": f"{browser} {version} {os_val}",
                    "browser": browser,
                    "version": float(version),
                    "os": os_val,
                }
                out.write(json.dumps(record, ensure_ascii=False) + "\n")
    else:
        with open(output_path, 'w', encoding='utf-8') as out:
            for it in items:
                ua = it.get('userAgent') or it.get('useragent') or it.get('ua') or ''
                if not ua:
                    continue
                browser, version = extract_browser_and_version(ua, it)
                percent = map_percent(it)
                device_type = map_device_type(it, ua)
                os_val = detect_os(ua, it)
                system = f"{browser} {version} {os_val}"
                record = {
                    "useragent": ua,
                    "percent": float(percent),
                    "type": device_type,
                    "system": system,
                    "browser": browser,
                    "version": float(version),
                    "os": os_val,
                }
                out.write(json.dumps(record, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert Intoli dataset to JSONLines")
    parser.add_argument('--input', '-i', default='data/user-agents.json.gz')
    parser.add_argument('--output', '-o', default='data/browsers.jsonl')
    parser.add_argument('--dedupe', action='store_true', help='Aggregate identical useragent strings into a single entry (sums percent)')
    args = parser.parse_args()
    main(args.input, args.output, dedupe=args.dedupe)
