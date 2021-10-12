def _sub(a, b):
    return [a[0] - b[0], a[1] - b[1]]


class _MorphVisitor:
    def __init__(self, morpher):
        self.morpher = morpher
        self.pos = [0., 0.]
        self.mrh_pos = [0., 0.]
        self.data = []
        self.cmd_data = []
        self.last_m = [0., 0.]
        self.last_cmd = None

    def cmd(self, cmd):
        new_cmd, proc = getattr(self, cmd)()
        if new_cmd != self.last_cmd:
            self.flush()
            self.cmd_data += [new_cmd]
            self.last_cmd = new_cmd

        def process(v):
            self.cmd_data += [proc(v)]

        return process

    def flush(self):
        if len(self.cmd_data) > 0:
            self.data += [self.cmd_data]
            self.cmd_data = []

    def m(self):
        def proc(v):
            prev = self.mrh_pos[:]
            self.pos[0] += v[0]
            self.pos[1] += v[1]
            self.mrh_pos = self.morpher(self.pos)
            self.last_m = self.pos[:]
            return _sub(self.mrh_pos, prev)
        return 'm', proc

    def M(self):
        def proc(v):
            self.pos = v[:]
            self.mrh_pos = self.morpher(self.pos)
            self.last_m = self.pos[:]
            return self.mrh_pos
        return 'M', proc

    def h(self):
        def proc(v):
            prev = self.mrh_pos[:]
            self.pos[0] += v[0]
            self.mrh_pos = self.morpher(self.pos)
            return _sub(self.mrh_pos, prev)
        return 'l', proc

    def H(self):
        def proc(v):
            self.pos[0] = v[0]
            self.mrh_pos = self.morpher(self.pos)
            return self.mrh_pos
        return 'L', proc

    def v(self):
        def proc(v):
            prev = self.mrh_pos[:]
            self.pos[1] += v[0]
            self.mrh_pos = self.morpher(self.pos)
            return _sub(self.mrh_pos, prev)
        return 'l', proc

    def V(self):
        def proc(v):
            self.pos[1] = v[0]
            self.mrh_pos = self.morpher(self.pos)
            return self.mrh_pos
        return 'L', proc

    def s(self):
        def proc(v):
            prev = self.mrh_pos[:]
            cp = self.morpher([self.pos[0] + v[0], self.pos[1] + v[1]])
            self.pos[0] += v[2]
            self.pos[1] += v[3]
            self.mrh_pos = self.morpher(self.pos)
            return [*_sub(cp, prev), *_sub(self.mrh_pos, prev)]
        return 's', proc

    def S(self):
        def proc(v):
            cp = self.morpher(v[0:2])
            self.pos = v[2:4]
            self.mrh_pos = self.morpher(self.pos)
            return [*cp, *self.mrh_pos]
        return 'S', proc

    def c(self):
        def proc(v):
            prev = self.mrh_pos[:]
            cp1 = self.morpher([self.pos[0] + v[0], self.pos[1] + v[1]])
            cp2 = self.morpher([self.pos[0] + v[2], self.pos[1] + v[3]])
            self.pos[0] += v[4]
            self.pos[1] += v[5]
            self.mrh_pos = self.morpher(self.pos)
            return [*_sub(cp1, prev), *_sub(cp2, prev), *_sub(self.mrh_pos, prev)]
        return 'c', proc

    def C(self):
        def proc(v):
            cp1 = self.morpher(v[0:2])
            cp2 = self.morpher(v[2:4])
            self.pos = v[4:6]
            self.mrh_pos = self.morpher(self.pos)
            return [*cp1, *cp2, *self.mrh_pos]
        return 'C', proc

    def a(self):
        def proc(v):
            prev = self.mrh_pos[:]
            self.pos[0] += v[5]
            self.pos[1] += v[6]
            self.mrh_pos = self.morpher(self.pos)
            return [*v[0:5], *_sub(self.mrh_pos, prev)]
        return 'a', proc

    def A(self):
        def proc(v):
            self.pos = v[5:7]
            self.mrh_pos = self.morpher(self.pos)
            return [*v[0:5], *self.mrh_pos]
        return 'A', proc

    def l(self):  # noqa: E743, E741
        def proc(v):
            prev = self.mrh_pos[:]
            self.pos[0] += v[0]
            self.pos[1] += v[1]
            self.mrh_pos = self.morpher(self.pos)
            return _sub(self.mrh_pos, prev)
        return 'l', proc

    def L(self):
        def proc(v):
            self.pos = v[:]
            self.mrh_pos = self.morpher(self.pos)
            return self.mrh_pos
        return 'L', proc

    def t(self):
        def proc(v):
            prev = self.mrh_pos[:]
            self.pos[0] += v[0]
            self.pos[1] += v[1]
            self.mrh_pos = self.morpher(self.pos)
            return _sub(self.mrh_pos, prev)
        return 't', proc

    def T(self):
        def proc(v):
            self.pos = v[:]
            self.mrh_pos = self.morpher(self.pos)
            return self.mrh_pos
        return 'T', proc

    def q(self):
        def proc(v):
            prev = self.mrh_pos[:]
            cp = self.morpher([self.pos[0] + v[0], self.pos[1] + v[1]])
            self.pos[0] += v[2]
            self.pos[1] += v[3]
            self.mrh_pos = self.morpher(self.pos)
            return [*_sub(cp, prev), *_sub(self.mrh_pos, prev)]
        return 'q', proc

    def Q(self):
        def proc(v):
            cp = self.morpher(v[0:2])
            self.pos = v[2:4]
            self.mrh_pos = self.morpher(self.pos)
            return [*cp, *self.mrh_pos]
        return 'Q', proc

    def z(self):
        self.flush()
        self.pos = self.last_m[:]
        self.mrh_pos = self.morpher(self.pos)
        return 'z', None

    def Z(self):
        self.flush()
        self.pos = self.last_m[:]
        self.mrh_pos = self.morpher(self.pos)
        return 'Z', None


def morph(d, morpher):
    visitor = _MorphVisitor(morpher)
    for vs in d:
        proc = visitor.cmd(vs[0])
        for v in vs[1:]:
            proc(v)
    visitor.flush()
    return visitor.data
