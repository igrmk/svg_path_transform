from math import sqrt, ceil, pi, cos, sin, acos, copysign


def _angle(a, b):
    n = acos((a[0] * b[0] + a[1] * b[1]) / sqrt((a[0] ** 2 + a[1] ** 2) * (b[0] ** 2 + b[1] ** 2)))
    sign = a[0] * b[1] - a[1] * b[0]
    return copysign(1, sign) * n


def _dist(a, b):
    return sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)


def _make_relative(ps):
    for i in range(len(ps) - 1, 0, -1):
        ps[i][0] -= ps[i - 1][0]
        ps[i][1] -= ps[i - 1][1]


def _split_quadratic_bezier(v, t):
    x1, y1, x2, y2, x3, y3 = v
    x12 = (x2 - x1) * t + x1
    y12 = (y2 - y1) * t + y1
    x23 = (x3 - x2) * t + x2
    y23 = (y3 - y2) * t + y2
    x123 = (x23 - x12) * t + x12
    y123 = (y23 - y12) * t + y12
    return [
        [x1, y1, x12, y12, x123, y123],
        [x123, y123, x23, y23, x3, y3],
    ]


def _split_cubic_bezier(v, t):
    x1, y1, x2, y2, x3, y3, x4, y4 = v
    x12 = (x2 - x1) * t + x1
    y12 = (y2 - y1) * t + y1
    x23 = (x3 - x2) * t + x2
    y23 = (y3 - y2) * t + y2
    x34 = (x4 - x3) * t + x3
    y34 = (y4 - y3) * t + y3
    x123 = (x23 - x12) * t + x12
    y123 = (y23 - y12) * t + y12
    x234 = (x34 - x23) * t + x23
    y234 = (y34 - y23) * t + y23
    x1234 = (x234 - x123) * t + x123
    y1234 = (y234 - y123) * t + y123
    return [
        [x1, y1, x12, y12, x123, y123, x1234, y1234],
        [x1234, y1234, x234, y234, x34, y34, x4, y4],
    ]


def _quadratic_bezier_to_segments(v, d):
    if _dist(v[0:2], v[2:4]) + _dist(v[2:4], v[4:6]) < d:
        return [v[:]]
    bs = _split_quadratic_bezier(v, .5)
    return _quadratic_bezier_to_segments(bs[0], d) + _quadratic_bezier_to_segments(bs[1], d)


def _cubic_bezier_to_segments(v, d):
    if _dist(v[0:2], v[2:4]) + _dist(v[2:4], v[4:6]) + _dist(v[4:6], v[6:8]) < d:
        return [v[:]]
    bs = _split_cubic_bezier(v, .5)
    return _cubic_bezier_to_segments(bs[0], d) + _cubic_bezier_to_segments(bs[1], d)


def _line_to_segments(b, e, d):
    def inner():
        n = max(ceil(_dist(b, e) / d), 1)
        for i in range(1, n + 1):
            t = i / n
            yield [b[0] * (1 - t) + e[0] * t, b[1] * (1 - t) + e[1] * t]

    return list(inner())


def _arc_to_segments(cx, cy, rx, ry, φ, θ1, θ2, d):
    θ12 = (θ1 + θ2) / 2
    x1 = rx * cos(φ) * cos(θ1) - ry * sin(φ) * sin(θ1) + cx
    y1 = rx * sin(φ) * cos(θ1) + ry * cos(φ) * sin(θ1) + cy
    x2 = rx * cos(φ) * cos(θ2) - ry * sin(φ) * sin(θ2) + cx
    y2 = rx * sin(φ) * cos(θ2) + ry * cos(φ) * sin(θ2) + cy
    x12 = rx * cos(φ) * cos(θ12) - ry * sin(φ) * sin(θ12) + cx
    y12 = rx * sin(φ) * cos(θ12) + ry * cos(φ) * sin(θ12) + cy
    if _dist([x1, y1], [x12, y12]) + _dist([x12, y12], [x2, y2]) < d:
        return [[x2, y2]]
    return _arc_to_segments(cx, cy, rx, ry, φ, θ1, θ12, d) + _arc_to_segments(cx, cy, rx, ry, φ, θ12, θ2, d)


def _arc_center_params(x1, y1, x2, y2, large, sweep, rx, ry, φ):
    rx, ry = abs(rx), abs(ry)
    x12 = (x1 - x2) / 2
    y12 = (y1 - y2) / 2
    x1_, y1_ = cos(φ) * x12 + sin(φ) * y12, cos(φ) * y12 - sin(φ) * x12
    Λ = (x1_ / rx) ** 2 + (y1_ / ry) ** 2
    if Λ > 1:
        rx *= sqrt(Λ) * 1.00000001
        ry *= sqrt(Λ) * 1.00000001
    sign = 1 if large != sweep else -1
    denom = rx ** 2 * y1_ ** 2 + ry ** 2 * x1_ ** 2
    nom = rx ** 2 * ry ** 2 - denom
    coeff = sign * sqrt(nom / denom)
    cx_ = coeff * rx * y1_ / ry
    cy_ = -coeff * ry * x1_ / rx
    cx = cos(φ) * cx_ - sin(φ) * cy_ + (x1 + x2) / 2
    cy = cos(φ) * cy_ + sin(φ) * cx_ + (y1 + y2) / 2
    θ1 = _angle([1., 0.], [(x1_ - cx_) / rx, (y1_ - cy_) / ry])
    dθ = _angle([(x1_ - cx_) / rx, (y1_ - cy_) / ry], [(-x1_ - cx_) / rx, (-y1_ - cy_) / ry]) % (2 * pi)
    dθ = (-1 if sweep == 0 else 1) * dθ
    θ2 = θ1 + dθ
    return cx, cy, rx, ry, θ1, θ2


