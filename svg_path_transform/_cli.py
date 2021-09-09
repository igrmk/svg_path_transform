import sys
import argparse
from lark import LarkError
from ._parser import parse_path, path_to_string
from ._transform import translate_and_scale
from .__version__ import __version__


def _main():
    parser = argparse.ArgumentParser(prog=__package__, description='SVG path data transformer')
    arg = parser.add_argument
    arg('--dx', metavar='N', type=float, default=0., help='translate x by N')
    arg('--dy', metavar='N', type=float, default=0., help='translate y by N')
    arg('--sx', metavar='N', type=float, default=1., help='scale x by N')
    arg('--sy', metavar='N', type=float, default=1., help='scale y by N')
    arg('--sfig', metavar='N', type=int, default=5, help='round to N significant figures')
    arg('--ndig', metavar='N', type=int, default=None, help='round to N decimal places')
    arg('-v', '--version', action='version', version=f'%(prog)s {__version__}')
    args = parser.parse_args()
    try:
        d = parse_path(sys.stdin.read())
        p = translate_and_scale(d, (args.dx, args.dy), (args.sx, args.sy))
    except LarkError:
        print('Invalid path data', file=sys.stderr)
        return 1
    except Exception as e:
        print(e, file=sys.stderr)
        return 1
    print(path_to_string(p, args.sfig, args.ndig))
