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

# import pytest
from decimal import Decimal

from vocashaker.core.template import _colwidth, _lastcolid, _more_row_cells


def test_colwidth():
    assert _colwidth(4) == (Decimal('4.9'), 16384)


def test_lastcolid():
    assert _lastcolid(4) == 'D'


def test_more_row_cells():
    assert _more_row_cells(0, 1, 2) == """
<table:table-cell table:style-name="Tableau1.B1" office:value-type="string">
    <text:p text:style-name="P5">__COL2__</text:p>
</table:table-cell>"""
    assert _more_row_cells(0, 2, 3) == """
<table:table-cell table:style-name="Tableau2.A1" office:value-type="string">
    <text:p text:style-name="P6">__COL2__</text:p>
</table:table-cell>
<table:table-cell table:style-name="Tableau2.C1" office:value-type="string">
    <text:p text:style-name="P6">__COL3__</text:p>
</table:table-cell>"""
    assert _more_row_cells(0, 1, 4) == """
<table:table-cell table:style-name="Tableau1.A1" office:value-type="string">
    <text:p text:style-name="P5">__COL2__</text:p>
</table:table-cell>
<table:table-cell table:style-name="Tableau1.A1" office:value-type="string">
    <text:p text:style-name="P5">__COL3__</text:p>
</table:table-cell>
<table:table-cell table:style-name="Tableau1.D1" office:value-type="string">
    <text:p text:style-name="P5">__COL4__</text:p>
</table:table-cell>"""
