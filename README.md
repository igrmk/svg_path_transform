SVG path data transformation toolkit
====================================

<!-- cut -->
[![Version](https://img.shields.io/pypi/v/svg-path-transform.svg)](https://pypi.org/project/svg-path-transform/)
<!-- end -->
A tool and a library for SVG path data transformations.
Currently it supports a translation and a scaling.

Usage
-----

As a library

```python
import svg_path_transform as S
path = S.parse_path("m 2 2 l 2 2")
path = S.translate_and_scale(path, s=(1, 3))
path = S.translate_and_scale(path, t=(3, 4))
print(S.path_to_string(path, sfig=4))
```

As a command line tool

```bash
svg_path_transform --dx 100 --dy 100 < input-path-data > output-path-data
```

A script to transform an SVG with a single path inside

```bash
new_path="$(xmlstarlet sel -t -v '//_:path[1]/@d' input.svg | svg_path_transform --sx 2 --sy 2)"
xmlstarlet ed -u '//_:path[1]/@d' -v "$new_path" < intput.svg > output.svg
```

Installation
------------

```bash
pip3 install svg_path_transform
```
