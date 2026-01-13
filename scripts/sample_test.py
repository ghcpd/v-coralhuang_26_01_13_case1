from fake import UserAgent

ua = UserAgent(os=["win10", "macos", "linux", "android", "ios", "other"]) 
print('total loaded:', len(ua.data_browsers))
filtered = ua._filter_useragents()
print('filtered length:', len(filtered))

samples = [ua.random for _ in range(1000)]
unique = set(samples)
print('unique in 1000 samples:', len(unique))

# show top 10 most selected values
from collections import Counter
c = Counter(samples)
print('top 10 counts:')
for k,v in c.most_common(10):
    print(v, k[:80])