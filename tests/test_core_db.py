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

import pytest
import sqlite3

from vocashaker.core.db import Connect
# from vocashaker.core.db import table_exists


def test_Connect():
    with Connect(':memory:') as c:
        cmd = """CREATE TABLE test1
                 (id INTEGER PRIMARY KEY, col1 INTEGER, col2 INTEGER)"""
        c.execute(cmd)
    # Check that, out of the with statement, the connection is *closed*
    # (not only committed)
    with pytest.raises(sqlite3.ProgrammingError) as excinfo:
        c.execute('SELECT 1 FROM test1;')
    assert str(excinfo.value) == 'Cannot operate on a closed database.'

# def test_table_exists():
#     pass
