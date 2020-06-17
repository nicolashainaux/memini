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
from unittest.mock import patch

from vocashaker.core import template, prefs
from vocashaker.core.env import TEST_BUILT_TABLE1_CONTENTXML_PATH
from vocashaker.core.env import CONTENTXML_PATH
from vocashaker.core.env import USER_TEMPLATES_PATH, TEMPLATE_EXT


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


def test_create(testdb, mocker):
    m1 = mocker.mock_open()
    m2 = mocker.patch('vocashaker.core.template._prepare_content')
    m2.return_value = 'some stuff'
    m3 = mocker.patch('os.remove')
    mocker.patch('shutil.make_archive')
    mocker.patch('shutil.move')
    with patch('builtins.open', m1, create=True):
        template.create('table1')
    m1.assert_called_with(CONTENTXML_PATH, 'w')
    m2.assert_called_with('table1')
    m3.assert_called_with(CONTENTXML_PATH)
