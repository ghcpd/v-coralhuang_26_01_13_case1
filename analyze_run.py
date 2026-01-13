from utils import load

data = load()
print('total entries:', len(data))

# Default instance filters
browsers = ["chrome", "firefox", "safari", "edge"]
os = ["win10", "macos", "linux", "android", "ios", "other"]
platforms = ["pc", "mobile", "tablet"]

filtered = [x for x in data if x['browser'] in browsers and x['os'] in os and x['type'] in platforms]
print('filtered entries (defaults + all OSes):', len(filtered))

# Count per browser
from collections import Counter
print('by browser:', Counter(x['browser'] for x in data))
print('by type:', Counter(x['type'] for x in data))
print('by os:', Counter(x['os'] for x in data))

ua_counts = Counter(x['useragent'] for x in data)
print('unique useragents in dataset:', len(ua_counts))
print('most common 10 counts:')
for ua,c in ua_counts.most_common(10):
    print(c)

# For platform=tablet filter
filtered_tablet = [x for x in data if x['type']=='tablet' and x['browser'] in browsers and x['os'] in os]
print('tablet entries matching browsers+os:', len(filtered_tablet))

# Show a small sample of unique tablet UAs
print('\nSample tablet entries:')
for i,x in enumerate(filtered_tablet[:10]):
    print(i, x['useragent'])