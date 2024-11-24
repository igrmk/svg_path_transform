from typing import Callable


def _sub(a, b):
    return [a[0] - b[0], a[1] - b[1]]


class _MorphVisitor:
    def __init__(self, morpher: Callable[[tuple[float, float]], tuple[float, float]]):
        self.morpher = morpher
        self.result_data = []
        self.current_bypass_pos = [0., 0.]
        self.current_result_pos = [0., 0.]
        self.current_cmd_result_symbol = None
        self.current_cmd_result_bundle = []
        self.current_subpath_starting_bypass_pos = [0., 0.]
        self.data_handler = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.flush()

    def flush(self):
        if len(self.current_cmd_result_bundle) > 0:
            self.result_data.append(self.current_cmd_result_bundle)
            self.current_cmd_result_bundle = []

    def process_cmd_symbol(self, cmd_symbol):
        getattr(self, f'process_cmd_symbol_{cmd_symbol}')()

    def process_cmd_data(self, cmd_data):
        self.data_handler(cmd_data)

    def process_cmd_symbol_common(self, cmd_result_symbol):
        if cmd_result_symbol != self.current_cmd_result_symbol:
            self.flush()
            self.current_cmd_result_symbol = cmd_result_symbol
            self.current_cmd_result_bundle += [cmd_result_symbol]
            self.data_handler = getattr(self, f'process_cmd_data_for_{cmd_result_symbol}', None)

    def process_cmd_symbol_m(self):
        never_collapse_m = None
        self.current_cmd_result_symbol = never_collapse_m
        self.process_cmd_symbol_common('m')

    def process_cmd_data_for_m(self, data):
        second_occurrence = len(self.current_cmd_result_bundle) == 2
        if second_occurrence:
            self.process_cmd_symbol_common('l')
            self.data_handler(data)
            return
        starting_result_pos = self.current_result_pos[:]
        self.current_bypass_pos[0] += data[0]
        self.current_bypass_pos[1] += data[1]
        self.current_result_pos = self.morpher(self.current_bypass_pos)
        self.current_subpath_starting_bypass_pos = self.current_bypass_pos[:]
        self.current_cmd_result_bundle.append(_sub(self.current_result_pos, starting_result_pos))

    def process_cmd_symbol_M(self):
        never_collapse_m = None
        self.current_cmd_result_symbol = never_collapse_m
        self.process_cmd_symbol_common('M')

    def process_cmd_data_for_M(self, data):
        second_occurrence = len(self.current_cmd_result_bundle) == 2
        if second_occurrence:
            self.process_cmd_symbol_common('L')
            self.data_handler(data)
            return
        self.current_bypass_pos = data[:]
        self.current_result_pos = self.morpher(self.current_bypass_pos)
        self.current_subpath_starting_bypass_pos = self.current_bypass_pos[:]
        self.current_cmd_result_bundle.append(self.current_result_pos)

    def process_cmd_symbol_h(self):
        self.process_cmd_symbol_common('l')
        self.data_handler = self.process_cmd_data_for_h

    def process_cmd_data_for_h(self, data):
        starting_result_pos = self.current_result_pos[:]
        self.current_bypass_pos[0] += data[0]
        self.current_result_pos = self.morpher(self.current_bypass_pos)
        self.current_cmd_result_bundle.append(_sub(self.current_result_pos, starting_result_pos))

    def process_cmd_symbol_H(self):
        self.process_cmd_symbol_common('L')
        self.data_handler = self.process_cmd_data_for_H

    def process_cmd_data_for_H(self, data):
        self.current_bypass_pos[0] = data[0]
        self.current_result_pos = self.morpher(self.current_bypass_pos)
        self.current_cmd_result_bundle.append(self.current_result_pos)

    def process_cmd_symbol_v(self):
        self.process_cmd_symbol_common('l')
        self.data_handler = self.process_cmd_data_for_v

    def process_cmd_data_for_v(self, data):
        starting_result_pos = self.current_result_pos[:]
        self.current_bypass_pos[1] += data[0]
        self.current_result_pos = self.morpher(self.current_bypass_pos)
        self.current_cmd_result_bundle.append(_sub(self.current_result_pos, starting_result_pos))

    def process_cmd_symbol_V(self):
        self.process_cmd_symbol_common('L')
        self.data_handler = self.process_cmd_data_for_V

    def process_cmd_data_for_V(self, data):
        self.current_bypass_pos[1] = data[0]
        self.current_result_pos = self.morpher(self.current_bypass_pos)
        self.current_cmd_result_bundle.append(self.current_result_pos)

    def process_cmd_symbol_s(self):
        self.process_cmd_symbol_common('s')

    def process_cmd_data_for_s(self, data):
        starting_result_pos = self.current_result_pos[:]
        cp = self.morpher([self.current_bypass_pos[0] + data[0], self.current_bypass_pos[1] + data[1]])
        self.current_bypass_pos[0] += data[2]
        self.current_bypass_pos[1] += data[3]
        self.current_result_pos = self.morpher(self.current_bypass_pos)
        self.current_cmd_result_bundle.append([
            *_sub(cp, starting_result_pos),
            *_sub(self.current_result_pos, starting_result_pos)
        ])

    def process_cmd_symbol_S(self):
        self.process_cmd_symbol_common('S')

    def process_cmd_data_for_S(self, data):
        cp = self.morpher(data[0:2])
        self.current_bypass_pos = data[2:4]
        self.current_result_pos = self.morpher(self.current_bypass_pos)
        params = [*cp, *self.current_result_pos]
        self.current_cmd_result_bundle += [params]

    def process_cmd_symbol_c(self):
        self.process_cmd_symbol_common('c')

    def process_cmd_data_for_c(self, data):
        starting_result_pos = self.current_result_pos[:]
        cp1 = self.morpher([self.current_bypass_pos[0] + data[0], self.current_bypass_pos[1] + data[1]])
        cp2 = self.morpher([self.current_bypass_pos[0] + data[2], self.current_bypass_pos[1] + data[3]])
        self.current_bypass_pos[0] += data[4]
        self.current_bypass_pos[1] += data[5]
        self.current_result_pos = self.morpher(self.current_bypass_pos)
        self.current_cmd_result_bundle.append([
            *_sub(cp1, starting_result_pos),
            *_sub(cp2, starting_result_pos),
            *_sub(self.current_result_pos, starting_result_pos),
        ])

    def process_cmd_symbol_C(self):
        self.process_cmd_symbol_common('C')

    def process_cmd_data_for_C(self, data):
        cp1 = self.morpher(data[0:2])
        cp2 = self.morpher(data[2:4])
        self.current_bypass_pos = data[4:6]
        self.current_result_pos = self.morpher(self.current_bypass_pos)
        self.current_cmd_result_bundle.append([*cp1, *cp2, *self.current_result_pos])

    def process_cmd_symbol_a(self):
        self.process_cmd_symbol_common('a')

    def process_cmd_data_for_a(self, data):
        starting_result_pos = self.current_result_pos[:]
        self.current_bypass_pos[0] += data[5]
        self.current_bypass_pos[1] += data[6]
        self.current_result_pos = self.morpher(self.current_bypass_pos)
        self.current_cmd_result_bundle.append([*data[0:5], *_sub(self.current_result_pos, starting_result_pos)])

    def process_cmd_symbol_A(self):
        self.process_cmd_symbol_common('A')

    def process_cmd_data_for_A(self, data):
        self.current_bypass_pos = data[5:7]
        self.current_result_pos = self.morpher(self.current_bypass_pos)
        self.current_cmd_result_bundle.append([*data[0:5], *self.current_result_pos])

    def process_cmd_symbol_l(self):
        self.process_cmd_symbol_common('l')

    def process_cmd_data_for_l(self, data):
        starting_result_pos = self.current_result_pos[:]
        self.current_bypass_pos[0] += data[0]
        self.current_bypass_pos[1] += data[1]
        self.current_result_pos = self.morpher(self.current_bypass_pos)
        self.current_cmd_result_bundle.append(_sub(self.current_result_pos, starting_result_pos))

    def process_cmd_symbol_L(self):
        self.process_cmd_symbol_common('L')

    def process_cmd_data_for_L(self, data):
        self.current_bypass_pos = data[:]
        self.current_result_pos = self.morpher(self.current_bypass_pos)
        self.current_cmd_result_bundle.append(self.current_result_pos)

    def process_cmd_symbol_t(self):
        self.process_cmd_symbol_common('t')

    def process_cmd_data_for_t(self, data):
        starting_result_pos = self.current_result_pos[:]
        self.current_bypass_pos[0] += data[0]
        self.current_bypass_pos[1] += data[1]
        self.current_result_pos = self.morpher(self.current_bypass_pos)
        self.current_cmd_result_bundle.append(_sub(self.current_result_pos, starting_result_pos))

    def process_cmd_symbol_T(self):
        self.process_cmd_symbol_common('T')

    def process_cmd_data_for_T(self, data):
        self.current_bypass_pos = data[:]
        self.current_result_pos = self.morpher(self.current_bypass_pos)
        self.current_cmd_result_bundle.append(self.current_result_pos)

    def process_cmd_symbol_q(self):
        self.process_cmd_symbol_common('q')

    def process_cmd_data_for_q(self, data):
        starting_result_pos = self.current_result_pos[:]
        cp = self.morpher([self.current_bypass_pos[0] + data[0], self.current_bypass_pos[1] + data[1]])
        self.current_bypass_pos[0] += data[2]
        self.current_bypass_pos[1] += data[3]
        self.current_result_pos = self.morpher(self.current_bypass_pos)
        self.current_cmd_result_bundle.append([
            *_sub(cp, starting_result_pos),
            *_sub(self.current_result_pos, starting_result_pos)
        ])

    def process_cmd_symbol_Q(self):
        self.process_cmd_symbol_common('Q')

    def process_cmd_data_for_Q(self, data):
        cp = self.morpher(data[0:2])
        self.current_bypass_pos = data[2:4]
        self.current_result_pos = self.morpher(self.current_bypass_pos)
        self.current_cmd_result_bundle.append([*cp, *self.current_result_pos])

    def process_cmd_symbol_z(self):
        self.process_cmd_symbol_common('z')
        self.current_bypass_pos = self.current_subpath_starting_bypass_pos[:]
        self.current_result_pos = self.morpher(self.current_bypass_pos)

    def process_cmd_symbol_Z(self):
        self.process_cmd_symbol_common('Z')
        self.current_bypass_pos = self.current_subpath_starting_bypass_pos[:]
        self.current_result_pos = self.morpher(self.current_bypass_pos)


def morph(d, morpher):
    with _MorphVisitor(morpher) as visitor:
        for cmd_bundle in d:
            visitor.process_cmd_symbol(cmd_bundle[0])
            for data in cmd_bundle[1:]:
                visitor.process_cmd_data(data)
    return visitor.result_data
