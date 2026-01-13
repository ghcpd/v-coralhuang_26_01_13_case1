import json
from pathlib import Path
p = Path('data/browsers.jsonl')
seen = set()
with p.open('r', encoding='utf-8') as fh:
    for line in fh:
        obj = json.loads(line)
        seen.add(obj['useragent'])
print('total lines:', sum(1 for _ in open(p, 'r', encoding='utf-8')))
print('unique useragents:', len(seen))