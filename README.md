SVG path data transformation toolkit
====================================

<!-- cut -->
[![Version](https://img.shields.io/pypi/v/svg-path-transform.svg)](https://pypi.org/project/svg-path-transform/)
<!-- end -->
A tool and a library for SVG path data transformations.
Currently it supports a translation and a scaling.

Usage
-----

As a Python library

```python
import svg_path_transform as S
path = S.parse_path("m 2 2 l 2 2")
path = S.translate_and_scale(path, s=(1, 3))
path = S.translate_and_scale(path, t=(3, 4))
print(S.path_to_string(path, sfig=4))
```

As a command line tool

```bash
svg_path_transform --dx 100 --dy 100 <<< "m 2 2 l 2 2"
```

Command line parameters

```
usage: svg_path_transform [-h] [--dx N] [--dy N] [--sx N] [--sy N] [--sfig N] [--ndig N] [-v]

SVG path data transformer

optional arguments:
  -h, --help     show this help message and exit
  --dx N         translate x by N
  --dy N         translate y by N
  --sx N         scale x by N
  --sy N         scale y by N
  --sfig N       round to N significant figures
  --ndig N       round to N decimal places
  -v, --version  show program's version number and exit
```

Hint: a bash function to transform an SVG with a single path inside

```bash
function svg_transform() {
    selector='//_:path[1]/@d'
    input=$(</dev/stdin)
    old_path="$(xmlstarlet sel -t -v "$selector" <<< "$input")"
    [[ $? -ne 0 ]] && echo "could not parse SVG" && return 1
    new_path="$(svg_path_transform "$@" <<< "$old_path")"
    [[ $? -ne 0 ]] && echo "could not parse path" && return 1
    xmlstarlet ed -u "$selector" -v "$new_path" <<< "$input"
    [[ $? -ne 0 ]] && echo "could not update SVG" && return 1
    return 0
}

svg_transform --sx 2 --sy 2 < intput.svg > output.svg
```

Installation
------------

```bash
pip3 install svg_path_transform
```
