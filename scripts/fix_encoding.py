"""Fix Python source files that were accidentally saved with UTF-16 encoding.

This script scans the repository for `.py` files and, when a file begins with a
UTF-16 BOM or contains null bytes, decodes it as UTF-16 and re-saves it as
UTF-8 (without BOM). Run it when you see "source code string cannot contain null
bytes" errors during import.
"""
from pathlib import Path

root = Path(__file__).parent.parent
changed = []
for path in sorted(root.glob("*.py")) + sorted(root.glob("scripts/*.py")):
    b = path.read_bytes()
    if b.startswith(b"\xff\xfe") or b.startswith(b"\xfe\xff") or b.find(b"\x00") != -1:
        try:
            text = b.decode("utf-16")
        except Exception:
            # If decoding as utf-16 fails, skip
            continue
        path.write_text(text, encoding="utf-8")
        changed.append(path.name)

if changed:
    print("Re-saved as UTF-8:", changed)
else:
    print("No files needed re-encoding.")