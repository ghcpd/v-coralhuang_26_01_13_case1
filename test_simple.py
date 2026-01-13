import json
import subprocess
import sys
from collections import Counter

from fake import UserAgent
from utils import load


def ensure_data_generated() -> None:
    # Run the generator script to produce data/browsers.jsonl (download or synthesize)
    subprocess.run([sys.executable, "scripts/generate_browsers_jsonl.py"], check=True)


def test_data_count_and_structure():
    ensure_data_generated()
    data = load()
    assert isinstance(data, list), "Loaded data must be a list"
    # Expect ~10k entries (we accept anything >= 9000)
    assert len(data) >= 9000, f"Expected ~10000 user agents, got {len(data)}"

    sample = data[0]
    # Check required fields exist and have sensible types
    for key in ("useragent", "percent", "type", "system", "browser", "version", "os"):
        assert key in sample, f"Missing key {key} in data item"
    assert isinstance(sample["useragent"], str)
    assert isinstance(sample["percent"], float)
    assert isinstance(sample["type"], str)
    assert isinstance(sample["browser"], str)


def test_randomness_improvement():
    ua = UserAgent(os=["win10", "macos", "linux", "android", "ios", "other"])  # include all OSes
    samples = [ua.random for _ in range(1000)]
    unique = set(samples)
    unique_count = len(unique)
    repetition_rate = (1000 - unique_count) / 1000 * 100

    print(f"Generated: 1000 samples")
    print(f"Unique: {unique_count} different UAs")
    print(f"Repetition rate: {repetition_rate:.1f}%")

    # Expect repetition rate less than 5%
    assert repetition_rate < 5.0, "Repetition rate did not improve enough"


def test_browser_methods_and_getters():
    ua = UserAgent(os=["win10", "macos", "linux", "android", "ios", "other"])  # include all OSes

    assert isinstance(ua.chrome, str)
    assert isinstance(ua.firefox, str)
    assert isinstance(ua.safari, str)
    assert isinstance(ua.edge, str)
    assert isinstance(ua.random, str)

    chrome_obj = ua.getChrome
    assert isinstance(chrome_obj, dict)
    for key in ("useragent", "percent", "type", "system", "browser", "version", "os"):
        assert key in chrome_obj


def test_device_filtering():
    ua_mobile = UserAgent(platforms=["mobile"], os=["win10", "macos", "linux", "android", "ios", "other"])  # include all OSes
    # getRandom returns the full data object
    obj = ua_mobile.getRandom
    assert obj["type"] == "mobile", "platform filter did not return a mobile UA"

    ua_tablet = UserAgent(platforms=["tablet"], os=["win10", "macos", "linux", "android", "ios", "other"])  # include all OSes
    obj2 = ua_tablet.getRandom
    assert obj2["type"] == "tablet", "platform filter did not return a tablet UA"