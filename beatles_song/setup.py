#!/usr/bin/env python
# -*- coding: utf-8 -*-


from setuptools import setup


package_name = 'beatles_song'


def get_version():
    import ast

    def parse_version(f):
        for line in f:
            if line.startswith('__version__'):
                return ast.parse(line).body[0].value.s

    for i in [package_name + '.py']:
        try:
            with open(i, 'r') as f:
                return parse_version(f)
        except IOError:
            pass


def get_long_description():
    try:
        with open('README.md', 'r') as f:
            return f.read()
    except IOError:
        return ''


setup(
    # license='License :: OSI Approved :: MIT License',
    name=package_name,
    version=get_version(),
    author='',
    author_email='',
    description='',
    url='',
    long_description=get_long_description(),
    py_modules=[package_name],
    entry_points={
        'console_scripts': [
            'bts = beatles_song:main',
        ]
    }
)
