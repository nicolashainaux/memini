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

import toml


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
