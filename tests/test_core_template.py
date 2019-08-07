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
import sqlite3
# import unittest.mock as mock

import pytest

from vocashaker.core import shared, template
from vocashaker.core.env import TEST_DB_PATH
from vocashaker.core.env import TEST_BUILT_TABLE1_CONTENTXML_PATH
from vocashaker.core.env import USER_TEMPLATES_PATH, TEMPLATE_EXT


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


def test_path():
    expected = os.path.join(USER_TEMPLATES_PATH,
                            'NAME.{}'.format(TEMPLATE_EXT))
    assert template.path('NAME') == expected


def test_exists(mocker):
    mock_os_is_file = mocker.patch('os.path.isfile')
    mock_path = mocker.patch('vocashaker.core.template.path')
    mock_path.return_value = '/path/to/template.odt'
    mock_os_is_file.return_value = True
    assert template.exists('table1')
    mock_os_is_file.assert_called_with('/path/to/template.odt')
    mock_os_is_file.return_value = False
    assert not template.exists('table2')
    mock_os_is_file.assert_called_with('/path/to/template.odt')


def test_prepare_content(testdb):
    created = template._prepare_content('table1')
    with open(TEST_BUILT_TABLE1_CONTENTXML_PATH, 'r') as f:
        expected = f.read()
    assert created == expected


# @mock.patch('tarfile.open')
# def test_create(testdb, mock_tarfile_open):
    #     template.create('table1')
    # assert not os.path.isfile(CONTENTXML_PATH)
