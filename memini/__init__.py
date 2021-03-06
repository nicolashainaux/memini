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

import click
import blessed

from memini.core.prefs import DEFAULT_Q_NB
from memini.core.env import USER_DB_PATH, __version__, PROG_NAME, MESSAGE
from memini.core.env import MAXCOL_NB
from memini.core.errors import MeminiError, CommandCancelledError
from memini.core import shared
from memini.core import database
from memini.core import commands


shared.init()

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


def _cmd(cmd, *args, do_click_echo=echo_error):
    """Generic command"""
    with database.Manager(USER_DB_PATH) as db:
        shared.db = db
        try:
            cmd(*args)
        except MeminiError as e:
            do_click_echo(str(e))


@run.command('list')
@click.argument('what')
def list_(what):
    """
    List known tables, templates or sweepstakes.

    List known tables, templates or sweepstakes. What to list exactly is set
    by argument WHAT (that may be "tables", "templates" or "sweepstakes").
    """
    _cmd(commands.list_, what)


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
    _cmd(commands.parse, filename, pattern, errors_only,
         do_click_echo=echo_warning)


@run.command('delete')
@click.argument('name')
def delete(name):
    """
    Delete a table.

    Delete the table NAME. The matching default template will be deleted too.
    """
    _cmd(commands.delete, name)


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
    _cmd(commands.remove, name, span)


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
    _cmd(commands.create, name, filename, pattern)


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
    _cmd(commands.add, name, filename, pattern)


@run.command('show')
@click.argument('name')
@click.option('-s', '--sort', default=0, show_default=True,
              type=click.IntRange(0, MAXCOL_NB),
              help='sort output according to column')
def show(name, sort):
    """
    Show content of a table.

    Display content of table NAME in standard output.
    """
    _cmd(commands.show, name, int(sort))


@run.command('sort')
@click.argument('name')
@click.option('-n', '--col-nb', default=1, type=click.IntRange(0, MAXCOL_NB),
              help='sort a table using n-th column')
def sort(name, col_nb):
    """
    Sort content of a table.

    Sort content of table NAME.
    """
    _cmd(commands.sort, name, int(col_nb))


@run.command('update')
@click.argument('name')
@click.argument('row')
def update(name, row):
    """
    Update a row of a table.

    Update a row of the table NAME. The row must be provided as it should be
    displayed when using the command "show": the fields are separated by a
    pipe (this: |) and the first field must be the row id. For instance:
    vosh update mytable "4 | to speak | spoke, spoken | parler"
    will put the contents "to speak", "spoke, spoken" and "parler" into row
    number 4 of table "mytable". Of course the number of fields must match the
    number of columns in the table.
    """
    _cmd(commands.update, name, row)


@run.command('dump')
@click.argument('sw_id')
def dump(sw_id):
    """
    Display content of a sweepstake.

    Display content of sweepstake #SW_ID in standard output.
    """
    _cmd(commands.dump, sw_id)


@run.command('rename')
@click.argument('name1')
@click.argument('name2')
def rename(name1, name2):
    """
    Rename a table.

    Rename table NAME1 as NAME2. The default template associated with NAME1
    is also renamed to match the new name.
    """
    _cmd(commands.rename, name1, name2)


@run.command('duplicate')
@click.argument('name1')
@click.argument('name2')
def duplicate(name1, name2):
    """
    Duplicate a table.

    Duplicate table NAME1 as NAME2. The default template associated with NAME1
    is also duplicated.
    """
    _cmd(commands.duplicate, name1, name2)


@run.command('merge')
@click.argument('src', nargs=-1)
@click.argument('dest', nargs=1)
def merge(src, dest):
    """
    Merge tables.

    Append the content of tables from SRC to the DEST table.
    """
    _cmd(commands.merge, src, dest)


@run.command('edit')
@click.argument('name')
def edit(name):
    """
    Edit a template.

    Run editor (e.g. LibreOffice) on "name" template.
    """
    _cmd(commands.edit, name)


@run.command('generate')
@click.argument('name', required=False)
@click.option('-n', '--questions-number', default=DEFAULT_Q_NB, type=int,
              show_default=True, help='number of questions')
@click.option('-s', '--scheme', default=None, type=str, help='scheme to use')
@click.option('-o', '--output', default=None, type=click.Path(),
              help='set output file name')
@click.option('-t', '--template', default=None, type=str,
              help='set alternative template')
@click.option('-f', '--force', default=False, is_flag=True, show_default=True,
              help='overwrite already existing file without asking')
@click.option('-e', '--edit', default=True, is_flag=True, show_default=True,
              help='edit document as soon as it has been generated')
@click.option('--use-previous', is_flag=True, default=False, show_default=True,
              help='use a previous sweepstake')
def generate(name, questions_number, scheme, output, force, template, edit,
             use_previous):
    """
    Generate a new document.

    Generate a new document using the data from table NAME.

    The --use-previous option can be used to reuse data from previous drawings
    (stored as "sweepstakes"). If it is used, then the NAME argument must be
    a sweepstake's id, or not written (then the sweepstake's id defaults to 1).

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
    if name is None:
        if use_previous:
            name = '1'
        else:
            echo_error('Missing argument \'NAME\'. It is required unless '
                       'option --use-previous is turned on. '
                       'Try \'vosh generate --help\' for help.')
    with database.Manager(USER_DB_PATH) as db:
        shared.db = db
        try:
            commands.generate(name, nb=questions_number, scheme=scheme,
                              output=output, force=force, tpl=template,
                              edit=edit, use_previous=use_previous)
        except CommandCancelledError as e:
            echo_info(str(e))
        except MeminiError as e:
            echo_error(str(e))
