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


class VocaShakerError(Exception):
    """Basic exception for errors raised by VocaShaker."""
    def __init__(self, msg):
        super().__init__(msg)


class MissingSeparatorError(VocaShakerError):
    """When a pattern is provided with missing separator."""
    def __init__(self, pattern, missing_tag_position):
        msg = 'Missing separator in pattern:\n{}\n{}'\
            .format(pattern, ' ' * (missing_tag_position + 1) + '^')
        super().__init__(msg)


class LineDoesNotMatchError(VocaShakerError):
    """When a line does not match the provided pattern."""
    def __init__(self, line, pattern):
        msg = 'This line: {}\ndoes not match provided pattern: {}'\
            .format(line, pattern)
        super().__init__(msg)


class NoSuchTableError(VocaShakerError):
    """When the provided name does not match any table."""
    def __init__(self, name):
        msg = 'Cannot find a table named "{}"'.format(name)
        super().__init__(msg)


class NoSuchRowError(VocaShakerError):
    """When the provided name does not match any row."""
    def __init__(self, id_, name):
        msg = 'Cannot find a row number {} in "{}"'.format(id_, name)
        super().__init__(msg)


class ColumnsDoNotMatchError(VocaShakerError):
    """When the columns number does not match."""
    def __init__(self, expected, found, table_name, col_titles, data):
        col_titles = ['"{}"'.format(c) for c in col_titles]
        col_list = '{} and {}'.format(', '.join(col_titles[:-1]),
                                      col_titles[-1])
        msg = '"{}" requires {} columns, but "{}" has {} columns ({}).'\
            .format(data, found, table_name, expected, col_list)
        super().__init__(msg)


class TooManyRowsRequiredError(VocaShakerError):
    """When the user requires more rows than a table does contain."""
    def __init__(self, n_required, n_rows, table_name):
        msg = '{} rows are required from "{}", but it only contains {} rows.'\
            .format(n_required, table_name, n_rows)
        super().__init__(msg)
