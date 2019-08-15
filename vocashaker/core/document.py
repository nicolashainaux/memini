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

import re

from vocashaker.core.prefs import BLANK_CHAR, FILLED_CHAR
from vocashaker.core.errors import SchemeSyntaxError, SchemeLogicalError


def _default_scheme(n):
    """
    Any column may be blank, only one column won't be blank at each row.
    See _parse_scheme() for scheme description and purpose.
    n is the number of columns.
    For example, for n=2, default will be __1
    For n=3: ___2
    For n=4: ____3
    """
    return '_' * n + str(n - 1)


def _parse_scheme(scheme):
    """
    Check the provided scheme is correct and return the matching distribution.

    The scheme is an information the user provides to tell how many blanks
    there will be in the table, and which columns may be blank.
    Syntax is: one underscore (_) for a column that may be blank. A star (*)
    for a column that will never be blank. And a number to tell how many blanks
    per row there should be.

    Scheme example: "__*1" to tell there will be one blank in one of the two
    first columns, each row. This method should return ([0, 1], 1)
    """
    original_scheme = scheme
    blanks_nb = scheme.count(BLANK_CHAR)
    filled_nb = scheme.count(FILLED_CHAR)
    if scheme[-1].isdigit():
        scheme, blanks_required = scheme[:-1], int(scheme[-1])
    else:
        blanks_required = min(len(scheme) - 1, blanks_nb)
    cols_nb = len(scheme)
    if blanks_nb + filled_nb != cols_nb:
        raise SchemeSyntaxError(scheme)
    elif (blanks_nb == 0 or blanks_required >= cols_nb
          or blanks_required > blanks_nb):
        raise SchemeLogicalError(original_scheme, blanks_nb, cols_nb,
                                 blanks_required)
    return ([m.start() for m in re.finditer(BLANK_CHAR, scheme)],
            blanks_required)
