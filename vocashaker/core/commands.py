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

from .prefs import DEFAULT_Q_NB
from . import database


def add(name, file, pattern):
    """
    Parse file using pattern and create a new table filled with the result.
    Check if the name is already used. If yes, ask if the lines should be
    appended to the existing table or not (cancel).
    """
    pass
    # template.create(name)


def delete(name):
    """Delete the table matching "name". Ask confirmation before."""
    pass


def remove(name, id_span):
    """Remove the rows identified by the given id_span from the table."""
    pass
    # template.remove(name)


def merge(name1, name2, name3=None):
    """
    If name3 is None, then merge contents of tables name1 and name2 into name2.
    Ask before doing so.
    If name3 is not None, then the merged content goes to a newly created table
    named name3.
    """
    pass


def list_():
    """Print the listing of all tables' names currently available."""
    print('\n'.join(database.list_tables()))


def show(name):
    """Print the content of the table matching name."""
    pass


def rename(name1, name2):
    """Rename table name1 as name2."""
    pass


def generate(name, nb=DEFAULT_Q_NB):
    """
    Create a new document using default template and drawing data from the
    table matching name.
    """
    pass
