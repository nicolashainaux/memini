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

# from vocashaker.core.settings import TABLE_WIDTH_CM, TABLE_WIDTH_PX


def _colwidth(n):
    """
    Return the columns width of a table of n columns and fixed width.

    Result is a tuple containing the width in cm and pixels.
    """


def _colid(n):
    """Return the column id for column number n. Simply the matching letter."""


def _more_row_cells(row_nb, table_nb, col_nb):
    """Return the portion of content.xml that defines the table rows."""


def _prebuild(n):
    """Return a model to build content.xml, matching n columns."""


def _build(table_name):
    """Return content.xml matching table_name's content."""


def create(table_name):
    """Create the template file."""
