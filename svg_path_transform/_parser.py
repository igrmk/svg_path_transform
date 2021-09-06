import lark as LA
import os
from decimal import Decimal


class _PathTransformer(LA.Transformer):
    def command(self, xs): return [xs[0].value, *xs[1:]]
    def NUMBER(self, x): return float(x.value)
    def SIGNED_NUMBER(self, x): return float(x.value)
    def FLAG(self, x): return int(x.value)
    m = command
    start = list
    xy_arg = list
    n_arg = list
    c_arg = list
    sq_arg = list
    a_arg = list


_script_path = os.path.dirname(os.path.realpath(__file__))
with open(os.path.join(_script_path, 'path.lark'), 'r') as f:
    _grammatic = LA.Lark(f.read())


def parse_path(data):
    return _PathTransformer().transform(_grammatic.parse(data))


def path_to_string(data, sfig=5, ndig=None):
    def to_string(v):
        if isinstance(v, float):
            return _to_significant_figures_and_digits(v, sfig, ndig)
        else:
            return str(v)

    data = [[cmd[0], *[v for vs in cmd[1:] for v in vs]] for cmd in data]
    return ' '.join(to_string(v) for vs in data for v in vs)


def _to_significant_figures_and_digits(v: float, n_figures: int, n_digits: int) -> str:
    n_digits = float('inf') if n_digits is None else n_digits
    d = Decimal(v)
    d = d.quantize(Decimal((0, (), max(d.adjusted() - n_figures + 1, -n_digits))))
    return str(d.quantize(Decimal(1)) if d == d.to_integral() else d.normalize())
