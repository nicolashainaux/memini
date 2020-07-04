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

from vocashaker.core.prefs import DEFAULT_Q_NB, SWEEPSTAKES_MAX
from vocashaker.core.env import USER_DB_PATH, __version__, PROG_NAME, MESSAGE
from vocashaker.core.env import MAXCOL_NB
from vocashaker.core.errors import CommandError, EmptyFileError, NotFoundError
from vocashaker.core.errors import NoSuchTableError, NoSuchRowError
from vocashaker.core.errors import NoSuchColumnError
from vocashaker.core.errors import DestinationExistsError
from vocashaker.core.errors import ColumnsDoNotMatchError
from vocashaker.core.errors import SchemeSyntaxError, SchemeLogicalError
from vocashaker.core.errors import SchemeColumnsMismatchError
from vocashaker.core.errors import CommandCancelledError, NoSuchSweepstakeError
from vocashaker.core import shared
from vocashaker.core import database
from vocashaker.core import commands


shared.init()

SW_CHOICES = [str(n) for n in range(SWEEPSTAKES_MAX + 1)]
COL_NBS = [str(n) for n in range(MAXCOL_NB)][1:]

__all__ = ['run']


def echo_info(s):
    term = blessed.Terminal()
    click.echo(term.lightskyblue('Info: ') + str(s))


def echo_warning(s):
    term = blessed.Terminal()
    click.echo(term.darkorange('Warning: ') + str(s))


def echo_error(s):
    term = blessed.Terminal()
    click.echo(term.color_rgb(197, 0, 11) + 'Error: ' + term.normal + str(s))
    exit(1)


@click.group()
@click.version_option(version=__version__, prog_name=PROG_NAME,
                      message=MESSAGE)
def run():
    """Manage vocabulary tables and generate training or test sheets."""


@run.command('list')
@click.argument('what')
def list_(what):
    """
    List known tables, templates or sweepstakes.

    List known tables, templates or sweepstakes. What to list exactly is set
    by argument WHAT (that may be "tables", "templates" or "sweepstakes").
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
    Parse a file and show result in console.

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
@click.option('-s', '--sort', default='False', show_default=True,
              type=click.Choice(['False', *COL_NBS], case_sensitive=False),
              help='sort output according to column')
def show(name, sort):
    """
    Show content of a table.

    Display content of table NAME in standard output.
    """
    if sort == 'False':
        sort = False
    else:
        sort = int(sort)
    with database.Manager(USER_DB_PATH) as db:
        shared.db = db
        try:
            commands.show(name, sort=sort)
        except (NoSuchTableError, NoSuchColumnError) as e:
            echo_error(str(e))


@run.command('sort')
@click.argument('name')
@click.option('-n', '--col-nb', default='1', type=click.Choice([*COL_NBS]),
              help='sort a table using n-th column')
def sort(name, col_nb):
    """
    Sort content of a table.

    Sort content of table NAME.
    """
    col_nb = int(col_nb)
    with database.Manager(USER_DB_PATH) as db:
        shared.db = db
        try:
            commands.sort(name, col_nb=col_nb)
        except (NoSuchTableError, NoSuchColumnError) as e:
            echo_error(str(e))


@run.command('dump')
@click.argument('sw_id')
def dump(sw_id):
    """
    Display content of a sweepstake.

    Display content of sweepstake #SW_ID in standard output.
    """
    with database.Manager(USER_DB_PATH) as db:
        shared.db = db
        try:
            commands.dump(sw_id)
        except NoSuchSweepstakeError as e:
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


@run.command('duplicate')
@click.argument('name1')
@click.argument('name2')
def duplicate(name1, name2):
    """
    Duplicate a table.

    Duplicate table NAME1 as NAME2. The default template associated with NAME1
    is also duplicated.
    """
    with database.Manager(USER_DB_PATH) as db:
        shared.db = db
        try:
            commands.duplicate(name1, name2)
        except (NoSuchTableError, DestinationExistsError) as e:
            echo_error(str(e))


@run.command('edit')
@click.argument('name')
def edit(name):
    """
    Edit a template.

    Run editor (e.g. LibreOffice) on "name" template.
    """
    with database.Manager(USER_DB_PATH) as db:
        shared.db = db
        try:
            commands.edit(name)
        except NotFoundError as e:
            echo_error(str(e))


@run.command('generate')
@click.argument('name')
@click.option('-n', '--questions-number', default=DEFAULT_Q_NB, type=int,
              show_default=True, help='number of questions')
@click.option('-s', '--scheme', default=None, type=str, help='scheme to use')
@click.option('-o', '--output', default=None, type=click.Path(),
              help='set output file name')
@click.option('-t', '--template', default=None, type=str,
              help='set alternative template')
@click.option('-f', '--force', default=False, is_flag=True, show_default=True,
              help='overwrite already existing file without asking')
@click.option('-e', '--edit', default=False, is_flag=True, show_default=True,
              help='edit document as soon as it has been generated')
@click.option('--use-previous', type=click.Choice(['None', *SW_CHOICES]),
              default='None', show_default=True,
              help='use a previous sweepstake')
def generate(name, questions_number, scheme, output, force, template, edit,
             use_previous):
    """
    Generate a new document.

    Generate a new document using the data from table NAME.

    The number of lines in the document's table can be specified via option -n.

    The --scheme option allows to specify which columns may be blanked in the
    questions. A scheme consists of underscore (_) and star (*) characters
    (one of them for each column) and ends with a number. A _ tells the column
    may be blank, a * tells it will never be blank. The number tells how many
    cells per row, at most, will be blank. The exact default scheme depends on
    the number of columns: for 2 columns it's __1, for 3 columns it's ___2 and
    for 4 columns it's ___3. They all mean any cell in a row may be blank; all
    cells but one will be blank.

    Scheme examples:

    - if you have a table of 3 columns and you wish the two last columns to
    always be blank, use *__2.

    - if you have 2 columns and you wish the first one to be always blank and
    the second one always filled, then use _*1.
    """
    with database.Manager(USER_DB_PATH) as db:
        shared.db = db
        try:
            commands.generate(name, nb=questions_number, scheme=scheme,
                              output=output, force=force, tpl=template,
                              edit=edit, use_previous=use_previous)
        except (NoSuchTableError, DestinationExistsError, SchemeSyntaxError,
                SchemeLogicalError, SchemeColumnsMismatchError,
                NoSuchSweepstakeError, NotFoundError,
                ColumnsDoNotMatchError) as e:
            echo_error(str(e))
        except CommandCancelledError as e:
            echo_info(str(e))
