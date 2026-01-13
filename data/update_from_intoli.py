"""Download Intoli `user-agents.json.gz`, convert to the project's JSONLines schema,
and write `data/browsers.jsonl` plus a smaller `data/browsers.jsonl.sample`.

This script is standalone and uses only the standard library so it can run in CI or
on developer machines without extra dependencies.

Usage:
    python data/update_from_intoli.py  # downloads and writes full `browsers.jsonl`
    python data/update_from_intoli.py --sample-only  # writes only the sample file

If the network is unavailable, the script exits with a non-zero status and prints
instructions to update the data manually.
"""
from __future__ import annotations

import gzip
import io
import json
import re
import sys
import urllib.request
from typing import Iterable

INTOLI_URL = (
    "https://raw.githubusercontent.com/intoli/user-agents/main/src/user-agents.json.gz"
)
OUT_FULL = "data/browsers.jsonl"
OUT_SAMPLE = "data/browsers.jsonl.sample"
SAMPLE_SIZE = 2000

# Minimal browser detection regexes (covers common desktop/mobile browsers)
BROWSER_REGEXES = [
    (re.compile(r"OPR/([0-9]+)"), "opera"),
    (re.compile(r"Opera/([0-9]+)"), "opera"),
    (re.compile(r"Edg(?:iOS|A)?/([0-9]+)"), "edge"),
    (re.compile(r"Chrome/([0-9]+)"), "chrome"),
    (re.compile(r"CriOS/([0-9]+)"), "chrome"),
    (re.compile(r"Firefox/([0-9]+)"), "firefox"),
    (re.compile(r"FxiOS/([0-9]+)"), "firefox"),
    (re.compile(r"Version/([0-9]+).*Safari/"), "safari"),
    (re.compile(r"Safari/([0-9]+)"), "safari"),
]

OS_MAP = [
    (re.compile(r"Windows NT 10|Windows 10", re.I), "win10"),
    (re.compile(r"Windows NT 6|Windows 7|Windows NT 5", re.I), "win"),
    (re.compile(r"Android", re.I), "android"),
    (re.compile(r"iPhone|iPad|iOS", re.I), "ios"),
    (re.compile(r"Mac OS X|Macintosh", re.I), "macos"),
    (re.compile(r"Linux", re.I), "linux"),
]


def detect_browser(ua: str) -> tuple[str, float]:
    """Return (browser-name, major-version-as-float).

    Browser detection is intentionally conservative — we only need values that
    match the expectations in `fake.py` (lowercase names and a numeric version).
    """
    for rx, name in BROWSER_REGEXES:
        m = rx.search(ua)
        if m:
            try:
                ver = float(m.group(1))
            except Exception:
                ver = 0.0
            return name, float(int(ver))
    return "other", 0.0


def detect_os(ua: str) -> str:
    for rx, mapped in OS_MAP:
        if rx.search(ua):
            return mapped
    return "other"


def normalize_type(device_category: str | None, ua: str) -> str:
    if device_category:
        if device_category in ("mobile", "desktop", "tablet"):
            return device_category if device_category != "desktop" else "pc"
    # fallback heuristics
    if "Mobile" in ua or "Android" in ua or "iPhone" in ua:
        return "mobile"
    if "iPad" in ua or "Tablet" in ua:
        return "tablet"
    return "pc"


def convert_intoli_item(item: dict) -> dict:
    ua = item.get("userAgent") or item.get("useragent") or ""
    weight = float(item.get("weight", 0.0))
    device_category = item.get("deviceCategory")

    browser, version = detect_browser(ua)
    return {
        "useragent": ua,
        "percent": float(weight) * 100.0,
        "type": normalize_type(device_category, ua),
        "system": item.get("platform", ""),
        "browser": browser,
        "version": float(version),
        "os": detect_os(ua),
    }


def download_and_convert() -> Iterable[dict]:
    """Download Intoli gz and yield converted records (generator)."""
    with urllib.request.urlopen(INTOLI_URL, timeout=30) as resp:
        compressed = resp.read()

    with gzip.GzipFile(fileobj=io.BytesIO(compressed)) as gz:
        data_bytes = gz.read()

    arr = json.loads(data_bytes.decode("utf-8"))
    for item in arr:
        yield convert_intoli_item(item)


def write_jsonlines(path: str, records: Iterable[dict]) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        for rec in records:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")


def main(argv: list[str]) -> int:
    sample_only = "--sample-only" in argv
    try:
        records = list(download_and_convert())
    except Exception as exc:
        print("Failed to download/convert Intoli data:", exc)
        print(
            "To update manually: download the gz from:\n  ",
            INTOLI_URL,
            "\nthen run this script again on a machine with network access.",
        )
        return 2

    if not records:
        print("No records found in Intoli dataset.")
        return 3

    # write sample always
    write_jsonlines(OUT_SAMPLE, records[:SAMPLE_SIZE])
    print(f"Wrote sample {OUT_SAMPLE} ({min(SAMPLE_SIZE, len(records))} records)")

    if sample_only:
        return 0

    write_jsonlines(OUT_FULL, records)
    print(f"Wrote full {OUT_FULL} ({len(records)} records)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
