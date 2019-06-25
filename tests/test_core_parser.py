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


def test_parse_pattern():
    p = '<tag1>:<tag2>'
    assert parse_pattern(p) == (':', ['tag1', 'tag2'])
    with pytest.raises(ValueError) as excinfo:
        parse_pattern('<tag1><tag2>')
    assert str(excinfo.value) == 'Cannot find a separator between tags in '\
        'this string: <tag1><tag2>'


def test_parse_line():
    p = '<Latin>:<Français>'
    line = 'ambitio, onis, f. : ambition'
    assert parse_line(line, p) == ['ambitio, onis, f.', 'ambition']
    # line1 = 'acies, ei, f ligne de bataille'
    # line2 = 'agmen, minis,n armée en marche'
    # line3 = ' ager, gri, m champ'
