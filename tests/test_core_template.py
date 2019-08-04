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

import sqlite3

import pytest
from decimal import Decimal

from vocashaker.core import shared
from vocashaker.core.env import TEST_DB_PATH
from vocashaker.core.env import TEST_PREBUILT_CONTENTXML_2COLS_PATH
from vocashaker.core.env import TEST_PREBUILT_CONTENTXML_3COLS_PATH
from vocashaker.core.env import TEST_PREBUILT_CONTENTXML_4COLS_PATH
from vocashaker.core.env import TEST_BUILT_TABLE1_CONTENTXML_PATH
from vocashaker.core.template import _colwidth, _colid, _more_row_cells
from vocashaker.core.template import _prebuild, _build, create


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


def test_colwidth():
    assert _colwidth(4) == (Decimal('4.9'), 16384)


def test_colid():
    assert _colid(4) == 'D'


def test_more_row0_cells():
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


def test_more_row1_cells():
    assert _more_row_cells(1, 1, 2) == """
<table:table-cell table:style-name="Tableau1.B2" office:value-type="string">"""\
+ """<text:p text:style-name="P1"/></table:table-cell>"""
    assert _more_row_cells(1, 1, 3) == """
<table:table-cell table:style-name="Tableau1.A2" office:value-type="string">"""\
+ """<text:p text:style-name="P1"/></table:table-cell>""" + """
<table:table-cell table:style-name="Tableau1.C2" office:value-type="string">"""\
+ """<text:p text:style-name="P1"/></table:table-cell>"""
    assert _more_row_cells(1, 1, 4) == """
<table:table-cell table:style-name="Tableau1.A2" office:value-type="string">"""\
+ """<text:p text:style-name="P1"/></table:table-cell>""" + """
<table:table-cell table:style-name="Tableau1.A2" office:value-type="string">"""\
+ """<text:p text:style-name="P1"/></table:table-cell>""" + """
<table:table-cell table:style-name="Tableau1.D2" office:value-type="string">"""\
+ """<text:p text:style-name="P1"/></table:table-cell>"""


def test_more_row2_cells():
    assert _more_row_cells(2, 1, 2) == """
<table:table-cell table:style-name="Tableau1.B2" office:value-type="string">"""\
+ '    <text:p text:style-name="P2">'\
        + '  <text:a xlink:type="simple" xlink:href="relatorio://row.col2" '\
        + 'text:style-name="Internet_20_link" '\
        + """text:visited-style-name="Visited_20_Internet_20_Link">
            <text:span text:style-name="T1">row.col2</text:span>
        </text:a>
    </text:p>
</table:table-cell>"""
    assert _more_row_cells(2, 1, 3) == """
<table:table-cell table:style-name="Tableau1.A2" office:value-type="string">"""\
+ '    <text:p text:style-name="P2">'\
        + '  <text:a xlink:type="simple" xlink:href="relatorio://row.col2" '\
        + 'text:style-name="Internet_20_link" '\
        + """text:visited-style-name="Visited_20_Internet_20_Link">
            <text:span text:style-name="T1">row.col2</text:span>
        </text:a>
    </text:p>
</table:table-cell>
<table:table-cell table:style-name="Tableau1.C2" office:value-type="string">"""\
+ '    <text:p text:style-name="P2">'\
        + '  <text:a xlink:type="simple" xlink:href="relatorio://row.col3" '\
        + 'text:style-name="Internet_20_link" '\
        + """text:visited-style-name="Visited_20_Internet_20_Link">
            <text:span text:style-name="T1">row.col3</text:span>
        </text:a>
    </text:p>
</table:table-cell>"""
    assert _more_row_cells(2, 1, 4) == """
<table:table-cell table:style-name="Tableau1.A2" office:value-type="string">"""\
+ '    <text:p text:style-name="P2">'\
        + '  <text:a xlink:type="simple" xlink:href="relatorio://row.col2" '\
        + 'text:style-name="Internet_20_link" '\
        + """text:visited-style-name="Visited_20_Internet_20_Link">
            <text:span text:style-name="T1">row.col2</text:span>
        </text:a>
    </text:p>
</table:table-cell>
<table:table-cell table:style-name="Tableau1.A2" office:value-type="string">"""\
+ '    <text:p text:style-name="P2">'\
        + '  <text:a xlink:type="simple" xlink:href="relatorio://row.col3" '\
        + 'text:style-name="Internet_20_link" '\
        + """text:visited-style-name="Visited_20_Internet_20_Link">
            <text:span text:style-name="T1">row.col3</text:span>
        </text:a>
    </text:p>
</table:table-cell>
<table:table-cell table:style-name="Tableau1.D2" office:value-type="string">"""\
+ '    <text:p text:style-name="P2">'\
        + '  <text:a xlink:type="simple" xlink:href="relatorio://row.col4" '\
        + 'text:style-name="Internet_20_link" '\
        + """text:visited-style-name="Visited_20_Internet_20_Link">
            <text:span text:style-name="T1">row.col4</text:span>
        </text:a>
    </text:p>
</table:table-cell>"""


def test_more_row3_cells():
    assert _more_row_cells(3, 1, 2) == """
<table:table-cell table:style-name="Tableau1.B2" """\
+ """office:value-type="string"><text:p text:style-name="P1"/>"""\
        + """</table:table-cell>"""
    assert _more_row_cells(3, 1, 3) == """
<table:table-cell table:style-name="Tableau1.A2" """\
+ """office:value-type="string"><text:p text:style-name="P1"/>"""\
        + """</table:table-cell>
<table:table-cell table:style-name="Tableau1.C2" """\
+ """office:value-type="string"><text:p text:style-name="P1"/>"""\
        + """</table:table-cell>"""
    assert _more_row_cells(3, 1, 4) == """
<table:table-cell table:style-name="Tableau1.A2" """\
+ """office:value-type="string"><text:p text:style-name="P1"/>"""\
        + """</table:table-cell>
<table:table-cell table:style-name="Tableau1.A2" """\
+ """office:value-type="string"><text:p text:style-name="P1"/>"""\
        + """</table:table-cell>
<table:table-cell table:style-name="Tableau1.D2" """\
+ """office:value-type="string"><text:p text:style-name="P1"/>"""\
        + """</table:table-cell>"""


def test_prebuild_2cols():
    with open(TEST_PREBUILT_CONTENTXML_2COLS_PATH, 'r') as f:
        expected = f.read()
    assert _prebuild(2) == expected


def test_prebuild_3cols():
    with open(TEST_PREBUILT_CONTENTXML_3COLS_PATH, 'r') as f:
        expected = f.read()
    assert _prebuild(3) == expected


def test_prebuild_4cols():
    with open(TEST_PREBUILT_CONTENTXML_4COLS_PATH, 'r') as f:
        expected = f.read()
    assert _prebuild(4) == expected


def test_build(testdb):
    with open(TEST_BUILT_TABLE1_CONTENTXML_PATH, 'r') as f:
        expected = f.read()
    assert _build('table1') == expected


def test_create(testdb):
    create('table1')
