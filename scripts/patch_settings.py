new = '''"""General library settings."""

from importlib import metadata


try:
    # When the package is not installed in the current environment (for example during
    # local development or tests), `metadata.version` will raise PackageNotFoundError.
    # Fall back to a sensible default so imports don't fail.
    __version__ = metadata.version("fake-useragent")
except metadata.PackageNotFoundError:
    __version__ = "0.0.0"


REPLACEMENTS = {

    " ": "",

    "_": "",

}



OS_REPLACEMENTS = {

    "windows": ["win10", "win7"],

}



SHORTCUTS = {

    "microsoft edge": "edge",

    "google": "chrome",

    "googlechrome": "chrome",

    "ff": "firefox",

}
'''
open('settings.py','w', encoding='utf-8').write(new)
print('Patched settings.py')