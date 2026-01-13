import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))
from utils import load
import random

data = load()
filtered = [x for x in data if x['browser'] in ['chrome','firefox','safari','edge'] and x['os'] in ['win10','macos','linux','android','ios','other'] and x['type'] in ['pc','mobile','tablet']]

# Build unique list and weights
groups = {}
weights = []
for entry in filtered:
    ua = entry['useragent']
    if ua in groups:
        weights[groups[ua]] += float(entry.get('percent',100.0))
    else:
        groups[ua] = len(weights)
        weights.append(float(entry.get('percent',100.0)))

unique_entries = [None] * len(weights)
for entry in filtered:
    unique_entries[groups[entry['useragent']]] = entry

print('unique pool size:', len(unique_entries))

samples = [random.choice(unique_entries)['useragent'] for _ in range(1000)]
print('unique in samples:', len(set(samples)))
print('top 10 counts:')
from collections import Counter
print(Counter(samples).most_common(10))