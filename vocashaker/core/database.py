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

from . import shared
from .errors import NoSuchTableError


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


def rename_table(name, new_name):
    if not table_exists(name):
        raise NoSuchTableError(name)
    shared.db.execute('ALTER TABLE `{}` RENAME TO `{}`;'
                      .format(name, new_name))


def get_table(name):
    pass


def table_to_text(name, pattern):
    pass


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
