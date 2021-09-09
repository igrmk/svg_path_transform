import sys

if sys.version_info < (3, 8):
    from importlib_metadata import distribution
else:
    from importlib.metadata import distribution

_fallback = '(devel)'

try:
    dist = distribution(__package__)
    if dist.locate_file('__version__.py') == __file__:
        __version__ = dist.version
    else:
        __version__ = _fallback
except:
    __version__ = _fallback
