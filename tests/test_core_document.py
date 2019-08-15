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

from vocashaker.core.errors import SchemeSyntaxError, SchemeLogicalError
from vocashaker.core.document import _default_scheme, _parse_scheme


def test_default_scheme():
    assert _default_scheme(2) == '__1'
    assert _default_scheme(3) == '___2'
    assert _default_scheme(4) == '____3'
    assert _default_scheme(5) == '_____4'


def test_parse_scheme():
    with pytest.raises(SchemeSyntaxError) as excinfo:
        _parse_scheme('_F*')
    assert str(excinfo.value) == 'Incorrect scheme: "_F*". A scheme should '\
        'contain underscore and star chars ("_" and "*"), plus possibly one '\
        'digit as last char.'
    with pytest.raises(SchemeLogicalError) as excinfo:
        _parse_scheme('_*_3')
    assert str(excinfo.value) == 'Incorrect scheme: "_*_3". It shows 3 '\
        'columns, hence 2 of them at most can be blank, not more (3).'
    with pytest.raises(SchemeLogicalError) as excinfo:
        _parse_scheme('_*_4')
    assert str(excinfo.value) == 'Incorrect scheme: "_*_4". It shows 3 '\
        'columns, hence 2 of them at most can be blank, not more (4).'
    with pytest.raises(SchemeLogicalError) as excinfo:
        _parse_scheme('***')
    assert str(excinfo.value) == 'Incorrect scheme: "***". A scheme should '\
        'contain at least one possible blank column ("_").'
    with pytest.raises(SchemeLogicalError) as excinfo:
        _parse_scheme('**_2')
    assert str(excinfo.value) == 'Incorrect scheme: "**_2". It shows less '\
        'possible blank columns (1 "_") than it requires (2).'

    assert _parse_scheme('**_') == ([2], 1)
    assert _parse_scheme('___') == ([0, 1, 2], 2)
    assert _parse_scheme('___1') == ([0, 1, 2], 1)
