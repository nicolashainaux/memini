# -*- coding: utf-8 -*-

# Memini is a simple project that creates vocabulary grids to train.
# Copyright 2019 Nicolas Hainaux <nh.techn@gmail.com>

# This file is part of Memini.

# Memini is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# any later version.

# Memini is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Memini; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import sys
import shutil

import blessed

from .prefs import DEFAULT_Q_NB
from . import database, template, terminal, parser, document, sweepstakes
from .errors import NoSuchTableError, DestinationExistsError, NotFoundError
from .errors import CommandError, ColumnsDoNotMatchError, MergeError


def _print_lines_not_matching_pattern(errors, pattern, decorate=True):
    term = blessed.Terminal()
    msg_start = ''
    msg_prepend_lines = ''
    msg_end = ''
    if decorate:
        msg_start = term.darkorange(f'WARNING: following lines do not match '
                                    f'the pattern "{pattern}" and have been '
                                    f'ignored:\n')
        msg_prepend_lines = term.darkorange('✘ ')
        msg_end = term.darkorange('End of ignored lines list\n')
    msg_content = '\n'.join(msg_prepend_lines + line for line in errors)
    message = f'{msg_start}{msg_content}\n{msg_end}'
    sys.stderr.write(message)


def parse(filename, pattern, errors_only=False):
    """
    Parse file using provided pattern and output the result. Do not store
    anything.
    """
    _, titles = parser.parse_pattern(pattern)
    parsed, errors = parser.parse_file(filename, pattern)
    if not errors_only:
        print(terminal.tabulate([titles] + parsed))
    if errors:
        _print_lines_not_matching_pattern(errors, pattern,
                                          decorate=not errors_only)
    elif errors_only:
        term = blessed.Terminal()
        sys.stderr.write(term.chartreuse3('No parsing errors ☺\n'))


def create(name, file_name, pattern):
    """
    Create a new table filled with the result of parsing file_name using
    provided pattern. Create the associated default template.
    Abort if the name is already used.
    """
    if database.table_exists(name):
        raise DestinationExistsError(name, kind='table')
    elif template.exists(name):
        raise DestinationExistsError(name, kind='template')
    rows, errors = parser.parse_file(file_name, pattern)
    _, titles = parser.parse_pattern(pattern)
    database.create_table(name, titles, rows)
    template.create(name)
    if errors:
        _print_lines_not_matching_pattern(errors, pattern)


def add(name, file_name, pattern):
    """
    Add the result of parsing file_name using provided pattern to existing
    table named "name".
    """
    if not database.table_exists(name):
        raise NoSuchTableError(name)
    rows, errors = parser.parse_file(file_name, pattern)
    _, titles = parser.parse_pattern(pattern)
    table_col_titles = database.get_cols(name)
    cols_nb = len(table_col_titles)
    if len(titles) != cols_nb:
        raise ColumnsDoNotMatchError(cols_nb, len(titles), name,
                                     table_col_titles, pattern)
    database.insert_rows(name, rows)
    if errors:
        _print_lines_not_matching_pattern(errors, pattern)


def delete(name):
    """
    Delete the table and/or the associated default template matching name.
    Ask confirmation before.
    """
    if database.table_exists(name) or template.exists(name):
        if database.table_exists(name):
            do_delete = terminal.ask_yes_no(f'Delete table "{name}"?')
            if do_delete:
                database.remove_table(name)
        if template.exists(name):
            do_delete = terminal.ask_yes_no(f'Delete template "{name}"?')
            if do_delete:
                template.remove(name)
    else:
        raise NotFoundError(f'No table nor template named "{name}" can be '
                            f'found to be deleted.')


def remove(name, id_span):
    """
    Remove the rows identified by the given id_span from the table identified
    by its name.
    """
    database.remove_rows(name, id_span)


def list_(kind):
    """Print the listing of all known tables' or templates' names."""
    if kind == 'tables':
        print('\n'.join(database.list_tables()))
    elif kind == 'templates':
        print('\n'.join(template.list_()))
    elif kind == 'sweepstakes':
        print('\n'.join(sweepstakes.list_sweepstakes()))
    else:
        raise CommandError(f'Sorry, I can only list "tables", "templates" or '
                           f'"sweepstakes". Please use one of these three '
                           f'keywords. I will not try to list "{kind}".')


