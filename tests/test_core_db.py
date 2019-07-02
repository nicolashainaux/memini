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

import sqlite3

import pytest

from vocashaker.core import shared
from vocashaker.core.env import TEST_DB_PATH
from vocashaker.core.database import Manager
from vocashaker.core.database import list_tables
from vocashaker.core.database import table_exists


@pytest.fixture
def testdb():
    testdb_conn = sqlite3.connect(TEST_DB_PATH)
    shared.db = testdb_conn.cursor()
    yield
    testdb_conn.rollback()
    testdb_conn.close()


def test_Manager():
    with Manager(':memory:') as db:
        cmd = """CREATE TABLE test1
                 (id INTEGER PRIMARY KEY, col1 INTEGER, col2 INTEGER)"""
        db.execute(cmd)
    # Check that, out of the with statement, the connection is *closed*
    # (not only committed)
    with pytest.raises(sqlite3.ProgrammingError) as excinfo:
        db.execute('SELECT 1 FROM test1;')
    assert str(excinfo.value) == 'Cannot operate on a closed database.'


def test_list_tables(testdb):
    assert list_tables() == ['table1', 'table2']


def test_table_exists(testdb):
    assert table_exists('table1')
    assert not table_exists('TABLE1')
