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

# import os

# from vocashaker.core import template
from vocashaker.core import commands


def test_list_(testdb, capsys):
    commands.list_()
    captured = capsys.readouterr()
    assert captured.out == 'table1\ntable2\n'


def test_rename(fs, mocker):
    pass
    # mock_rename_table = mocker.patch('vocashaker.core.database.rename_table')
    # fs.create_file(template.path('name1'))
    # commands.rename('name1', 'name2')
    # assert os.path.exists(template.path('name2'))
    # assert mock_rename_table.assert_called_with('name1', 'name2')


def test_delete(fs, mocker):
    pass
    # mock_remove_table = mocker.patch('vocashaker.core.database.remove_table')
    # fs.create_file(template.path('name1'))
    # commands.delete('name1')
    # assert not os.path.exists(template.path('name1'))
    # assert mock_remove_table.assert_called_with('name1')
