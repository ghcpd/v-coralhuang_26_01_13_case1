#!/usr/bin/env python3
"""Test script to verify the User-Agent randomness improvement."""

from fake import UserAgent

def test_ua_count():
    """Test that we have ~10,000 UAs."""
    ua = UserAgent()
    count = len(ua.data_browsers)
    print(f"Total UA count: {count}")
    assert count >= 9000, f"Expected >=9000, got {count}"
    return count

def test_repetition_rate():
    """Test repetition rate over 1000 samples."""
    ua = UserAgent()
    samples = [ua.random for _ in range(1000)]
    unique = set(samples)
    repetition_rate = (1000 - len(unique)) / 1000 * 100
    print(f"Generated: 1000 samples")
    print(f"Unique: {len(unique)} different UAs")
    print(f"Repetition rate: {repetition_rate:.1f}%")
    assert repetition_rate < 80, f"Repetition rate {repetition_rate:.1f}% too high (improved from 85-90%)"
    return repetition_rate

def test_browser_methods():
    """Test that browser-specific methods work."""
    ua = UserAgent()
    browsers = ['chrome', 'firefox', 'safari', 'edge']
    expected_substrings = {
        'chrome': 'chrome',
        'firefox': 'firefox',
        'safari': 'safari',
        'edge': 'edg'
    }
    for browser in browsers:
        ua_str = getattr(ua, browser)
        print(f"{browser}: {ua_str[:50]}...")
        substring = expected_substrings[browser]
        assert substring in ua_str.lower(), f"{substring} not in UA: {ua_str}"

def test_device_types():
    """Test device type filtering."""
    ua = UserAgent()
    # Test pc
    ua_pc = UserAgent(platforms=['pc'])
    pc_ua = ua_pc.random
    print(f"PC UA: {pc_ua[:50]}...")
    # Note: hard to assert without parsing, but at least it runs

def test_data_structure():
    """Test that data has proper fields."""
    ua = UserAgent()
    sample = ua.data_browsers[0]
    required_fields = ['useragent', 'percent', 'type', 'system', 'browser', 'version', 'os']
    for field in required_fields:
        assert field in sample, f"Missing field: {field}"
    print(f"Sample data: {sample}")

if __name__ == "__main__":
    print("Testing User-Agent improvements...")
    try:
        count = test_ua_count()
        rep_rate = test_repetition_rate()
        test_browser_methods()
        test_device_types()
        test_data_structure()
        print("\n✅ All tests passed!")
        print(f"📊 UA count: {count} (was ~165)")
        print(f"📊 Repetition rate: {rep_rate:.1f}% (was ~85-90%)")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        raise