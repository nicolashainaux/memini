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
from itertools import zip_longest, chain

from intspan import intspan

from . import shared
from .errors import NoSuchTableError, ColumnsDoNotMatchError, NoSuchRowError
from .errors import TooManyRowsRequiredError, DestinationExistsError
from .errors import NoSuchColumnError
from .parser import parse_pattern
from .sweepstakes import store_sweepstake


# Inspiration from: https://gist.github.com/miku/6522074
class Manager:
    """
    Simple CM for sqlite3 databases. Commits AND closes everything at exit.
    """
    def __init__(self, path):
        self.path = path
        self.conn = None
        self.cursor = None

    def __enter__(self):
        self.conn = sqlite3.connect(self.path)
        self.cursor = self.conn.cursor()
        return self.cursor

    def __exit__(self, exc_class, exc, traceback):
        self.conn.commit()
        self.conn.close()


def list_tables():
    """List all available tables."""
    results = shared.db.execute(
        'SELECT name FROM sqlite_master WHERE type=\'table\';')
    return [_[0] for _ in results.fetchall()]


def table_exists(name):
    """True if a table of this name does exist in the database."""
    return name in list_tables()


def _assert_table_exists(name):
    """Raise an exception if no table of this name exists in the database."""
    if not table_exists(name):
        raise NoSuchTableError(name)
    return True


def _assert_row_exists(table_name, id_):
    """Raise an exception if no such row in the table exists."""
    cmd = f'SELECT EXISTS(SELECT 1 FROM {table_name} WHERE id={id_});'
    row_exists = shared.db.execute(cmd).fetchall()[0][0]
    if not row_exists:
        raise NoSuchRowError(id_, table_name)
    return True


def _exec(table_name, cmd, id_=None):
    """
    Safe execution of the sql command on existing tables: start by checking
    table exists, then possibly the row id_ too, and finally execute the
    command. If table_name is provided as None, then no check is run, the
    command is simply directly executed.
    """
    if table_name is not None:
        _assert_table_exists(table_name)
        if id_ is not None:
            _assert_row_exists(table_name, id_)
    return shared.db.execute(cmd)


def rename_table(name, new_name):
    """Change a table's name."""
    _exec(name, f'ALTER TABLE `{name}` RENAME TO `{new_name}`;')


def update_table(name, id_, content):
    """Change a table's name."""
    col_titles = get_cols(name)
    _assert_row_exists(name, id_)
    if len(content) != len(col_titles):
        raise ColumnsDoNotMatchError(len(col_titles), len(content), name,
                                     col_titles, content)
    pairs = zip(col_titles, content)
    col_values = ', '.join(f'{p[0]}="{p[1]}"' for p in pairs)
    _exec(name, f'UPDATE {name} SET {col_values} WHERE id={id_};')


def copy_table(name1, name2, sort=False):
    """Copy table name1 as name2."""
    if table_exists(name2):
        raise DestinationExistsError(name2)
    orderby = ''
    if sort:
        if sort not in [n + 1 for n in range(len(get_cols(name1)))]:
            raise NoSuchColumnError(sort, name1)
        orderby = f' ORDER BY {get_cols(name1, include_id=True)[sort]}'
    create_table(name2, get_cols(name1))
    titles = ', '.join(get_cols(name1))
    _exec(None, f'INSERT INTO {name2} ({titles}) '
                f'SELECT {titles} FROM {name1}{orderby};')


def _original_name(name):
    """Create a table name that does not already exists in the database."""
    i = 0
    new_name = name + '_0'
    while table_exists(new_name):
        i += 1
        new_name = name + f'_{i}'
    return new_name


def sort_table(name, n):
    """Sort table "name" using column number n"""
    temp_name = _original_name(name)
    copy_table(name, temp_name, sort=n)
    remove_table(name)
    rename_table(temp_name, name)


def get_cols(table_name, include_id=False):
    """List all columns of a given table."""
    cursor = _exec(table_name, f'SELECT * from {table_name};')
    start = 0 if include_id else 1
    return [_[0] for _ in cursor.description][start:-1]


def get_rows_nb(table_name):
    """Return rows' number of a given table."""
    cmd = f'SELECT COUNT(*) FROM {table_name};'
    return tuple(_exec(table_name, cmd))[0][0]


def get_table(name, include_headers=False, sort=False):
    """Return a list of all table's lines."""
    headers = []
    cols = ','.join(get_cols(name, include_id=True))
    content = _exec(name, f'SELECT {cols} FROM {name};').fetchall()
    content = [(str(t[0]), ) + t[1:] for t in content]
    if sort:
        if sort not in [n for n in range(len(content[0]))]:
            raise NoSuchColumnError(sort, name)
        content = sorted(content, key=lambda row: row[sort])
    if include_headers:
        headers = [tuple(get_cols(name, include_id=True))]
    return headers + content


