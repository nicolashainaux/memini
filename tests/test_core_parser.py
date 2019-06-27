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

from vocashaker.core.parser import parse_pattern, parse_line
from vocashaker.core.errors import PatternError, MismatchError


def test_parse_pattern():
    p = '<tag1>:<tag2>'
    assert parse_pattern(p) == ('(.*?):(.*?)', ['tag1', 'tag2'])
    with pytest.raises(PatternError) as excinfo:
        parse_pattern('<tag1><tag2>')
    assert str(excinfo.value) == 'Missing separator in pattern:\n'\
        '<tag1><tag2>\n'\
        '      ^'


def test_parse_line():
    p = '<Latin>:<Français>'
    line = 'ambitio, onis, f. : ambition'
    assert parse_line(p, line) == ['ambitio, onis, f.', 'ambition']
    line = 'acies, ei, f ligne de bataille'
    with pytest.raises(MismatchError) as excinfo:
        parse_line(p, line)
    assert str(excinfo.value) == 'This line: acies, ei, f ligne de bataille\n'\
        'does not match provided pattern: <Latin>:<Français>'
