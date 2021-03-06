# -*- coding: utf-8 -*-

# Memini is a simple project that creates vocabulary grids to train.
# Copyright 2019 Nicolas Hainaux <nh.techn@gmail.com>

# This file is part of Memini.

# Memini is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# any later version.

# Memini is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Memini; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import sqlite3

import pytest

from memini.core.env import USER_SWEEPSTAKES_PATH
from memini.core import shared
from memini.core.database import Manager
from memini.core.database import list_tables, table_exists
from memini.core.database import _assert_table_exists, _assert_row_exists
from memini.core.database import rename_table, get_table, table_to_text
from memini.core.database import remove_table, create_table, get_cols
from memini.core.database import remove_row, draw_rows, insert_rows
from memini.core.database import get_rows_nb, copy_table, sort_table
from memini.core.database import remove_rows, update_table, merge_tables
from memini.core.database import _timestamp, _reset, _full_reset
from memini.core.database import _intspan2sqllist, _original_name
from memini.core.errors import NoSuchTableError
from memini.core.errors import NoSuchRowError, NoSuchColumnError
from memini.core.errors import ColumnsDoNotMatchError
from memini.core.errors import TooManyRowsRequiredError
from memini.core.errors import DestinationExistsError


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
    assert _assert_table_exists('table1')
    with pytest.raises(NoSuchTableError) as excinfo:
        _assert_table_exists('table4')
    assert str(excinfo.value) == 'Cannot find a table named "table4"'


def test_assert_row_exists(testdb):
    assert _assert_row_exists('table1', 1)
    with pytest.raises(NoSuchRowError) as excinfo:
        _assert_row_exists('table1', 10)
    assert str(excinfo.value) == 'Cannot find a row number 10 in "table1"'


def test_get_cols(testdb):
    assert get_cols('table1') == ['col1', 'col2']
    assert get_cols('table2') == ['col1', 'col2', 'col3']
    assert get_cols('table1', include_id=True) == ['id', 'col1', 'col2']
    assert get_cols('table2', include_id=True) == ['id', 'col1', 'col2',
                                                   'col3']


def test_get_rows_nb(testdb):
    assert get_rows_nb('table1') == 4


def test_get_table(testdb):
    assert get_table('table2') \
        == [('1', 'begin', 'began, begun', 'commencer'),
            ('2', 'break', 'broke, broken', 'casser'),
            ('3', 'do', 'did, done', 'faire'),
            ('4', 'give', 'gave, given', 'donner')]
    assert get_table('table2', include_headers=True) \
        == [('id', 'col1', 'col2', 'col3'),
            ('1', 'begin', 'began, begun', 'commencer'),
            ('2', 'break', 'broke, broken', 'casser'),
            ('3', 'do', 'did, done', 'faire'),
            ('4', 'give', 'gave, given', 'donner')]
    with pytest.raises(NoSuchTableError) as excinfo:
        get_table('table3')
    assert str(excinfo.value) == 'Cannot find a table named "table3"'
    with pytest.raises(NoSuchColumnError) as excinfo:
        get_table('table1', sort=3)
    assert str(excinfo.value) == 'Cannot find a column number 3 in "table1"'
    assert get_table('table2', include_headers=True, sort=3) \
        == [('id', 'col1', 'col2', 'col3'),
            ('2', 'break', 'broke, broken', 'casser'),
            ('1', 'begin', 'began, begun', 'commencer'),
            ('4', 'give', 'gave, given', 'donner'),
            ('3', 'do', 'did, done', 'faire')]


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
    assert table_to_text('table2', '<col1>, <col2> : <col3>') \
        == """begin, began, begun : commencer
break, broke, broken : casser
do, did, done : faire
give, gave, given : donner"""


def test_rename_table(testdb):
    table1_content = table_to_text('table1', '<Latin> : <Français>')
    rename_table('table1', 'table4')
    assert not table_exists('table1')
    assert table_exists('table4')
    with pytest.raises(NoSuchTableError) as excinfo:
        rename_table('table1', 'table4')
    assert str(excinfo.value) == 'Cannot find a table named "table1"'
    assert table1_content == table_to_text('table4', '<Latin> : <Français>')


def test_copy_table(testdb):
    copy_table('table1', 'table4')
    assert table_exists('table1')
    assert table_exists('table4')
    assert table_to_text('table1', '<Latin> : <Français>') \
        == table_to_text('table4', '<Latin> : <Français>')
    with pytest.raises(DestinationExistsError) as excinfo:
        copy_table('table4', 'table2')
    assert str(excinfo.value) == 'Action cancelled: a table named "table2" '\
        'already exists. Please rename or remove it before using this name.'


