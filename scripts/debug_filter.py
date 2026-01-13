import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))
from fake import UserAgent

ua = UserAgent(os=["win10", "macos", "linux", "android", "ios", "other"]) 
print('total loaded:', len(ua.data_browsers))
filtered = ua._filter_useragents()
print('filtered length:', len(filtered))

# Count unique useragents in the filtered list
unique_filtered = {x['useragent'] for x in filtered}
print('unique in filtered:', len(unique_filtered))

# Show top-10 browsers in filtered
from collections import Counter
print('browser counts:', Counter(x['browser'] for x in filtered))
print('unique per browser:')
for b in sorted(set(x['browser'] for x in filtered)):
    print(' ', b, len({x['useragent'] for x in filtered if x['browser']==b}))
print('type counts:', Counter(x['type'] for x in filtered))
print('os counts:', Counter(x['os'] for x in filtered))