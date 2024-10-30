import sys
import argparse
import traceback
from lark import LarkError
from ._parser import parse_path, path_to_string
from ._translate_and_scale import translate_and_scale
from ._segmentize import segmentize
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
    arg('--seg', metavar='N', type=float, default=None,
        help='convert to straight line segments with a given max distance')
    arg('--pretty-print', action='store_true', help='pretty print the input path and exit')
    arg('-v', '--version', action='version', version=f'%(prog)s {__version__}')
    args = parser.parse_args()
    try:
        d = parse_path(sys.stdin.read())
        if args.pretty_print:
            for command in d:
                print(command[0])
                for params in command[1:]:
                    print('    ' + ' '.join(str(x) for x in params))
            sys.exit(0)
        if args.seg is not None:
            d = segmentize(d, args.seg)
        d = translate_and_scale(d, (args.dx, args.dy), (args.sx, args.sy))
    except LarkError:
        print('Invalid path data', file=sys.stderr)
        return 1
    except Exception:
        traceback.print_exc()
        return 1
    print(path_to_string(d, args.sfig, args.ndig))
