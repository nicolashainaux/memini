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
    with database.Manager(USER_DB_PATH) as db:
        shared.db = db
        try:
            commands.list_(what)
        except CommandError as e:
            echo_error(str(e))


@run.command('parse')
@click.option('--errors-only', is_flag=True, default=False, show_default=True)
@click.argument('filename', type=click.Path(exists=True))
@click.argument('pattern')
def parse(filename, pattern, errors_only):
    with database.Manager(USER_DB_PATH) as db:
        shared.db = db
        try:
            commands.parse(filename, pattern, errors_only)
        except EmptyFileError as e:
            echo_warning(str(e))


@run.command('delete')
@click.argument('name')
def delete(name):
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
    with database.Manager(USER_DB_PATH) as db:
        shared.db = db
        try:
            commands.remove(name, span)
        except (NoSuchTableError, NoSuchRowError) as e:
            echo_error(str(e))


@run.command('create')
@click.argument('name')
@click.argument('file_name', type=click.Path())
@click.argument('pattern')
def create(name, file_name, pattern):
    with database.Manager(USER_DB_PATH) as db:
        shared.db = db
        try:
            commands.create(name, file_name, pattern)
        except DestinationExistsError as e:
            echo_error(str(e))


@run.command('add')
@click.argument('name')
@click.argument('file_name', type=click.Path(exists=True))
@click.argument('pattern')
def add(name, file_name, pattern):
    with database.Manager(USER_DB_PATH) as db:
        shared.db = db
        try:
            commands.add(name, file_name, pattern)
        except (NoSuchTableError, ColumnsDoNotMatchError) as e:
            echo_error(str(e))


@run.command('show')
@click.argument('name')
def show(name):
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
    with database.Manager(USER_DB_PATH) as db:
        shared.db = db
        try:
            commands.rename(name1, name2)
        except (NoSuchTableError, DestinationExistsError) as e:
            echo_error(str(e))


@run.command('generate')
@click.argument('name')
@click.option('-n', '--questions-number', default=DEFAULT_Q_NB, type=int,
              show_default=True)
def generate(name, questions_number):
    with database.Manager(USER_DB_PATH) as db:
        shared.db = db
        try:
            commands.generate(name, nb=questions_number)
        except (NoSuchTableError, DestinationExistsError) as e:
            echo_error(str(e))
