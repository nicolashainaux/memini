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
from unittest.mock import mock_open, patch
# import unittest.mock as mock

import pytest

from vocashaker.core import shared, template, prefs
from vocashaker.core.env import TEST_DB_PATH
from vocashaker.core.env import TEST_BUILT_TABLE1_CONTENTXML_PATH
from vocashaker.core.env import CONTENTXML_PATH
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


def test_edit(mocker):
    mock_popen = mocker.patch('subprocess.Popen')
    template.edit('table1')
    mock_popen.assert_called_with([prefs.EDITOR, template.path('table1')])


def test_prepare_content(testdb):
    created = template._prepare_content('table1')
    with open(TEST_BUILT_TABLE1_CONTENTXML_PATH, 'r') as f:
        expected = f.read()
    assert created == expected


def test_files_to_add(mocker):
    mock_listdir = mocker.patch('os.listdir')
    mock_listdir.return_value = ['content2.xml', 'layout-cache', 'styles.xml',
                                 'mimetype', 'meta.xml', 'META-INF',
                                 'content4.xml', 'settings.xml',
                                 'content3.xml', 'manifest.rdf']
    expected = ['/path/to/layout-cache', '/path/to/styles.xml',
                '/path/to/mimetype', '/path/to/meta.xml', '/path/to/META-INF',
                '/path/to/settings.xml', '/path/to/manifest.rdf']
    assert template._files_to_add('/path/to') == expected


def test_create(testdb, mocker):
    m1 = mocker.mock_open()
    m2 = mocker.patch('tarfile.open', autospec=True, create=True)
    m3 = mocker.patch('os.remove')
    m4 = mocker.patch('vocashaker.core.template._files_to_add')
    m4.return_value = ['/path/to/file1', '/path/to/file2']
    with patch('builtins.open', m1, create=True):
        with patch('tarfile.open', m2, create=True):
            template.create('table1')
    m2.assert_called_with(template.path('table1'), 'w:gz')
    m3.assert_called_with(CONTENTXML_PATH)
    handle = m2()
    print(handle.mock_calls)
    handle.add.assert_called_with('/path/to/file1', arcname='file1')
    handle.add.assert_called_with('/path/to/file2', arcname='file2')
