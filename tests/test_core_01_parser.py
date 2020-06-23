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

import pytest

from vocashaker.core.parser import parse_pattern, parse_line, parse_file
from vocashaker.core.errors import MissingSeparatorError
from vocashaker.core.errors import LineDoesNotMatchError
from vocashaker.core.errors import EmptyFileError


def test_parse_pattern():
    p = '<tag1>:<tag2>'
    assert parse_pattern(p) == ('(.*?):(.*?)', ('tag1', 'tag2'))
    with pytest.raises(MissingSeparatorError) as excinfo:
        parse_pattern('<tag1><tag2>')
    assert str(excinfo.value) == 'Missing separator in pattern:\n'\
        '<tag1><tag2>\n'\
        '      ^'
    assert parse_pattern(p, sep_list=True) == ([':'], ('tag1', 'tag2'))
    p = '<Latin> : <Français>'
    assert parse_pattern(p, sep_list=True) == ([' : '], ('Latin', 'Français'))


def test_parse_line():
    p = '<Latin>:<Français>'
    line = 'ambitio, onis, f. : ambition'
    assert parse_line(p, line) == ('ambitio, onis, f.', 'ambition')
    line = 'acies, ei, f ligne de bataille'
    with pytest.raises(LineDoesNotMatchError) as excinfo:
        parse_line(p, line)
    assert str(excinfo.value) == 'This line: acies, ei, f ligne de bataille\n'\
        'does not match provided pattern: <Latin>:<Français>'


def test_parse_clean_file(mocker):
    content = """gaudium,  i, n. : joie

jungo,  is, ere, junxi, junctum : joindre

nosco,  is, ere, novi, notum : apprendre ; pf. savoir

nuntio, as, are : annoncer

soleo,  es, ere, solui, solitum : avoir l'habitude de

solvo,  is, ere, vi, solutum : détacher, payer
"""
    m = mocker.patch('builtins.open', mocker.mock_open(read_data=content))
    result = parse_file('some_file.txt', '<Latin>:<Français>')
    m.assert_called_once_with('some_file.txt')
    expected = [('gaudium,  i, n.', 'joie'),
                ('jungo,  is, ere, junxi, junctum', 'joindre'),
                ('nosco,  is, ere, novi, notum', 'apprendre ; pf. savoir'),
                ('nuntio, as, are', 'annoncer'),
                ('soleo,  es, ere, solui, solitum', "avoir l'habitude de"),
                ('solvo,  is, ere, vi, solutum', 'détacher, payer')]
    assert result[0] == expected
    assert result[1] == []


def test_parse_file_with_errors(mocker):
    content = """gaudium,  i, n. : joie

jungo,  is, ere, junxi, junctum joindre

nosco,  is, ere, novi, notum : apprendre ; pf. savoir

solvo,  is, ere, vi, solutum détacher, payer
"""
    m = mocker.patch('builtins.open', mocker.mock_open(read_data=content))
    result = parse_file('some_file.txt', '<Latin>:<Français>')
    m.assert_called_once_with('some_file.txt')
    expected = [('gaudium,  i, n.', 'joie'),
                ('nosco,  is, ere, novi, notum', 'apprendre ; pf. savoir')]
    assert result[0] == expected
    assert result[1] == ['jungo,  is, ere, junxi, junctum joindre',
                         'solvo,  is, ere, vi, solutum détacher, payer']


def test_parse_empty_file(mocker):
    content = ''
    m = mocker.patch('builtins.open', mocker.mock_open(read_data=content))
    with pytest.raises(EmptyFileError) as excinfo:
        parse_file('empty_file.txt', '<Latin>:<Français>')
    assert str(excinfo.value) == 'The provided file seems empty, could not '\
        'find a single line to parse.'
    m.assert_called_once_with('empty_file.txt')