def show(name, sort=False):
    """Print the content of the table matching name."""
    print(terminal.tabulate(database.get_table(name, include_headers=True,
                                               sort=sort)))


def sort(name, col_nb=1):
    """Sort the content of the table matching name."""
    database.sort_table(name, col_nb)


def update(name, rowstr):
    """Update a row."""
    cells = rowstr.split('|')
    id_ = int(cells[0])
    content = cells[1:]
    database.update_table(name, id_, content)


def dump(sw_id):
    """Print content of sweepstake sw_id to standard output."""
    print('\n'.join(str(row) for row in sweepstakes.load_sweepstake(sw_id)))


def _check_moveable(name1, name2):
    """
    Check table name1 does exist, but not name2. Check no template name2
    already exists. Create template name1 if it does not exist yet.
    """
    if not database.table_exists(name1):
        raise NoSuchTableError(name1)
    if not template.exists(name1):
        template.create(name1)
    if database.table_exists(name2):
        raise DestinationExistsError(name2, kind='table')
    elif template.exists(name2):
        raise DestinationExistsError(name2, kind='template')


def rename(name1, name2):
    """
    Rename table name1 as name2. Also rename the associated default template.
    """
    _check_moveable(name1, name2)
    shutil.move(template.path(name1), template.path(name2))
    database.rename_table(name1, name2)


def duplicate(name1, name2):
    """
    Rename table name1 as name2. Duplicate the associated default template.
    """
    _check_moveable(name1, name2)
    shutil.copy(template.path(name1), template.path(name2))
    database.copy_table(name1, name2)


def merge(src, dest):
    """
    Merge tables from src into dest.

    If it does not exist, then dest is created and the matching default
    template too.
    """
    # Check sources first
    if not src:
        raise MergeError('At least one table must be provided as source.')
    nonexisting_tables = []
    for table in src:
        try:
            database._assert_table_exists(table)
        except NoSuchTableError:
            nonexisting_tables.append(table)
    if nonexisting_tables:
        raise MergeError(f"One or more tables cannot be found: "
                         f"{', '.join(nonexisting_tables)}")
    src_cols_nb = [len(database.get_cols(table)) for table in src]
    if not all(n == src_cols_nb[0] for n in src_cols_nb):
        raise MergeError(f'All tables used as sources must have the same '
                         f'number of columns. Found {src_cols_nb} instead.')
    else:
        src_cols_nb = src_cols_nb[0]

    # Now check dest
    do_create_dest_template = False
    if database.table_exists(dest):
        dest_cols_nb = len(database.get_cols(dest))
        if src_cols_nb != dest_cols_nb:
            raise MergeError(f'Number of columns mismatch: destination table '
                             f'{dest} has {dest_cols_nb} columns, while '
                             f'source table(s) have {src_cols_nb} columns.')
        if not template.exists(dest):
            do_create_dest_template = True
    else:
        if template.exists(dest):
            raise MergeError(f'Action cancelled: a template matching "{dest}" '
                             f'already exists, but not the matching table. '
                             f'Please rename or remove it before using this '
                             f'name.')
        database.create_table(dest, database.get_cols(src[0]))
        do_create_dest_template = True

    if do_create_dest_template:
        template.create(dest)
    for table in src:
        database.merge_tables(table, dest)


def edit(name):
    """
    Edit template named "name".
    """
    if not template.exists(name):
        raise NotFoundError(f'Cannot find any template "{name}".')
    template.edit(name)


def generate(name, nb=DEFAULT_Q_NB, scheme=None, output=None, force=False,
             tpl=None, edit=True, use_previous=False):
    """
    Create a new document using default template and drawing data from the
    table matching name.
    """
    document.generate(name, nb=nb, scheme=scheme, output=output, force=force,
                      tpl=tpl, edit_after=edit, use_previous=use_previous)
