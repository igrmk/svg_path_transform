from os.path import abspath, dirname, join
import setuptools
from pathlib import Path

here = abspath(dirname(__file__))


def read(rel_path): return Path(join(here, rel_path)).read_text()


def long_description():
    lines = read('README.md').splitlines()
    lines_ = []
    cut = False
    for line in lines:
        if '<!-- end -->' in line:
            cut = False
        elif '<!-- cut -->' in line:
            cut = True
        elif not cut:
            lines_.append(line)
    return ''.join(lines_)


setuptools.setup(
    name='svg_path_transform',
    version=read('svg_path_transform/__version__.py').split("'")[1],
    author='igrmk',
    author_email='igrmkx@gmail.com',
    description='SVG path data transformation toolkit',
    long_description=long_description(),
    long_description_content_type='text/markdown',
    url='https://github.com/igrmk/svg_path_transform',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    entry_points={'console_scripts': ['svg_path_transform = svg_path_transform._cli:_main']},
    install_requires=['lark>=0.11.3'],
    package_data={'': ['*.lark']},
    include_package_data=True,
)
