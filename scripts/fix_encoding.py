#!/usr/bin/env python3
"""Fix files that were accidentally written as UTF-16 with null bytes.

This script finds .py files containing a UTF-16 BOM and rewrites them as UTF-8.
"""
import glob

REWRITE = []
for f in glob.glob('**/*.py', recursive=False):
    with open(f, 'rb') as fh:
        b = fh.read(4)
        if b.startswith(b'\xff\xfe') or b.startswith(b'\xfe\xff'):
            REWRITE.append(f)

for f in REWRITE:
    print('Fixing', f)
    # Read using utf-16 and re-write as utf-8 bytes to avoid BOM issues
    with open(f, 'r', encoding='utf-16') as fh:
        txt = fh.read()
    with open(f, 'wb') as fh:
        fh.write(txt.encode('utf-8'))
print('Done')