def table_to_text(name, pattern):
    """Return table's content using provided pattern."""
    content = get_table(name)
    content = [c[1:] for c in content]
    col_titles = get_cols(name)
    cols_nb = len(col_titles)
    sep_list, tags = parse_pattern(pattern, sep_list=True)
    tags_nb = len(tags)
    if cols_nb != tags_nb:
        raise ColumnsDoNotMatchError(cols_nb, tags_nb,
                                     name, col_titles, pattern)
    lines = [list(zip_longest(c, sep_list)) for c in content]
    lines = [list(chain(*z))[:-1] for z in lines]
    lines = [''.join(line) for line in lines]
    output = '\n'.join(lines)
    return output


def remove_table(name):
    """Remove table name."""
    _exec(name, f'DROP TABLE {name};')


def create_table(name, col_titles, content=None):
    """Create table name using given col_titles and content."""
    titles = ' TEXT, '.join(col_titles) + ' TEXT, '
    cmd = f'CREATE TABLE {name} (id INTEGER PRIMARY KEY, '\
        f'{titles}timestamp INTEGER)'
    _exec(None, cmd)
    if content is not None:
        insert_rows(name, content, col_titles=col_titles)


def insert_rows(table_name, rows, col_titles=None):
    """Insert rows to the table."""
    if col_titles is None:
        col_titles = get_cols(table_name)
    for row in rows:
        if len(col_titles) != len(row):
            data = [f"'{item}'" for item in row]
            data = ', '.join(data)
            raise ColumnsDoNotMatchError(len(col_titles), len(row),
                                         table_name, col_titles, data)
    titles = ', '.join(list(col_titles) + ['timestamp'])
    qmarks = '?, ' * len(col_titles) + '?'
    cmd = f'INSERT INTO {table_name}({titles}) VALUES({qmarks})'
    content = [item + (0, ) for item in rows]
    shared.db.executemany(cmd, content)


def merge_tables(name1, name2):
    """Insert rows of table name1 table into name2."""
    if len(get_cols(name1)) != len(get_cols(name2)):
        raise ColumnsDoNotMatchError(len(get_cols(name2)),
                                     len(get_cols(name1)), name2,
                                     get_cols(name2), name1)
    titles1 = ', '.join(get_cols(name1))
    titles2 = ', '.join(get_cols(name2))
    _exec(None, f'INSERT INTO {name2} ({titles2}) '
                f'SELECT {titles1} FROM {name1};')


def _reset_table_ids(name):
    """Reset the ids of a table to remove gaps created by rows removals."""
    temp_name = _original_name(name)
    copy_table(name, temp_name)
    remove_table(name)
    rename_table(temp_name, name)


def remove_row(table_name, id_):
    """Remove row matching id_ in the table."""
    cmd = f'DELETE FROM {table_name} WHERE id = {id_};'
    _exec(table_name, cmd, id_=id_)
    _reset_table_ids(table_name)


def _intspan2sqllist(s):
    """Turn an ints' span (given as str) to a SQLite list of values."""
    values = ', '.join([str(n) for n in list(intspan(s))])
    return f'({values})'


def remove_rows(table_name, id_span):
    """Remove rows matching the ids from id_span from the table."""
    _assert_table_exists(table_name)
    for id_ in list(intspan(id_span)):
        _assert_row_exists(table_name, id_)
    values = _intspan2sqllist(id_span)
    cmd = f'DELETE FROM {table_name} WHERE id IN {values};'
    _exec(table_name, cmd)
    _reset_table_ids(table_name)


def _timestamp(table_name, id_):
    """Set timestamp to entry matching id_ in the table."""
    cmd = f"""UPDATE {table_name} SET timestamp = strftime('%Y-%m-%d %H:%M:%f')
WHERE id = {id_};"""
    _exec(table_name, cmd, id_=id_)


def _reset(table_name, n):
    """Reset the n oldest timestamped entries."""
    cmd = f"""UPDATE {table_name} SET timestamp=0
WHERE id IN (SELECT id FROM {table_name} WHERE timestamp != 0
ORDER BY timestamp LIMIT {n});"""
    _exec(table_name, cmd)


def _full_reset(table_name):
    """Reset all entries."""
    _reset(table_name, get_rows_nb(table_name))


def draw_rows(table_name, n, oldest_prevail=False):
    """Return n rows, randomly chosen."""
    rows_nb = get_rows_nb(table_name)
    if n > rows_nb:
        raise TooManyRowsRequiredError(n, rows_nb, table_name)
    timestamps_clause = ''
    if oldest_prevail:  # If timestamps must be taken into account
        cmd = f'SELECT COUNT(*) FROM {table_name} WHERE timestamp=0;'
        free_nb = tuple(_exec(table_name, cmd))[0][0]
        if n > free_nb:
            _reset(table_name, n - free_nb)
        timestamps_clause = 'WHERE timestamp=0 '
    cols_list = ','.join(get_cols(table_name))
    cmd = f'SELECT {cols_list} FROM {table_name} {timestamps_clause}'\
        f'ORDER BY random() LIMIT {n};'
    rows = _exec(table_name, cmd).fetchall()
    store_sweepstake(rows)
    return rows
