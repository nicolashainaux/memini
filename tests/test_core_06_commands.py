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

import pytest

from vocashaker.core import template
from vocashaker.core import commands
from vocashaker.core import database
from vocashaker.core.errors import NoSuchTableError, DestinationExistsError


def test_list_(testdb, capsys):
    commands.list_()
    captured = capsys.readouterr()
    assert captured.out == 'table1\ntable2\n'


def test_rename(testdb, fs, mocker, capsys):
    m = mocker.patch('vocashaker.core.database.rename_table')
    fs.create_file(template.path('table1'))
    commands.rename('table1', 'table3')
    assert os.path.exists(template.path('table3'))
    assert not os.path.exists(template.path('table1'))
    m.assert_called_with('table1', 'table3')


def test_rename_unknown_table(testdb):
    with pytest.raises(NoSuchTableError) as excinfo:
        commands.rename('unknown', 'newname')
    assert str(excinfo.value) == 'Cannot find a table named "unknown"'


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


def test_delete(fs, mocker):
    pass
    # mock_remove_table = mocker.patch('vocashaker.core.database.remove_table')
    # fs.create_file(template.path('name1'))
    # commands.delete('name1')
    # assert not os.path.exists(template.path('name1'))
    # assert mock_remove_table.assert_called_with('name1')
