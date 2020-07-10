# -*- coding: utf-8 -*-

# VocaShaker is a simple project that creates vocabulary grids to train.
# Copyright 2019 Nicolas Hainaux <nh.techn@gmail.com>

# This file is part of VocaShaker.

# VocaShaker is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# any later version.

# VocaShaker is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with VocaShaker; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import os
import sys
from pathlib import Path

import toml

PROG_NAME = 'VocaShaker'
MAXCOL_NB = 4

__process_name = os.path.basename(__file__)
__abspath = os.path.abspath(__file__)
__l1 = len(__process_name)
__l2 = len(__abspath)
CORE_DIRNAME = 'core/'
ROOTDIR = __abspath[:__l2 - __l1][:-(len(CORE_DIRNAME) + 1)]
DATADIR = os.path.join(ROOTDIR, 'data')

with open(os.path.join(DATADIR, 'metadata.toml'), 'r') as f:
    pp = toml.load(f)

__myname__ = pp['__myname__']
__authors__ = pp['__authors__']
__version__ = pp['__version__']

PYVER = sys.version.replace('\n', ' ')
MESSAGE = f'This is {PROG_NAME}, version {__version__}, '\
    f'running under python {PYVER}.\nCopyright (C) 2020 Nicolas Hainaux\n'\
    'This program comes with ABSOLUTELY NO WARRANTY.\n'\
    'This is free software, and you are welcome to redistribute it '\
    'under certain conditions. Its license is the GPL version 3 or later.'

USER_LOCAL_SHARE_FALLBACK = os.path.join(str(Path.home()), '.local', 'share',
                                         __myname__)
USER_LOCAL_SHARE = os.getenv('XDG_DATA_HOME', USER_LOCAL_SHARE_FALLBACK)
# USER_CONFIG_FALLBACK = os.path.join(str(Path.home()), '.config', __myname__)
# USER_CONFIG = os.getenv('XDG_CONFIG_HOME', USER_CONFIG_FALLBACK)
USER_DB_NAME = 'data.db'
USER_DB_PATH = os.path.join(USER_LOCAL_SHARE, USER_DB_NAME)
USER_TEMPLATES_DIRNAME = 'templates'
USER_TEMPLATES_PATH = os.path.join(USER_LOCAL_SHARE, USER_TEMPLATES_DIRNAME)
TEMPLATE_EXT = 'odt'
if not os.path.exists(USER_TEMPLATES_PATH):
    Path(USER_TEMPLATES_PATH).mkdir(parents=True, exist_ok=True)
USER_SWEEPSTAKES_DIRNAME = 'sweepstakes'
USER_SWEEPSTAKES_PATH = os.path.join(USER_LOCAL_SHARE,
                                     USER_SWEEPSTAKES_DIRNAME)
if not os.path.exists(USER_SWEEPSTAKES_PATH):
    Path(USER_SWEEPSTAKES_PATH).mkdir(parents=True, exist_ok=True)

TESTS_DIR = os.path.join(ROOTDIR[:-len(__myname__) - 1], 'tests')
TESTS_DATADIR = os.path.join(TESTS_DIR, 'data')
TEST_DB_PATH = os.path.join(TESTS_DATADIR, 'test.db')
TEST_BUILT_TABLE1_CONTENTXML_PATH = \
    os.path.join(TESTS_DATADIR, 'built_table1_contentxml.xml')
TEST_TEMPLATE1_PATH = os.path.join(TESTS_DATADIR, 'template1.odt')

TEMPLATE_DIR = os.path.join(DATADIR, 'template')
CONTENTXML_PATH = os.path.join(TEMPLATE_DIR, 'content.xml')
