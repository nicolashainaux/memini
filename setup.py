# -*- coding: utf-8 -*-

# DO NOT EDIT THIS FILE!
# This file has been autogenerated by dephell <3
# https://github.com/dephell/dephell

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

readme = ''

setup(
    long_description=readme,
    name='memini',
    version='0.1.0',
    python_requires='==3.*,>=3.6.0',
    author='Nicolas Hainaux',
    author_email='nh.techn@gmail.com',
    entry_points={"console_scripts": ["memini = memini:run"]},
    packages=['memini', 'memini.core'],
    package_dir={"": "."},
    package_data={
        "memini": [
            "data/*.toml", "data/*.xml", "data/default/files/*.yaml",
            "data/template/*.rdf", "data/template/*.xml",
            "data/template/META-INF/*.xml"
        ]
    },
    install_requires=[
        'blessed==1.*,>=1.17.8', 'click==7.*,>=7.1.2', 'intspan==1.*,>=1.6.1',
        'relatorio==0.*,>=0.9.0', 'toml==0.*,>=0.9.4'
    ],
    extras_require={
        "dev": [
            "coverage==5.*,>=5.1.0", "coveralls==2.*,>=2.0.0",
            "flake8==3.*,>=3.8.3", "pyfakefs==3.*,>=3.6.0",
            "pytest==3.*,>=3.0.0", "pytest-mock==1.*,>=1.10.0",
            "sphinx==3.*,>=3.1.2", "sphinx-rtd-theme==0.*,>=0.5.0"
        ]
    },
)
