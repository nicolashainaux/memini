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

import click
import blessed

from vocashaker.core.prefs import DEFAULT_Q_NB
from vocashaker.core.env import USER_DB_PATH
from vocashaker.core.errors import CommandError, EmptyFileError, NotFoundError
from vocashaker.core.errors import NoSuchTableError, NoSuchRowError
from vocashaker.core.errors import DestinationExistsError
from vocashaker.core.errors import ColumnsDoNotMatchError
from vocashaker.core import shared
from vocashaker.core import database
from vocashaker.core import commands


shared.init()

__all__ = ['run']


def echo_warning(s):
    term = blessed.Terminal()
    click.echo(term.darkorange('Warning: ') + str(s))


def echo_error(s):
    term = blessed.Terminal()
    click.echo(term.color_rgb(197, 0, 11) + 'Error: ' + term.normal + str(s))


@click.group()
def run():
    pass


@run.command('list')
@click.argument('what')
def list_(what):
    """
    List known tables or templates.

    List known tables or templates. What to list exactly is set by argument
    WHAT (that may be "tables" or "templates").
    """
    with database.Manager(USER_DB_PATH) as db:
        shared.db = db
        try:
            commands.list_(what)
        except CommandError as e:
            echo_error(str(e))


@run.command('parse')
@click.option('--errors-only', is_flag=True, default=False, show_default=True,
              help='if true, only the lines that do not match the pattern '
              'will be shown')
@click.argument('filename', type=click.Path(exists=True))
@click.argument('pattern')
def parse(filename, pattern, errors_only):
    """
    Parse a file a show result in console.

    Parse the file FILENAME using the provided PATTERN. The result will be
    displayed in the console. No new table will be created.

    It will highlight possible parsing errors. You can get a clean output of
    the lines producing errors by setting option --errors-only to true.
    """
    with database.Manager(USER_DB_PATH) as db:
        shared.db = db
        try:
            commands.parse(filename, pattern, errors_only)
        except EmptyFileError as e:
            echo_warning(str(e))


@run.command('delete')
@click.argument('name')
def delete(name):
    """
    Delete a table.

    Delete the table NAME. The matching default template will be deleted too.
    """
    with database.Manager(USER_DB_PATH) as db:
        shared.db = db
        try:
            commands.delete(name)
        except NotFoundError as e:
            echo_error(str(e))


@run.command('remove')
@click.argument('name')
@click.argument('span')
def remove(name, span):
    """
    Remove rows from a table.

    Remove rows from the table NAME. SPAN is the list of lines' numbers to be
    removed. It can be provided as a single int or as an int range, like
    "2-6,9" that would remove rows 2, 3, 4, 5, 6 and 9.
    """
    with database.Manager(USER_DB_PATH) as db:
        shared.db = db
        try:
            commands.remove(name, span)
        except (NoSuchTableError, NoSuchRowError) as e:
            echo_error(str(e))


@run.command('create')
@click.argument('name')
@click.argument('filename', type=click.Path())
@click.argument('pattern')
def create(name, filename, pattern):
    """
    Create a new table.

    Create a table NAME. The data will be read from file FILENAME
    and parsed according to the provided PATTERN.
    """
    with database.Manager(USER_DB_PATH) as db:
        shared.db = db
        try:
            commands.create(name, filename, pattern)
        except DestinationExistsError as e:
            echo_error(str(e))


@run.command('add')
@click.argument('name')
@click.argument('filename', type=click.Path(exists=True))
@click.argument('pattern')
def add(name, filename, pattern):
    """
    Add new rows in an existing table.

    Add new rows in the table NAME. The data will be read from file FILENAME
    and parsed according to the provided PATTERN.
    """
    with database.Manager(USER_DB_PATH) as db:
        shared.db = db
        try:
            commands.add(name, filename, pattern)
        except (NoSuchTableError, ColumnsDoNotMatchError) as e:
            echo_error(str(e))


@run.command('show')
@click.argument('name')
def show(name):
    """
    Show content of a table.

    Display content of table NAME in standard output.
    """
    with database.Manager(USER_DB_PATH) as db:
        shared.db = db
        try:
            commands.show(name)
        except NoSuchTableError as e:
            echo_error(str(e))


@run.command('rename')
@click.argument('name1')
@click.argument('name2')
def rename(name1, name2):
    """
    Rename a table.

    Rename table NAME1 as NAME2. The default template associated with NAME1
    is also renamed to match the new name.
    """
    with database.Manager(USER_DB_PATH) as db:
        shared.db = db
        try:
            commands.rename(name1, name2)
        except (NoSuchTableError, DestinationExistsError) as e:
            echo_error(str(e))


@run.command('generate')
@click.argument('name')
@click.option('-n', '--questions-number', default=DEFAULT_Q_NB, type=int,
              show_default=True, help='number of questions')
def generate(name, questions_number):
    """
    Generate a new document.

    Generate a new document using the data from table NAME. The number of lines
    in the document's table can be specified via option -n.
    """
    with database.Manager(USER_DB_PATH) as db:
        shared.db = db
        try:
            commands.generate(name, nb=questions_number)
        except (NoSuchTableError, DestinationExistsError) as e:
            echo_error(str(e))
