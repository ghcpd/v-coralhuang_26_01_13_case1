"""Fetch and process Intoli user-agents dataset."""

import json
import gzip
import urllib.request
import sys

print('Downloading Intoli user-agents dataset...')
url = 'https://raw.githubusercontent.com/intoli/user-agents/main/src/user-agents.json.gz'

try:
    with urllib.request.urlopen(url, timeout=30) as response:
        compressed = response.read()
    
    data = json.loads(gzip.decompress(compressed).decode('utf-8'))
    print(f'Downloaded: {len(data)} user agents')
    
    if data:
        keys = list(data[0].keys())
        print(f'Sample keys: {keys}')
        print(f'Sample record: {json.dumps(data[0], indent=2)}')
    
    # Save for next processing step
    with open('intoli_raw.json', 'w') as f:
        json.dump(data, f)
    print('Saved to intoli_raw.json')
except Exception as e:
    print(f'Error: {e}', file=sys.stderr)
    sys.exit(1)