def test_update_table(testdb):
    update_table('table1', 3, ['spes, ei f', 'espoir'])
    assert get_table('table1') == \
        [('1', 'adventus,  us, m.', 'arrivée'),
         ('2', 'aqua , ae, f', 'eau'),
         ('3', 'spes, ei f', 'espoir'),
         ('4', 'sol, solis, m', 'soleil')]
    with pytest.raises(ColumnsDoNotMatchError) as excinfo:
        update_table('table1', 3, ['spes, ei', 'f', 'espoir'])
    assert str(excinfo.value) == '"[\'spes, ei\', \'f\', \'espoir\']" '\
        'requires 3 columns, but "table1" has 2 columns ("col1" and "col2").'


def test_original_name(testdb):
    assert _original_name('table1') == 'table1_0'
    create_table('table2_0', ['col1', 'col2'])
    create_table('table2_1', ['col1', 'col2'])
    create_table('table2_2', ['col1', 'col2'])
    assert _original_name('table2') == 'table2_3'


def test_sort_table(testdb):
    sort_table('table1', 2)
    assert table_exists('table1')
    assert not table_exists('table1_copy')
    assert get_table('table1') \
        == [('1', 'adventus,  us, m.', 'arrivée'),
            ('2', 'candidus,  a, um', 'blanc'),
            ('3', 'aqua , ae, f', 'eau'),
            ('4', 'sol, solis, m', 'soleil')]
    with pytest.raises(NoSuchColumnError) as excinfo:
        sort_table('table1', 3)
    assert str(excinfo.value) == 'Cannot find a column number 3 in "table1"'
    sort_table('table2', 3)
    assert get_table('table2', include_headers=True) \
        == [('id', 'col1', 'col2', 'col3'),
            ('1', 'break', 'broke, broken', 'casser'),
            ('2', 'begin', 'began, begun', 'commencer'),
            ('3', 'give', 'gave, given', 'donner'),
            ('4', 'do', 'did, done', 'faire')]


def test_remove_table(testdb, mocker):
    remove_table('table1')
    assert list_tables() == ['table2']
    with pytest.raises(NoSuchTableError) as excinfo:
        remove_table('table1')
    assert str(excinfo.value) == 'Cannot find a table named "table1"'


def test_create_table(testdb, mocker):
    create_table('table3', ['infinitif', 'passé', 'français'],
                 [('bieten', 'bot, hat geboten', 'offrir'),
                  ('bleiben', 'blieb, ist geblieben', 'rester'),
                  ('gelingen', 'gelang, ist gelungen', 'réussir'),
                  ('schmelzen', 'schmolz, ist geschmolzen', 'fondre'),
                  ('ziegen', 'zog, hat OU ist gezogen', 'tirer OU déménager'),
                  ])
    assert list_tables() == ['table1', 'table2', 'table3']
    assert get_table('table3') \
        == [('1', 'bieten', 'bot, hat geboten', 'offrir'),
            ('2', 'bleiben', 'blieb, ist geblieben', 'rester'),
            ('3', 'gelingen', 'gelang, ist gelungen', 'réussir'),
            ('4', 'schmelzen', 'schmolz, ist geschmolzen', 'fondre'),
            ('5', 'ziegen', 'zog, hat OU ist gezogen', 'tirer OU déménager'),
            ]


def test_insert_rows(testdb):
    insert_rows('table1', [('spes, ei f', 'espoir')])
    assert get_table('table1') \
        == [('1', 'adventus,  us, m.', 'arrivée'),
            ('2', 'aqua , ae, f', 'eau'),
            ('3', 'candidus,  a, um', 'blanc'),
            ('4', 'sol, solis, m', 'soleil'),
            ('5', 'spes, ei f', 'espoir')]
    with pytest.raises(NoSuchTableError) as excinfo:
        insert_rows('table3', [('spes, ei', 'f', 'espoir')])
    assert str(excinfo.value) == 'Cannot find a table named "table3"'
    with pytest.raises(ColumnsDoNotMatchError) as excinfo:
        insert_rows('table1', [('spes, ei', 'f', 'espoir')])
    assert str(excinfo.value) == '"\'spes, ei\', \'f\', \'espoir\'" '\
        'requires 3 columns, but "table1" has 2 columns ("col1" and "col2").'
    insert_rows('table1', [('amor,  oris, m.', 'amour'),
                           ('anima,  ae, f.', 'coeur, âme'),
                           ('hiems, mis,f', 'hiver')])
    assert get_table('table1') \
        == [('1', 'adventus,  us, m.', 'arrivée'),
            ('2', 'aqua , ae, f', 'eau'),
            ('3', 'candidus,  a, um', 'blanc'),
            ('4', 'sol, solis, m', 'soleil'),
            ('5', 'spes, ei f', 'espoir'),
            ('6', 'amor,  oris, m.', 'amour'),
            ('7', 'anima,  ae, f.', 'coeur, âme'),
            ('8', 'hiems, mis,f', 'hiver')]


