from math import pi, cos, sin, atan2, sqrt


def _tr_scale_arc_rel(v, t, s):
    sx, sy = s[0], s[1]
    rx, ry = v[0], v[1]
    θ = v[2] * pi / 180
    sweep = v[4]
    kx = sx**2 * (rx**2 * cos(θ)**2 + ry**2 * sin(θ)**2)
    ky = sy**2 * (rx**2 * sin(θ)**2 + ry**2 * cos(θ)**2)
    ks = sx * sy * (rx**2 - ry**2) * sin(2 * θ)
    θ_ = atan2(ks, kx - ky) / 2
    rx_ = rx * ry * sx * sy * sqrt(2 / (kx + ky - sqrt(ks**2 + (kx - ky)**2)))
    ry_ = rx * ry * sx * sy * sqrt(2 / (kx + ky + sqrt(ks**2 + (kx - ky)**2)))
    sweep_ = (sweep + (sx < 0) + (sy < 0)) % 2
    return [rx_, ry_, θ_ * 180 / pi, v[3], sweep_, v[5] * sx, v[6] * sy]


def _tr_scale_arc_abs(v, t, s):
    r = _tr_scale_arc_rel(v, t, s)
    r[5] += t[0]
    r[6] += t[1]
    return r


_tr_scale_dict = {
    'm': lambda v, t, s: [v[0] * s[0], v[1] * s[1]],
    'M': lambda v, t, s: [v[0] * s[0] + t[0], v[1] * s[1] + t[1]],
    'h': lambda v, t, s: [v[0] * s[0]],
    'H': lambda v, t, s: [v[0] * s[0] + t[0]],
    'v': lambda v, t, s: [v[0] * s[1]],
    'V': lambda v, t, s: [v[0] * s[1] + t[1]],
    's': lambda v, t, s: [v[0] * s[0], v[1] * s[1], v[2] * s[0], v[3] * s[1]],
    'S': lambda v, t, s: [
        v[0] * s[0] + t[0], v[1] * s[1] + t[1],
        v[2] * s[0] + t[0], v[3] * s[1] + t[1],
    ],
    'c': lambda v, t, s: [
        v[0] * s[0],        v[1] * s[1],
        v[2] * s[0],        v[3] * s[1],
        v[4] * s[0],        v[5] * s[1],
    ],
    'C': lambda v, t, s: [
        v[0] * s[0] + t[0], v[1] * s[1] + t[1],
        v[2] * s[0] + t[0], v[3] * s[1] + t[1],
        v[4] * s[0] + t[0], v[5] * s[1] + t[1],
    ],
    'a': _tr_scale_arc_rel,
    'A': _tr_scale_arc_abs,
    'l': lambda v, t, s: _tr_scale_dict['m'](v, t, s),
    'L': lambda v, t, s: _tr_scale_dict['M'](v, t, s),
    't': lambda v, t, s: _tr_scale_dict['m'](v, t, s),
    'T': lambda v, t, s: _tr_scale_dict['M'](v, t, s),
    'q': lambda v, t, s: _tr_scale_dict['s'](v, t, s),
    'Q': lambda v, t, s: _tr_scale_dict['S'](v, t, s),
}


def translate_and_scale(d, t=(0, 0), s=(1, 1)):
    first = True

    def inner(vs, t, s):
        nonlocal first
        yield vs[0]
        for x in vs[1:]:
            yield _tr_scale_dict['M' if first else vs[0]](x, t, s)
            first = False
    return [list(inner(vs, t, s)) for vs in d]
