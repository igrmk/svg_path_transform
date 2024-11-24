import pytest
import math
from svg_path_transform._segmentize import _convert_arc_endpoint_params_to_center_params

pi = math.pi


def test_arc_endpoint_params_to_center_params_conversion_1():
    cx, cy, rx, ry, θ1, θ2 =\
         _convert_arc_endpoint_params_to_center_params(x1=0, y1=0, x2=1, y2=0, large=0, sweep=1, rx=0.5, ry=1, φ=0)
    expected = (0.5, 0, 0.5, 1, pi, 2*pi)
    assert (cx, cy, rx, ry, θ1, θ2) == pytest.approx(expected, abs=1e-9)


def test_arc_endpoint_params_to_center_params_conversion_2():
    cx, cy, rx, ry, θ1, θ2 =\
        _convert_arc_endpoint_params_to_center_params(x1=0, y1=0, x2=1, y2=0, large=0, sweep=0, rx=0.5, ry=1, φ=0)
    expected = (0.5, 0, 0.5, 1, pi, 0)
    assert (cx, cy, rx, ry, θ1, θ2) == pytest.approx(expected, abs=1e-9)


def test_arc_endpoint_params_to_center_params_conversion_3():
    cx, cy, rx, ry, θ1, θ2 =\
        _convert_arc_endpoint_params_to_center_params(x1=0, y1=0, x2=1, y2=0, large=0, sweep=1, rx=1000, ry=1000, φ=0)
    expected = (0.5, 1000, 1000, 1000, -0.5 * pi, -0.5 * pi)
    assert (cx, cy, rx, ry, θ1, θ2) == pytest.approx(expected, abs=1e-3)
    assert θ1 < -0.5 * pi
    assert θ2 > -0.5 * pi


def test_arc_endpoint_params_to_center_params_conversion_4():
    cx, cy, rx, ry, θ1, θ2 =\
        _convert_arc_endpoint_params_to_center_params(x1=0, y1=0, x2=1, y2=0, large=0, sweep=0, rx=1000, ry=1000, φ=0)
    expected = (0.5, -1000, 1000, 1000, 0.5 * pi, 0.5 * pi)
    assert (cx, cy, rx, ry, θ1, θ2) == pytest.approx(expected, abs=1e-3)
    assert θ1 > 0.5 * pi
    assert θ2 < 0.5 * pi
