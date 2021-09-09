import sys
from os.path import join

if sys.version_info < (3, 8):
    from importlib_metadata import distribution
else:
    from importlib.metadata import distribution

_fallback = '(devel)'

try:
    dist = distribution(__package__)
    installed = str(dist.locate_file(join(__package__, '__version__.py')))
    if installed == __file__:
        __version__ = dist.version
    else:
        __version__ = _fallback
except:
    __version__ = _fallback
