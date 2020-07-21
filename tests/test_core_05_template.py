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

import os
import zipfile
from unittest.mock import patch

import pytest

from memini.core import template, prefs
from memini.core.env import TEST_BUILT_TABLE1_CONTENTXML_PATH, PROG_NAME
from memini.core.env import CONTENTXML_PATH, TESTS_DATADIR
from memini.core.env import USER_TEMPLATES_PATH, TEMPLATE_EXT
from memini.core.errors import NotATemplateError


def test_path():
    expected = os.path.join(USER_TEMPLATES_PATH,
                            f'NAME.{TEMPLATE_EXT}')
    assert template.path('NAME') == expected


def test_list_(fs):
    fs.create_file(template.path('table1'))
    fs.create_file(template.path('table2'))
    assert template.list_() == ['table1.odt', 'table2.odt']


def test_exists(mocker):
    mock_os_is_file = mocker.patch('os.path.isfile')
    mock_path = mocker.patch('memini.core.template.path')
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
    with open(TEST_BUILT_TABLE1_CONTENTXML_PATH, 'r', encoding='utf8') as f:
        expected = f.read()
    assert created == expected


def test_create(testdb, mocker):
    m1 = mocker.mock_open()
    m2 = mocker.patch('memini.core.template._prepare_content')
    m2.return_value = 'some stuff'
    m3 = mocker.patch('os.remove')
    mocker.patch('shutil.make_archive')
    mocker.patch('shutil.move')
    with patch('builtins.open', m1, create=True):
        template.create('table1')
    m1.assert_called_with(CONTENTXML_PATH, 'w', encoding=prefs.ENCODING)
    m2.assert_called_with('table1')
    m3.assert_called_with(CONTENTXML_PATH)


def test_check():
    correct_template = os.path.join(TESTS_DATADIR, 'template1.odt')
    assert template._check(correct_template)
    wrong_template = os.path.join(TESTS_DATADIR, 'template_faked.odt')
    assert not template._check(wrong_template)


def test_LO_saved_content_xml_detected():
    wrong_content_xml = os.path.join(TESTS_DATADIR, 'wrong_content.xml')
    fixed_content_xml = os.path.join(TESTS_DATADIR, 'fixed_content.xml')
    assert template._LO_saved_content_xml_detected(wrong_content_xml)
    assert not template._LO_saved_content_xml_detected(fixed_content_xml)
    buggy = os.path.join(TESTS_DATADIR, 'LO_modified_buggy.odt')
    with zipfile.ZipFile(buggy, 'r') as z:
        with z.open('content.xml') as f:
            assert template._LO_saved_content_xml_detected(f)


def test_fix_LO_saved_content_xml():
    wrong_content_xml = os.path.join(TESTS_DATADIR, 'wrong_content.xml')
    fixed_content_xml = os.path.join(TESTS_DATADIR, 'fixed_content.xml')
    with open(wrong_content_xml, 'r') as infile,\
         open(fixed_content_xml, 'r') as outfile:
        assert template._fix_LO_saved_content_xml(infile.readlines()).strip() \
            == '\n'.join(outfile.readlines()).strip()


def test_get_cols_nb():
    t2 = os.path.join(TESTS_DATADIR, 'template1.odt')
    assert template.get_cols_nb(t2) == 2
    t3 = os.path.join(TESTS_DATADIR, 'template3.odt')
    assert template.get_cols_nb(t3) == 3
    t4 = os.path.join(TESTS_DATADIR, 'template4.odt')
    assert template.get_cols_nb(t4) == 4

    ft = os.path.join(TESTS_DATADIR, 'template_faked.odt')
    with pytest.raises(NotATemplateError) as excinfo:
        template.get_cols_nb(ft)
    assert str(excinfo.value) == 'This file: template_faked.odt does not look'\
        f' like a {PROG_NAME} template.'

    ft = os.path.join(TESTS_DATADIR, 'defect_template.odt')
    with pytest.raises(NotATemplateError) as excinfo:
        template.get_cols_nb(ft)
    assert str(excinfo.value) == 'This file: defect_template.odt does not '\
        f'look like a {PROG_NAME} template.'

    mt = os.path.join(TESTS_DATADIR, 'modified_template.odt')
    assert template.get_cols_nb(mt) == 2


def test_sanitize(fs):
    buggy = os.path.join(TESTS_DATADIR, 'LO_modified_buggy.odt')
    fixed = os.path.join(TESTS_DATADIR, 'LO_modified_fixed.odt')
    fs.add_real_file(buggy)
    fs.add_real_file(fixed)
    assert template.sanitize(buggy)
    assert not template.sanitize(fixed)
