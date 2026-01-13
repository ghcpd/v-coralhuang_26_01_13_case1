"""Convert Intoli data to our BrowserUserAgentData schema and generate JSONLines format."""

import json
import re
from typing import Optional

def extract_browser(ua_string: str) -> str:
    """Extract browser name from user agent string."""
    ua_lower = ua_string.lower()
    
    if 'edge' in ua_lower or 'edg/' in ua_lower:
        return 'edge'
    elif 'chrome' in ua_lower and 'chromium' not in ua_lower:
        return 'chrome'
    elif 'firefox' in ua_lower:
        return 'firefox'
    elif 'safari' in ua_lower and 'chrome' not in ua_lower:
        return 'safari'
    elif 'opera' in ua_lower or 'opr/' in ua_lower:
        return 'opera'
    elif 'brave' in ua_lower:
        return 'brave'
    elif 'chromium' in ua_lower:
        return 'chromium'
    else:
        return 'other'

def extract_version(ua_string: str, browser: str) -> float:
    """Extract version from user agent string."""
    patterns = {
        'edge': r'Edg[e/](\d+)',
        'chrome': r'Chrome/(\d+)',
        'firefox': r'Firefox/(\d+)',
        'safari': r'Version/(\d+)',
        'opera': r'OPR/(\d+)',
        'brave': r'Brave/(\d+)',
        'chromium': r'Chromium/(\d+)',
    }
    
    pattern = patterns.get(browser)
    if pattern:
        match = re.search(pattern, ua_string)
        if match:
            try:
                return float(match.group(1))
            except (ValueError, IndexError):
                pass
    
    return 0.0

def extract_os(ua_string: str, platform: str) -> str:
    """Extract and standardize OS name."""
    ua_lower = ua_string.lower()
    
    if 'windows' in ua_lower or 'win' in ua_lower:
        if 'windows nt 6.1' in ua_lower or 'win7' in ua_lower.lower():
            return 'win7'
        else:
            return 'win10'
    elif 'macintosh' in ua_lower or 'mac os x' in ua_lower:
        return 'macos'
    elif 'linux' in ua_lower:
        return 'linux'
    elif 'iphone' in ua_lower or 'ipad' in ua_lower:
        return 'ios'
    elif 'android' in ua_lower:
        return 'android'
    else:
        return 'other'

def convert_intoli_to_schema(intoli_data: dict) -> dict:
    """Convert a single Intoli record to BrowserUserAgentData schema."""
    ua_string = intoli_data.get('userAgent', '')
    browser = extract_browser(ua_string)
    version = extract_version(ua_string, browser)
    os = extract_os(ua_string, intoli_data.get('platform', ''))
    
    # Map device category to our type system
    device_category = intoli_data.get('deviceCategory', '').lower()
    if device_category == 'mobile':
        device_type = 'mobile'
    elif device_category == 'tablet':
        device_type = 'tablet'
    else:
        device_type = 'pc'
    
    # Calculate percentage based on weight
    weight = intoli_data.get('weight', 0.0001)
    percent = min(100.0, weight * 10000)  # Scale weight to percentage
    
    system = f"{browser.title()} {version} {os.title()}"
    
    return {
        'useragent': ua_string,
        'percent': percent,
        'type': device_type,
        'system': system,
        'browser': browser,
        'version': version,
        'os': os,
    }

def main():
    print('Converting Intoli data to BrowserUserAgentData schema...')
    
    with open('intoli_raw.json', 'r') as f:
        intoli_data = json.load(f)
    
    print(f'Processing {len(intoli_data)} records...')
    
    converted = []
    for record in intoli_data:
        try:
            converted_record = convert_intoli_to_schema(record)
            converted.append(converted_record)
        except Exception as e:
            print(f'Warning: Failed to convert record - {e}')
            continue
    
    print(f'Successfully converted {len(converted)} records')
    
    # Write to JSONLines format
    output_path = 'data/browsers.jsonl'
    with open(output_path, 'w', encoding='utf-8') as f:
        for record in converted:
            f.write(json.dumps(record) + '\n')
    
    print(f'Saved {len(converted)} records to {output_path}')
    
    # Print sample
    if converted:
        print('\nSample records:')
        for i, record in enumerate(converted[:3]):
            print(f"  Record {i+1}: {record['useragent'][:80]}... (browser={record['browser']}, version={record['version']}, type={record['type']})")

if __name__ == '__main__':
    main()
