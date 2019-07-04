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
from vocashaker.core.database import list_tables, table_exists
from vocashaker.core.database import assert_table_exists
from vocashaker.core.database import rename_table, get_table, table_to_text
from vocashaker.core.database import remove_table, create_table
from vocashaker.core.database import add_row, remove_row, draw_rows
from vocashaker.core.errors import NoSuchTableError
from vocashaker.core.errors import NoSuchRowError
from vocashaker.core.errors import ColumnsDoNotMatchError


@pytest.fixture
def testdb():
    testdb_conn = sqlite3.connect(TEST_DB_PATH)
    shared.db = testdb_conn.cursor()
    shared.db.execute('SAVEPOINT starttest;')
    yield
    # Using testdb_conn.rollback() would not rollback certain transactions
    # like RENAME...
    shared.db.execute('ROLLBACK TO SAVEPOINT starttest;')
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


def test_assert_table_exists(testdb):
    assert assert_table_exists('table1')
    with pytest.raises(NoSuchTableError) as excinfo:
        assert_table_exists('table4')
    assert str(excinfo.value) == 'Cannot find a table named "table4"'


def test_rename_table(testdb):
    rename_table('table1', 'table4')
    assert not table_exists('table1')
    assert table_exists('table4')
    with pytest.raises(NoSuchTableError) as excinfo:
        rename_table('table1', 'table4')
    assert str(excinfo.value) == 'Cannot find a table named "table1"'


def test_get_table(testdb):
    assert get_table('table2') \
        == [('1', 'begin', 'began, begun', 'commencer'),
            ('2', 'break', 'broke, broken', 'casser'),
            ('3', 'do', 'did, done', 'faire'),
            ('4', 'give', 'gave, given', 'donner')]
    with pytest.raises(NoSuchTableError) as excinfo:
        get_table('table3')
    assert str(excinfo.value) == 'Cannot find a table named "table3"'


def test_table_to_text(testdb):
    assert table_to_text('table1', '<Latin> : <Français>') \
        == """adventus,  us, m. : arrivée
aqua , ae, f : eau
candidus,  a, um : blanc
sol, solis, m : soleil"""
    with pytest.raises(NoSuchTableError) as excinfo:
        table_to_text('table3', '<Latin> : <Français>')
    assert str(excinfo.value) == 'Cannot find a table named "table3"'
    with pytest.raises(ColumnsDoNotMatchError) as excinfo:
        table_to_text('table1', '<Latin> : <Français> : <Grec>')
    assert str(excinfo.value) == '"<Latin> : <Français> : <Grec>" requires ' \
        '3 columns, but "table1" has 2 columns ("col1" and "col2").'


def test_remove_table(testdb):
    remove_table('table1')
    assert list_tables() == ['table2']
    with pytest.raises(NoSuchTableError) as excinfo:
        remove_table('table1')
    assert str(excinfo.value) == 'Cannot find a table named "table1"'


def test_create_table(testdb):
    create_table('table3', ('infinitif', 'passé', 'français'),
                 [('bieten', 'bot, hat geboten', 'offrir'),
                  ('bleiben', 'blieb, ist geblieben', 'rester'),
                  ('gelingen', 'gelang, ist gelungen', 'réussir')
                  ('schmelzen', 'schmolz, ist geschmolzen', 'fondre'),
                  ('ziegen', 'zog, hat OU ist gezogen', 'tirer OU déménager'),
                  ])
    assert list_tables() == ['table1', 'table2', 'table3']
    assert get_table('table3') \
        == [('1', 'bieten', 'bot, hat geboten', 'offrir'),
            ('2', 'bleiben', 'blieb, ist geblieben', 'rester'),
            ('3', 'gelingen', 'gelang, ist gelungen', 'réussir')
            ('4', 'schmelzen', 'schmolz, ist geschmolzen', 'fondre'),
            ('5', 'ziegen', 'zog, hat OU ist gezogen', 'tirer OU déménager'),
            ]


def test_add_row(testdb):
    add_row('table1', ('spes, ei f', 'espoir'))
    assert get_table('table1') \
        == [('1', 'adventus,  us, m.', 'arrivée'),
            ('2', 'aqua , ae, f', 'eau'),
            ('3', 'candidus,  a, um', 'blanc'),
            ('4', 'sol, solis, m', 'soleil'),
            ('5', 'spes, ei f', 'espoir')]
    with pytest.raises(NoSuchTableError) as excinfo:
        add_row('table3', ('spes, ei', 'f', 'espoir'))
    assert str(excinfo.value) == 'Cannot find a table named "table3"'
    with pytest.raises(ColumnsDoNotMatchError) as excinfo:
        add_row('table1', ('spes, ei', 'f', 'espoir'))
    assert str(excinfo.value) == '("\'spes, ei\', \'f\', \'espoir\'") '\
        'requires 3 columns, but "table1" has 2 columns ("col1" and "col2").'


def test_remove_row(testdb):
    with pytest.raises(NoSuchTableError) as excinfo:
        remove_row('table3', 2)
    assert str(excinfo.value) == 'Cannot find a table named "table3"'
    with pytest.raises(NoSuchRowError) as excinfo:
        remove_row('table1', 7)
    assert str(excinfo.value) == 'Cannot find a row number 7 in "table1"'
    remove_row('table1', 2)
    assert get_table('table1') \
        == [('1', 'adventus,  us, m.', 'arrivée'),
            ('3', 'candidus,  a, um', 'blanc'),
            ('4', 'sol, solis, m', 'soleil')]


def test_draw_rows(testdb):
    with pytest.raises(NoSuchTableError) as excinfo:
        draw_rows('table3', 2)
    assert str(excinfo.value) == 'Cannot find a table named "table3"'
    result = draw_rows('table1', 2)
    assert len(result) == 2
    # Check there are two timestamped data
