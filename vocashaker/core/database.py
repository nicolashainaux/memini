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

from . import shared
from .errors import NoSuchTableError, ColumnsDoNotMatchError
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
    """
    List all available tables.
    """
    results = shared.db.execute(
        'SELECT name FROM sqlite_master WHERE type=\'table\';')
    return [_[0] for _ in results.fetchall()]


def table_exists(name):
    """True if a table of this name does exist in the database."""
    return name in list_tables()


def assert_table_exists(name):
    """Raise an exception if no table of this name exists in the database."""
    if not table_exists(name):
        raise NoSuchTableError(name)
    return True


def rename_table(name, new_name):
    assert_table_exists(name)
    shared.db.execute('ALTER TABLE `{}` RENAME TO `{}`;'
                      .format(name, new_name))


def get_cols(name, include_id=False):
    """
    List all columns of a given table.
    """
    assert_table_exists(name)
    cursor = shared.db.execute('SELECT * from {};'.format(name))
    start = 0 if include_id else 1
    return [_[0] for _ in cursor.description][start:-1]


def get_table(name):
    assert_table_exists(name)
    cols = ','.join(get_cols(name, include_id=True))
    content = shared.db.execute(
        'SELECT {} FROM {};'.format(cols, name)).fetchall()
    content = [(str(t[0]), ) + t[1:] for t in content]
    return content


def table_to_text(name, pattern):
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
    pass


def create_table(name, col_titles, content):
    pass


def add_row(name, row):
    pass


def remove_row(name, id):
    pass


def draw_rows(name, nb):
    pass
