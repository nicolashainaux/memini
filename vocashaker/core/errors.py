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


class DestinationExistsError(VocaShakerError):
    """When a destination table or template already exists."""
    def __init__(self, name, kind='table'):
        msg = 'Action cancelled: a {} named "{}" already exists. '\
            'Please rename or remove it before using this name.'\
            .format(kind, name)
        super().__init__(msg)


class NotFoundError(VocaShakerError):
    """When obviously something is missing."""
    def __init__(self, msg):
        super().__init__(msg)


class EmptyFileError(VocaShakerError):
    """When an empty file has been given to parse, for instance."""
    def __init__(self, msg):
        super().__init__(msg)


class CommandError(VocaShakerError):
    """When the user mistyped a command."""
    def __init__(self, msg):
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


class SchemeSyntaxError(VocaShakerError):
    """When the user provides a scheme that contains unexpected chars."""
    def __init__(self, scheme):
        msg = 'Incorrect scheme: "{}". A scheme should contain underscore '\
            'and star chars ("_" and "*"), plus possibly one digit as last '\
            'char.'.format(scheme)
        super().__init__(msg)


class SchemeLogicalError(VocaShakerError):
    """When the user provides a scheme with too few or too many blanks."""
    def __init__(self, scheme, blanks_nb, cols_nb, blanks_required):
        start = 'Incorrect scheme: "{}". '.format(scheme)
        if blanks_nb == 0:
            end = 'A scheme should contain at least one possible blank '\
                'column ("_").'
        elif blanks_required >= cols_nb:
            end = 'It shows {} columns, hence {} of them at most can be '\
                'blank, not more ({}).'.format(str(cols_nb), str(cols_nb - 1),
                                               str(blanks_required))
        elif blanks_required > blanks_nb:
            end = 'It shows less possible blank columns ({} "_") '\
                'than it requires ({}).'.format(str(blanks_nb),
                                                str(blanks_required))
        msg = start + end
        super().__init__(msg)


class SchemeColumnsMismatchError(VocaShakerError):
    """
    When the user provides a scheme that does not match the number of
    columns in the table.
    """
    def __init__(self, scheme, cols_nb):
        msg = 'The provided scheme ({}) does not have the same number of '\
            'columns as the table ({}).'.format(scheme, str(cols_nb))
        super().__init__(msg)