class _SegmentizeVisitor:
    def __init__(self, max_distance):
        self.max_distance = max_distance
        self.pos = [0., 0.]
        self.ctrl_c = [0., 0.]
        self.ctrl_q = [0., 0.]
        self.data = []
        self.cmd_data = []
        self.last_cmd = None
        self.last_m = [0., 0.]

    def cmd(self, cmd):
        new_cmd, proc = getattr(self, cmd)()
        if new_cmd != self.last_cmd:
            self.flush()
            self.cmd_data += [new_cmd]
            self.last_cmd = new_cmd

        def process(v):
            self.cmd_data += proc(v)

        return process

    def flush(self):
        if len(self.cmd_data) > 0:
            self.data += [self.cmd_data]
            self.cmd_data = []

    def m(self):
        def proc(v):
            self.pos[0] += v[0]
            self.pos[1] += v[1]
            self.last_m = self.pos[:]
            self.ctrl_c = self.pos[:]
            self.ctrl_q = self.pos[:]
            return [v]
        return 'm', proc

    def M(self):
        def proc(v):
            self.pos = v
            self.last_m = self.pos[:]
            self.ctrl_c = self.pos[:]
            self.ctrl_q = self.pos[:]
            return [v]
        return 'M', proc

    def h(self):
        def proc(v):
            ps = _line_to_segments([0., 0.], [v[0], 0.], self.max_distance)
            _make_relative(ps)
            self.pos[0] += v[0]
            self.ctrl_c = self.pos[:]
            self.ctrl_q = self.pos[:]
            return ps
        return 'l', proc

    def H(self):
        def proc(v):
            ps = _line_to_segments(self.pos, [v[0], self.pos[1]], self.max_distance)
            self.pos[0] = v[0]
            self.ctrl_c = self.pos[:]
            self.ctrl_q = self.pos[:]
            return ps
        return 'L', proc

    def v(self):
        def proc(v):
            ps = _line_to_segments([0., 0.], [0., v[0]], self.max_distance)
            _make_relative(ps)
            self.pos[1] += v[0]
            self.ctrl_c = self.pos[:]
            self.ctrl_q = self.pos[:]
            return ps
        return 'l', proc

    def V(self):
        def proc(v):
            ps = _line_to_segments(self.pos, [self.pos[0], v[0]], self.max_distance)
            self.pos[1] = v[0]
            self.ctrl_c = self.pos[:]
            self.ctrl_q = self.pos[:]
            return ps
        return 'L', proc

    def s(self):
        def proc(v):
            pfx = [0., 0., self.pos[0] - self.ctrl_c[0], self.pos[1] - self.ctrl_c[1]]
            ps = [p[6:8] for p in _cubic_bezier_to_segments(pfx + v, self.max_distance)]
            _make_relative(ps)
            self.ctrl_c[0] = self.pos[0] + v[0]
            self.ctrl_c[1] = self.pos[1] + v[1]
            self.pos[0] += v[2]
            self.pos[1] += v[3]
            self.ctrl_q = self.pos[:]
            return ps
        return 'l', proc

    def S(self):
        def proc(v):
            pfx = self.pos + [self.pos[0] * 2 - self.ctrl_c[0], self.pos[1] * 2 - self.ctrl_c[1]]
            ps = [p[6:8] for p in _cubic_bezier_to_segments(pfx + v, self.max_distance)]
            self.pos = v[2:4]
            self.ctrl_c = v[0:2]
            self.ctrl_q = self.pos[:]
            return ps
        return 'L', proc

    def c(self):
        def proc(v):
            ps = [p[6:8] for p in _cubic_bezier_to_segments([0., 0.] + v, self.max_distance)]
            _make_relative(ps)
            self.ctrl_c[0] = self.pos[0] + v[2]
            self.ctrl_c[1] = self.pos[1] + v[3]
            self.pos[0] += v[4]
            self.pos[1] += v[5]
            self.ctrl_q = self.pos[:]
            return ps
        return 'l', proc

    def C(self):
        def proc(v):
            ps = [p[6:8] for p in _cubic_bezier_to_segments(self.pos + v, self.max_distance)]
            self.pos = v[4:6]
            self.ctrl_c = v[2:4]
            self.ctrl_q = self.pos[:]
            return ps
        return 'L', proc

    def a(self):
        def proc(v):
            rx, ry, deg, large, sweep, dx, dy = v
            if rx == 0 or ry == 0:
                _, lproc = self.l()
                return lproc([dx, dy])
            φ = deg / 180 * pi
            x1, y1 = self.pos
            x2, y2 = x1 + dx, y1 + dy
            cx, cy, rx, ry, θ1, θ2 = _arc_center_params(x1, y1, x2, y2, large, sweep, rx, ry, φ)
            ps = _arc_to_segments(cx, cy, rx, ry, φ, θ1, θ2, self.max_distance)
            _make_relative(ps)
            ps[0][0] -= self.pos[0]
            ps[0][1] -= self.pos[1]
            self.pos[0] += dx
            self.pos[1] += dy
            self.ctrl_c = self.pos[:]
            self.ctrl_q = self.pos[:]
            return ps
        return 'l', proc

    def A(self):
        def proc(v):
            rx, ry, deg, large, sweep, x2, y2 = v
            if rx == 0 or ry == 0:
                _, lproc = self.L()
                return lproc([x2, y2])
            φ = deg / 180 * pi
            x1, y1 = self.pos
            cx, cy, rx, ry, θ1, θ2 = _arc_center_params(x1, y1, x2, y2, large, sweep, rx, ry, φ)
            ps = _arc_to_segments(cx, cy, rx, ry, φ, θ1, θ2, self.max_distance)
            self.pos = [x2, y2]
            self.ctrl_c = self.pos[:]
            self.ctrl_q = self.pos[:]
            return ps
        return 'L', proc

    def l(self):  # noqa: E743, E741
        def proc(v):
            ps = _line_to_segments([0., 0.], v, self.max_distance)
            _make_relative(ps)
            self.pos[0] += v[0]
            self.pos[1] += v[1]
            self.ctrl_c = self.pos[:]
            self.ctrl_q = self.pos[:]
            return ps
        return 'l', proc

    def L(self):
        def proc(v):
            ps = _line_to_segments(self.pos, v, self.max_distance)
            self.pos = v
            self.ctrl_c = self.pos[:]
            self.ctrl_q = self.pos[:]
            return ps
        return 'L', proc

    def t(self):
        def proc(v):
            pfx = [0., 0., self.pos[0] - self.ctrl_q[0], self.pos[1] - self.ctrl_q[1]]
            ps = [p[4:6] for p in _quadratic_bezier_to_segments(pfx + v, self.max_distance)]
            _make_relative(ps)
            self.ctrl_q[0] = self.pos[0] * 2 - self.ctrl_q[0]
            self.ctrl_q[1] = self.pos[1] * 2 - self.ctrl_q[1]
            self.pos[0] += v[0]
            self.pos[1] += v[1]
            self.ctrl_c = self.pos[:]
            return ps
        return 'l', proc

    def T(self):
        def proc(v):
            self.ctrl_q[0] = self.pos[0] * 2 - self.ctrl_q[0]
            self.ctrl_q[1] = self.pos[1] * 2 - self.ctrl_q[1]
            pfx = self.pos + self.ctrl_q
            ps = [p[4:6] for p in _quadratic_bezier_to_segments(pfx + v, self.max_distance)]
            self.pos = v[:]
            self.ctrl_c = self.pos[:]
            return ps
        return 'L', proc

    def q(self):
        def proc(v):
            ps = [p[4:6] for p in _quadratic_bezier_to_segments([0., 0.] + v, self.max_distance)]
            _make_relative(ps)
            self.ctrl_q[0] = self.pos[0] + v[0]
            self.ctrl_q[1] = self.pos[1] + v[1]
            self.pos[0] += v[2]
            self.pos[1] += v[3]
            self.ctrl_c = self.pos[:]
            return ps
        return 'l', proc

    def Q(self):
        def proc(v):
            ps = [p[4:6] for p in _quadratic_bezier_to_segments(self.pos + v, self.max_distance)]
            self.pos = v[2:4]
            self.ctrl_c = self.pos[:]
            self.ctrl_q = v[0:2]
            return ps
        return 'L', proc

    def z(self):
        self.flush()
        end = [self.last_m[0] - self.pos[0], self.last_m[1] - self.pos[1]]
        ps = _line_to_segments([0., 0.], end, self.max_distance)[:-1]
        if len(ps) > 0:
            _make_relative(ps)
            self.data += [['l'] + ps]
        self.pos = self.last_m[:]
        self.ctrl_c = self.pos[:]
        self.ctrl_q = self.pos[:]
        return 'z', None

    def Z(self):
        self.flush()
        ps = _line_to_segments(self.pos, self.last_m, self.max_distance)[:-1]
        if len(ps) > 0:
            self.data += [['L'] + ps]
        self.pos = self.last_m[:]
        self.ctrl_c = self.pos[:]
        self.ctrl_q = self.pos[:]
        return 'Z', None


def segmentize(d, max_distance=float('inf')):
    visitor = _SegmentizeVisitor(max_distance)
    for vs in d:
        proc = visitor.cmd(vs[0])
        for v in vs[1:]:
            proc(v)
    visitor.flush()
    return visitor.data
