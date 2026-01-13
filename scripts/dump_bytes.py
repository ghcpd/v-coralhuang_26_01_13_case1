for fn in ('fake.py', 'utils.py'):
    p = open(fn, 'rb').read(300)
    print(fn, repr(p[:40]))
    print(list(p[:40]))
    print()