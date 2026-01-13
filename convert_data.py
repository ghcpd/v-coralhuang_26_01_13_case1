import json
import re
from typing import Dict, Any

def parse_user_agent(ua_string: str) -> Dict[str, Any]:
    """Parse user agent string to extract browser, version, os."""
    # Simple parser
    ua = ua_string.lower()

    # Browser detection
    browser = None
    version = None

    if 'chrome' in ua and 'edg' not in ua:
        browser = 'chrome'
        match = re.search(r'chrome/([\d.]+)', ua)
        if match:
            version = float(match.group(1).split('.')[0])
    elif 'firefox' in ua:
        browser = 'firefox'
        match = re.search(r'firefox/([\d.]+)', ua)
        if match:
            version = float(match.group(1).split('.')[0])
    elif 'safari' in ua and 'chrome' not in ua:
        browser = 'safari'
        match = re.search(r'version/([\d.]+)', ua)
        if match:
            version = float(match.group(1).split('.')[0])
    elif 'edg' in ua:
        browser = 'edge'
        match = re.search(r'edg/([\d.]+)', ua)
        if match:
            version = float(match.group(1).split('.')[0])
    elif 'opera' in ua:
        browser = 'opera'
        match = re.search(r'opera/([\d.]+)', ua) or re.search(r'opr/([\d.]+)', ua)
        if match:
            version = float(match.group(1).split('.')[0])

    if browser is None:
        browser = 'chrome'  # fallback
    if version is None:
        version = 100.0  # fallback

    # OS detection
    os = None
    if 'windows nt' in ua:
        os = 'win10'
    elif 'mac os x' in ua or 'macintosh' in ua:
        os = 'macos'
    elif 'linux' in ua:
        os = 'linux'
    elif 'android' in ua:
        os = 'linux'  # approximate
    elif 'ios' in ua or 'iphone' in ua or 'ipad' in ua:
        os = 'macos'  # approximate
    else:
        os = 'win10'  # fallback

    # System string
    system = f"{browser.capitalize()} {version} {os.replace('win10', 'Windows').replace('macos', 'Mac OS X').replace('linux', 'Linux')}"

    return {
        'browser': browser,
        'version': version,
        'os': os,
        'system': system
    }

# Load Intoli data
with open('user-agents.json', 'r', encoding='utf-8') as f:
    intoli_data = json.load(f)

# Convert to our format
converted_data = []
for item in intoli_data:
    ua = item['userAgent']
    parsed = parse_user_agent(ua)

    # Map deviceCategory to type
    device_map = {
        'desktop': 'pc',
        'mobile': 'mobile',
        'tablet': 'tablet'
    }
    ua_type = device_map.get(item['deviceCategory'], 'pc')

    converted_item = {
        'useragent': ua,
        'percent': item['weight'] * 100,  # Convert to percent (0-100)
        'type': ua_type,
        'system': parsed['system'],
        'browser': parsed['browser'],
        'version': parsed['version'],
        'os': parsed['os']
    }
    converted_data.append(converted_item)

# Write to JSONlines
with open('data/browsers.jsonl', 'w', encoding='utf-8') as f:
    for item in converted_data:
        f.write(json.dumps(item) + '\n')

print(f"Converted {len(converted_data)} entries to data/browsers.jsonl")