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

import shutil

from .prefs import DEFAULT_Q_NB
from . import database, template, terminal, parser
from .errors import NoSuchTableError, DestinationExistsError, NotFoundError
from .errors import CommandError


def add(name, file_name, pattern):
    """
    Parse file using pattern and create a new table filled with the result.
    Create the associated default template.
    Before doing so, check if the name is already used. If yes, ask if the
    lines should be appended to the existing table or not (cancel).
    """
    rows = parser.parse_file(file_name, pattern)
    _, titles = parser.parse_pattern(pattern)
    database.create_table(name, titles, rows)
    template.create(name)


def delete(name):
    """
    Delete the table and/or the associated default template matching name.
    Ask confirmation before.
    """
    if database.table_exists(name) or template.exists(name):
        if database.table_exists(name):
            do_delete = terminal.ask_yes_no('Delete table "{}"?'.format(name))
            if do_delete:
                database.remove_table(name)
        if template.exists(name):
            do_delete = terminal.ask_yes_no('Delete template "{}"?'
                                            .format(name))
            if do_delete:
                template.remove(name)
    else:
        raise NotFoundError('No table nor template named "{}" can be found '
                            'to be deleted.'.format(name))


def remove(name, id_span):
    """
    Remove the rows identified by the given id_span from the table identified
    by its name.
    """
    database.remove_rows(name, id_span)


# def merge(name1, name2, name3=None):
#     """
#     If name3 is None, then merge contents of tables name1 and name2
# into name2.
#     Ask before doing so.
#     If name3 is not None, then the merged content goes to a newly created
# table
#     named name3 (the matching default template will then be created too).
#     """
#     pass


def list_(kind):
    """Print the listing of all known tables' or templates' names."""
    if kind == 'tables':
        print('\n'.join(database.list_tables()))
    elif kind == 'templates':
        print('\n'.join(template.list_()))
    else:
        raise CommandError('I can list "tables" or "templates". I don\'t '
                           'know what "{}" might mean.'.format(kind))


def show(name):
    """Print the content of the table matching name."""
    if not database.table_exists(name):
        raise NoSuchTableError(name)
    print(terminal.tabulate(database.get_table(name, include_headers=True)))


def rename(name1, name2):
    """
    Rename table name1 as name2. Also rename the associated default template.
    """
    if not database.table_exists(name1):
        raise NoSuchTableError(name1)
    if not template.exists(name1):
        template.create(name1)
    if database.table_exists(name2):
        raise DestinationExistsError(name2, kind='table')
    elif template.exists(name2):
        raise DestinationExistsError(name2, kind='template')
    shutil.move(template.path(name1), template.path(name2))
    database.rename_table(name1, name2)


def generate(name, nb=DEFAULT_Q_NB):
    """
    Create a new document using default template and drawing data from the
    table matching name.
    """
    pass