def test_merge_tables(testdb):
    with pytest.raises(ColumnsDoNotMatchError) as excinfo:
        merge_tables('table1', 'table2')
    assert str(excinfo.value) == '"table1" requires 2 columns, but "table2" '\
        'has 3 columns ("col1", "col2" and "col3").'
    create_table('table3', ['col3', 'col4'],
                 [('spes, ei f', 'espoir'),
                 ('amor,  oris, m.', 'amour'),
                 ('anima,  ae, f.', 'coeur, âme'),
                 ('hiems, mis,f', 'hiver')])
    merge_tables('table1', 'table3')
    assert get_table('table3') \
        == [('1', 'spes, ei f', 'espoir'),
            ('2', 'amor,  oris, m.', 'amour'),
            ('3', 'anima,  ae, f.', 'coeur, âme'),
            ('4', 'hiems, mis,f', 'hiver'),
            ('5', 'adventus,  us, m.', 'arrivée'),
            ('6', 'aqua , ae, f', 'eau'),
            ('7', 'candidus,  a, um', 'blanc'),
            ('8', 'sol, solis, m', 'soleil')
            ]


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
            ('2', 'candidus,  a, um', 'blanc'),
            ('3', 'sol, solis, m', 'soleil')]


def test_intspan2sqllist():
    assert _intspan2sqllist('1-3,14,29,92-97') == \
        '(1, 2, 3, 14, 29, 92, 93, 94, 95, 96, 97)'


def test_remove_rows(testdb):
    with pytest.raises(NoSuchRowError) as excinfo:
        remove_rows('table1', '2-5')
    assert str(excinfo.value) == 'Cannot find a row number 5 in "table1"'
    remove_rows('table1', '1-3')
    assert get_table('table1') \
        == [('1', 'sol, solis, m', 'soleil')]


def test_timestamp(testdb):
    _timestamp('table1', 1)
    stamped = shared.db.execute('SELECT id FROM table1 WHERE timestamp != 0;')\
        .fetchall()
    assert stamped == [(1, )]


def test_reset(testdb):
    _timestamp('table1', 1)
    _timestamp('table1', 2)
    _timestamp('table1', 3)
    _timestamp('table1', 4)
    _reset('table1', 1)
    stamped = shared.db.execute('SELECT id FROM table1 WHERE timestamp != 0;')\
        .fetchall()
    assert len(stamped) == 3
    _timestamp('table1', 1)
    _timestamp('table1', 2)
    _timestamp('table1', 3)
    _timestamp('table1', 4)
    _reset('table1', 3)
    stamped = shared.db.execute('SELECT id FROM table1 WHERE timestamp != 0;')\
        .fetchall()
    assert len(stamped) == 1
    _timestamp('table1', 1)
    _timestamp('table1', 2)
    _timestamp('table1', 3)
    _full_reset('table1')
    stamped = shared.db.execute('SELECT id FROM table1 WHERE timestamp != 0;')\
        .fetchall()
    assert len(stamped) == 0


def test_draw_rows(testdb, fs):
    fs.create_dir(USER_SWEEPSTAKES_PATH)
    with pytest.raises(NoSuchTableError) as excinfo:
        draw_rows('table3', 2)
    assert str(excinfo.value) == 'Cannot find a table named "table3"'
    with pytest.raises(TooManyRowsRequiredError) as excinfo:
        draw_rows('table1', 5)
    assert str(excinfo.value) == '5 rows are required from "table1", '\
        'but it only contains 4 rows.'
    result = draw_rows('table1', 2)
    assert len(result) == 2
    assert all([type(r) == tuple for r in result])
    assert all([len(r) == 2 for r in result])
    _full_reset('table1')
    _timestamp('table1', 1)
    _timestamp('table1', 2)
    result = draw_rows('table1', 2, oldest_prevail=True)
    assert ('candidus,  a, um', 'blanc') in result
    assert ('sol, solis, m', 'soleil') in result
    _full_reset('table1')
    _timestamp('table1', 1)
    _timestamp('table1', 2)
    _timestamp('table1', 3)
    result = draw_rows('table1', 2, oldest_prevail=True)
    assert ('sol, solis, m', 'soleil') in result
