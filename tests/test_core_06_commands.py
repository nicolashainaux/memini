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
from unittest.mock import call

import pytest

from vocashaker.core import template
from vocashaker.core import commands
from vocashaker.core import database
from vocashaker.core.errors import NoSuchTableError, DestinationExistsError
from vocashaker.core.errors import NotFoundError, CommandError


def test_list_(testdb, capsys, fs):
    fs.create_file(template.path('template1'))
    fs.create_file(template.path('template2'))
    commands.list_('tables')
    captured = capsys.readouterr()
    assert captured.out == 'table1\ntable2\n'
    commands.list_('templates')
    captured = capsys.readouterr()
    assert captured.out == 'template1.odt\ntemplate2.odt\n'
    with pytest.raises(CommandError) as excinfo:
        commands.list_('foo')
    assert str(excinfo.value) == 'I can list "tables" or "templates". '\
        'I don\'t know what "foo" might mean.'


def test_rename(testdb, fs, mocker):
    m = mocker.patch('vocashaker.core.database.rename_table')
    fs.create_file(template.path('table1'))
    commands.rename('table1', 'table3')
    assert os.path.exists(template.path('table3'))
    assert not os.path.exists(template.path('table1'))
    m.assert_called_with('table1', 'table3')


def test_rename_nonexistent_table(testdb):
    with pytest.raises(NoSuchTableError) as excinfo:
        commands.rename('nonexistent', 'newname')
    assert str(excinfo.value) == 'Cannot find a table named "nonexistent"'


def test_rename_missing_template(testdb, fs, mocker):
    # No template for source table: automatic creation
    def create_fake_template(*args):
        fs.create_file(template.path('table1'))

    m = mocker.patch('vocashaker.core.template.create',
                     side_effect=create_fake_template)
    commands.rename('table1', 'table4')
    m.assert_called_with('table1')
    assert os.path.exists(template.path('table4'))
    assert not os.path.exists(template.path('table1'))
    assert database.table_exists('table4')
    assert not database.table_exists('table1')


def test_rename_to_existing_table(testdb, fs):
    fs.create_file(template.path('table1'))

    with pytest.raises(DestinationExistsError) as excinfo:
        commands.rename('table1', 'table2')
    assert str(excinfo.value) == 'Action cancelled: a table named "table2" '\
        'already exists. Please rename or remove it before using this name.'


def test_rename_to_existing_template(testdb, fs):
    fs.create_file(template.path('table1'))
    fs.create_file(template.path('table3'))

    with pytest.raises(DestinationExistsError) as excinfo:
        commands.rename('table1', 'table3')
    assert str(excinfo.value) == 'Action cancelled: a template named '\
        '"table3" already exists. Please rename or remove it before using '\
        'this name.'


def test_delete(fs, mocker, testdb):
    fs.create_file(template.path('table1'))
    m = mocker.patch('vocashaker.core.terminal.ask_yes_no')

    # User cancels the deletions
    m.side_effect = [False, False]
    commands.delete('table1')
    m.assert_has_calls([call('Delete table "table1"?'),
                        call('Delete template "table1"?')])
    assert os.path.exists(template.path('table1'))
    assert database.table_exists('table1')

    # User confirms the deletions
    m.side_effect = [True, True]
    commands.delete('table1')
    assert not os.path.exists(template.path('table1'))
    assert not database.table_exists('table1')


def test_delete_nonexistent(testdb):
    with pytest.raises(NotFoundError) as excinfo:
        commands.delete('table3')
    assert str(excinfo.value) == 'No table nor template named "table3" can '\
        'be found to be deleted.'


def test_show_nonexistent(testdb):
    with pytest.raises(NoSuchTableError) as excinfo:
        commands.show('nonexistent')
    assert str(excinfo.value) == 'Cannot find a table named "nonexistent"'


def test_show(testdb, capsys):
    commands.show('table2')
    captured = capsys.readouterr()
    assert captured.out == \
        " id |  col1 |      col2     |    col3   \n"\
        "----+-------+---------------+-----------\n"\
        "  1 | begin |  began, begun | commencer \n"\
        "  2 | break | broke, broken |   casser  \n"\
        "  3 |   do  |   did, done   |   faire   \n"\
        "  4 |  give |  gave, given  |   donner  \n"
