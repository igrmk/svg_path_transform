SVG path data transformation toolkit
====================================

A tool and a library for SVG path data transformations.
Currently it supports a translation and a scaling.

Usage
-----

As a library

    import svg_path_transform as S
    path = S.parse_path("m 2 2 l 2 2")
    path = S.translate_and_scale(path, s=(1, 3))
    path = S.translate_and_scale(path, t=(3, 4))
    print(S.path_to_string(path, sfig = 4))

As a command line tool

    svg_path_transform --dx 100 --dy 100 < input-path-data > output-path-data

A script to transform an SVG with a single path inside

    new_path="$(xmlstarlet sel -t -v '//_:path[1]/@d' input.svg | svg_path_transform --sx 2 --sy 2)"
    xmlstarlet ed -u '//_:path[1]/@d' -v "$new_path" < intput.svg > output.svg

Installation
------------

    pip3 install svg_path_transform