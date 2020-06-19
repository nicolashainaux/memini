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
from .errors import TooManyRowsRequiredError
from .parser import parse_pattern


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
    cmd = 'SELECT EXISTS(SELECT 1 FROM {} WHERE id={});'\
        .format(table_name, id_)
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
    _exec(name, 'ALTER TABLE `{}` RENAME TO `{}`;'.format(name, new_name))


def get_cols(table_name, include_id=False):
    """List all columns of a given table."""
    cursor = _exec(table_name, 'SELECT * from {};'.format(table_name))
    start = 0 if include_id else 1
    return [_[0] for _ in cursor.description][start:-1]


def get_rows_nb(table_name):
    """Return rows' number of a given table."""
    cmd = 'SELECT COUNT(*) FROM {};'.format(table_name)
    return tuple(_exec(table_name, cmd))[0][0]


def get_table(name, include_headers=False):
    """Return a list of all table's lines."""
    headers = []
    cols = ','.join(get_cols(name, include_id=True))
    content = _exec(name, 'SELECT {} FROM {};'.format(cols, name)).fetchall()
    content = [(str(t[0]), ) + t[1:] for t in content]
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
    _exec(name, 'DROP TABLE {};'.format(name))


def create_table(name, col_titles, content):
    """Create table name using given col_titles and content."""
    titles = ' TEXT, '.join(col_titles) + ' TEXT, '
    cmd = 'CREATE TABLE {} (id INTEGER PRIMARY KEY, {}timestamp INTEGER)'\
        .format(name, titles)
    _exec(None, cmd)
    titles = ', '.join(col_titles) + ', timestamp'
    qmarks = '?, ' * len(col_titles) + '?'
    cmd = 'INSERT INTO {}({}) VALUES({})'.format(name, titles, qmarks)
    content = [item + (0, ) for item in content]
    shared.db.executemany(cmd, content)


def add_row(table_name, row):
    """Add row to the table."""
    cols = get_cols(table_name)
    if len(cols) != len(row):
        data = ["'{}'".format(item) for item in row]
        data = ', '.join(data)
        raise ColumnsDoNotMatchError(len(cols), len(row),
                                     table_name, cols, data)
    titles = ', '.join(cols + ['timestamp'])
    row = ['"{}"'.format(item) for item in row]
    values = ', '.join(row + ['0'])
    cmd = 'INSERT INTO {}({}) VALUES({})'.format(table_name, titles, values)
    _exec(table_name, cmd)


def remove_row(table_name, id_):
    """Remove row matching id_ in the table."""
    cmd = 'DELETE FROM {} WHERE id = {};'.format(table_name, id_)
    _exec(table_name, cmd, id_=id_)


def _intspan2sqllist(s):
    """Turn an ints' span (given as str) to a SQLite list of values."""
    values = ', '.join([str(n) for n in list(intspan(s))])
    return f'({values})'


def _timestamp(table_name, id_):
    """Set timestamp to entry matching id_ in the table."""
    cmd = """UPDATE {} SET timestamp = strftime('%Y-%m-%d %H:%M:%f')
WHERE id = {};""".format(table_name, id_)
    _exec(table_name, cmd, id_=id_)


def _reset(table_name, n):
    """Reset the n oldest timestamped entries."""
    cmd = """UPDATE {table_name} SET timestamp=0
WHERE id IN (SELECT id FROM {table_name} WHERE timestamp != 0
ORDER BY timestamp LIMIT {n});""".format(table_name=table_name, n=n)
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
        cmd = 'SELECT COUNT(*) FROM {} WHERE timestamp=0;'.format(table_name)
        free_nb = tuple(_exec(table_name, cmd))[0][0]
        if n > free_nb:
            _reset(table_name, n - free_nb)
        timestamps_clause = 'WHERE timestamp=0 '
    cols_list = ','.join(get_cols(table_name))
    cmd = 'SELECT {} FROM {} {}ORDER BY random() LIMIT {};'\
        .format(cols_list, table_name, timestamps_clause, n)
    return _exec(table_name, cmd).fetchall()
