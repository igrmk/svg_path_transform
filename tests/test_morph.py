from svg_path_transform._morph import morph


def test_morph_straight_line():
    data = [
        ['m', [1, 2]],
        ['l', [0, 1]],
    ]
    result = morph(data, lambda p: (p[1], p[0]))
    expected = [
        ['m', [2, 1]],
        ['l', [1, 0]],
    ]
    assert result == expected


def test_morph_two_connected_straight_lines():
    data = [
        ['m', [1, 2]],
        ['l', [0, 1]],
        ['l', [0, 1]],
    ]
    result = morph(data, lambda p: (p[1], p[0]))
    expected = [
        ['m', [2, 1]],
        [
            'l',
            [1, 0],
            [1, 0],
        ],
    ]
    assert result == expected


def test_morph_two_disconnected_straight_lines():
    data = [
        ['m', [1, 2]],
        ['l', [0, 1]],
        ['m', [1, 0]],
        ['l', [0, 1]],
    ]
    result = morph(data, lambda p: (p[1], p[0]))
    expected = [
        ['m', [2, 1]],
        ['l', [1, 0]],
        ['m', [0, 1]],
        ['l', [1, 0]],
    ]
    assert result == expected


def test_consecutive_m():
    data = [
        ['m', [1, 1]],
        ['m', [0, 1]],
        ['m', [1, 0]],
        ['m', [1, -1]],
    ]
    result = morph(data, lambda p: (p[1], p[0]))
    expected = [
        ['m', [1, 1]],
        ['m', [1, 0]],
        ['m', [0, 1]],
        ['m', [-1, 1]],
    ]
    assert result == expected


def test_subsequent_coordinate_pairs_in_m():
    data = [
        [
            'm',
            [0, 1],
            [1, 0],
            [0, 1],
            [-1, 1],
        ],
    ]
    result = morph(data, lambda p: (p[1], p[0]))
    expected = [
        ['m', [1, 0]],
        [
            'l',
            [0, 1],
            [1, 0],
            [1, -1],
        ],
    ]
    assert result == expected


def test_subsequent_coordinate_pairs_in_m_with_z_and_repeat():
    data = [
        [
            'm',
            [1, 1],
            [1, 0],
            [0, 1],
        ],
        ['z'],
        [
            'm',
            [1, 1],
            [1, 0],
            [0, 1],
        ],
        ['z'],
    ]
    result = morph(data, lambda p: (p[0] * p[0], p[1] * p[1]))
    expected = [
        ['m', [1, 1]],
        [
            'l',
            [3, 0],
            [0, 3],
        ],
        ['z'],
        ['m', [3, 3]],
        [
            'l',
            [5, 0],
            [0, 5],
        ],
        ['z'],
    ]
    assert result == expected
