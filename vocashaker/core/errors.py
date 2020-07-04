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

import os

from .env import PROG_NAME


class VocaShakerError(Exception):
    """Basic exception for errors raised by VocaShaker."""
    def __init__(self, msg):
        super().__init__(msg)


class MissingSeparatorError(VocaShakerError):
    """When a pattern is provided with missing separator."""
    def __init__(self, pattern, missing_tag_position):
        arrow = ' ' * (missing_tag_position + 1) + '^'
        msg = f'Missing separator in pattern:\n{pattern}\n{arrow}'
        super().__init__(msg)


class LineDoesNotMatchError(VocaShakerError):
    """When a line does not match the provided pattern."""
    def __init__(self, line, pattern):
        msg = f'This line: {line}\ndoes not match provided pattern: {pattern}'
        super().__init__(msg)


class DestinationExistsError(VocaShakerError):
    """When a destination table or template already exists."""
    def __init__(self, name, kind='table'):
        msg = f'Action cancelled: a {kind} named "{name}" already exists. '\
            'Please rename or remove it before using this name.'
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
        msg = f'Cannot find a table named "{name}"'
        super().__init__(msg)


class NoSuchRowError(VocaShakerError):
    """When the provided id_ does not match any row."""
    def __init__(self, id_, name):
        msg = f'Cannot find a row number {id_} in "{name}"'
        super().__init__(msg)


class NoSuchColumnError(VocaShakerError):
    """When the provided number does not match any row."""
    def __init__(self, n, name):
        msg = f'Cannot find a column number {n} in "{name}"'
        super().__init__(msg)


class NoSuchSweepstakeError(VocaShakerError):
    """When the provided id does not match any sweepstake."""
    def __init__(self, sw_id):
        msg = f'Cannot find a sweepstake starting with "{sw_id}"'
        super().__init__(msg)


class ColumnsDoNotMatchError(VocaShakerError):
    """When the columns number does not match."""
    def __init__(self, expected, found, table_name, col_titles, data):
        col_titles = [f'"{c}"' for c in col_titles]
        comma_sep_cols_but_the_last = ', '.join(col_titles[:-1])
        the_last = col_titles[-1]
        col_list = f'{comma_sep_cols_but_the_last} and {the_last}'
        msg = f'"{data}" requires {found} columns, but "{table_name}" '\
            f'has {expected} columns ({col_list}).'
        super().__init__(msg)


class TooManyRowsRequiredError(VocaShakerError):
    """When the user requires more rows than a table does contain."""
    def __init__(self, n_required, n_rows, table_name):
        msg = f'{n_required} rows are required from "{table_name}", '\
            f'but it only contains {n_rows} rows.'
        super().__init__(msg)


class SchemeSyntaxError(VocaShakerError):
    """When the user provides a scheme that contains unexpected chars."""
    def __init__(self, scheme):
        msg = f'Incorrect scheme: "{scheme}". A scheme should contain '\
            f'underscore and star chars ("_" and "*"), plus possibly one '\
            f'digit as last char.'
        super().__init__(msg)


class SchemeLogicalError(VocaShakerError):
    """When the user provides a scheme with too few or too many blanks."""
    def __init__(self, scheme, blanks_nb, cols_nb, blanks_required):
        start = f'Incorrect scheme: "{scheme}". '
        if blanks_nb == 0:
            end = 'A scheme should contain at least one possible blank '\
                'column ("_").'
        elif blanks_required >= cols_nb:
            end = f'It shows {cols_nb} columns, hence {cols_nb - 1} of them '\
                f'at most can be blank, not more ({blanks_required}).'
        elif blanks_required > blanks_nb:
            end = f'It shows less possible blank columns ({blanks_nb} "_") '\
                f'than it requires ({blanks_required}).'
        msg = start + end
        super().__init__(msg)


class SchemeColumnsMismatchError(VocaShakerError):
    """
    When the user provides a scheme that does not match the number of
    columns in the table.
    """
    def __init__(self, scheme, cols_nb):
        msg = f'The provided scheme ({scheme}) does not have the same number '\
            f'of columns as the table ({cols_nb}).'
        super().__init__(msg)


class CommandCancelledError(VocaShakerError):
    """When the user cancels a command."""
    def __init__(self, cmd):
        msg = f'Command {cmd} has been cancelled.'
        super().__init__(msg)


class NotATemplateError(VocaShakerError):
    """
    When a provided file is not recognized as a template created by VocaShaker.
    """
    def __init__(self, filename):
        msg = f'This file: {os.path.basename(filename)} does not look like a '\
            f'{PROG_NAME} template.'
        super().__init__(msg)
