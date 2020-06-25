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

import os
from unittest.mock import call

import pytest

from vocashaker.core.env import TESTS_DATADIR
from vocashaker.core import template
from vocashaker.core import commands
from vocashaker.core import database
from vocashaker.core.errors import NoSuchTableError, DestinationExistsError
from vocashaker.core.errors import NotFoundError, CommandError


def test_list_(testdb, capsys, fs):
    fs.create_file(template.path('template1'))
    fs.create_file(template.path('template2'))
    commands.list_('tables')
    captured = capsys.readouterr()
    assert captured.out == 'table1\ntable2\n'
    commands.list_('templates')
    captured = capsys.readouterr()
    assert captured.out == 'template1.odt\ntemplate2.odt\n'
    with pytest.raises(CommandError) as excinfo:
        commands.list_('foo')
    assert str(excinfo.value) == 'Sorry, I can only list "tables" or '\
        '"templates". Please use one of these two keywords. '\
        'I will not try to list "foo".'


def test_rename(testdb, fs, mocker):
    m = mocker.patch('vocashaker.core.database.rename_table')
    fs.create_file(template.path('table1'))
    commands.rename('table1', 'table3')
    assert os.path.exists(template.path('table3'))
    assert not os.path.exists(template.path('table1'))
    m.assert_called_with('table1', 'table3')


def test_rename_nonexistent_table(testdb):
    with pytest.raises(NoSuchTableError) as excinfo:
        commands.rename('nonexistent', 'newname')
    assert str(excinfo.value) == 'Cannot find a table named "nonexistent"'


def test_rename_missing_template(testdb, fs, mocker):
    # No template for source table: automatic creation
    def create_fake_template(*args):
        fs.create_file(template.path('table1'))

    m = mocker.patch('vocashaker.core.template.create',
                     side_effect=create_fake_template)
    commands.rename('table1', 'table4')
    m.assert_called_with('table1')
    assert os.path.exists(template.path('table4'))
    assert not os.path.exists(template.path('table1'))
    assert database.table_exists('table4')
    assert not database.table_exists('table1')


def test_rename_to_existing_table(testdb, fs):
    fs.create_file(template.path('table1'))

    with pytest.raises(DestinationExistsError) as excinfo:
        commands.rename('table1', 'table2')
    assert str(excinfo.value) == 'Action cancelled: a table named "table2" '\
        'already exists. Please rename or remove it before using this name.'


def test_rename_to_existing_template(testdb, fs):
    fs.create_file(template.path('table1'))
    fs.create_file(template.path('table3'))

    with pytest.raises(DestinationExistsError) as excinfo:
        commands.rename('table1', 'table3')
    assert str(excinfo.value) == 'Action cancelled: a template named '\
        '"table3" already exists. Please rename or remove it before using '\
        'this name.'


def test_delete(fs, mocker, testdb):
    fs.create_file(template.path('table1'))
    m = mocker.patch('vocashaker.core.terminal.ask_yes_no')

    # User cancels the deletions
    m.side_effect = [False, False]
    commands.delete('table1')
    m.assert_has_calls([call('Delete table "table1"?'),
                        call('Delete template "table1"?')])
    assert os.path.exists(template.path('table1'))
    assert database.table_exists('table1')

    # User confirms the deletions
    m.side_effect = [True, True]
    commands.delete('table1')
    assert not os.path.exists(template.path('table1'))
    assert not database.table_exists('table1')


def test_delete_nonexistent(testdb):
    with pytest.raises(NotFoundError) as excinfo:
        commands.delete('table3')
    assert str(excinfo.value) == 'No table nor template named "table3" can '\
        'be found to be deleted.'


def test_show_nonexistent(testdb):
    with pytest.raises(NoSuchTableError) as excinfo:
        commands.show('nonexistent')
    assert str(excinfo.value) == 'Cannot find a table named "nonexistent"'


def test_show(testdb, capsys):
    commands.show('table2')
    captured = capsys.readouterr()
    assert captured.out == \
        " id |  col1 |      col2     |    col3   \n"\
        "----+-------+---------------+-----------\n"\
        "  1 | begin |  began, begun | commencer \n"\
        "  2 | break | broke, broken |   casser  \n"\
        "  3 |   do  |   did, done   |   faire   \n"\
        "  4 |  give |  gave, given  |   donner  \n"


def test_remove(mocker):
    m = mocker.patch('vocashaker.core.database.remove_rows')
    commands.remove('table2', '2,3')
    m.assert_called_with('table2', '2,3')


def test_parse(capsys, mocker):
    f = os.path.join(TESTS_DATADIR, 'latin.txt')
    commands.parse(f, '<Latin>:<Français>')
    captured = capsys.readouterr()
    assert captured.out == \
        '         Latin        |       Français      \n'\
        '----------------------+---------------------\n'\
        '    actio, onis, f.   | procès , plaidoirie \n'\
        ' admiratio,  onis, f. |      admiration     \n'\
        '   adventus,  us, m.  |       arrivée       \n'\
        '   aedilis,  is, m.   |        édile        \n'\
        '  aetas, atis, f âge  |         vie         \n'\
        '   ambitio, onis, f.  |       ambition      \n'\
        '    ambitus, us, m.   |      la brigue      \n'\
        '   amicitia,  ae, f.  |        amitié       \n'\
        '    amicus,  i, m.    |         ami         \n'\
        '    amor,  oris, m.   |        amour        \n'\
        '    anima,  ae, f.    |      coeur, âme     \n'
    commands.parse(f, '<Latin>:<Français>', errors_only=True)
    captured = capsys.readouterr()
    assert captured.out == ''
    assert captured.err == 'No parsing errors ☺\n'

    f = os.path.join(TESTS_DATADIR, 'latin_parse_err.txt')
    commands.parse(f, '<Latin>:<Français>')
    captured = capsys.readouterr()
    assert captured.out == \
        '         Latin        |       Français      \n'\
        '----------------------+---------------------\n'\
        '    actio, onis, f.   | procès , plaidoirie \n'\
        ' admiratio,  onis, f. |      admiration     \n'\
        '   adventus,  us, m.  |       arrivée       \n'\
        '  aetas, atis, f âge  |         vie         \n'\
        '   ambitio, onis, f.  |       ambition      \n'\
        '    amicus,  i, m.    |         ami         \n'\
        '    amor,  oris, m.   |        amour        \n'\
        '    anima,  ae, f.    |      coeur, âme     \n'
    assert captured.err == \
        'WARNING: following lines do not match the pattern '\
        '"<Latin>:<Français>" and have been ignored:\n'\
        '✘ aedilis,  is, m.  édile\n'\
        '✘ ambitus, us, m. la brigue\n'\
        '✘ amicitia,  ae, f. amitié\n'\
        'End of ignored lines list\n'
    commands.parse(f, '<Latin>:<Français>', errors_only=True)
    captured = capsys.readouterr()
    assert captured.out == ''
    assert captured.err == \
        'aedilis,  is, m.  édile\n'\
        'ambitus, us, m. la brigue\n'\
        'amicitia,  ae, f. amitié\n'


def test_create(testdb, capsys, mocker):
    m = mocker.patch('vocashaker.core.template.create')
    f = os.path.join(TESTS_DATADIR, 'latin.txt')
    commands.create('latin', f, '<Latin>:<Français>')
    m.assert_called_with('latin')
    commands.show('latin')
    captured = capsys.readouterr()
    assert captured.out == \
        ' id |         Latin        |       Français      \n'\
        '----+----------------------+---------------------\n'\
        '  1 |    actio, onis, f.   | procès , plaidoirie \n'\
        '  2 | admiratio,  onis, f. |      admiration     \n'\
        '  3 |   adventus,  us, m.  |       arrivée       \n'\
        '  4 |   aedilis,  is, m.   |        édile        \n'\
        '  5 |  aetas, atis, f âge  |         vie         \n'\
        '  6 |   ambitio, onis, f.  |       ambition      \n'\
        '  7 |    ambitus, us, m.   |      la brigue      \n'\
        '  8 |   amicitia,  ae, f.  |        amitié       \n'\
        '  9 |    amicus,  i, m.    |         ami         \n'\
        ' 10 |    amor,  oris, m.   |        amour        \n'\
        ' 11 |    anima,  ae, f.    |      coeur, âme     \n'


def test_create_with_parse_errors(testdb, capsys, mocker):
    m = mocker.patch('vocashaker.core.template.create')
    f = os.path.join(TESTS_DATADIR, 'latin_parse_err.txt')
    commands.create('latin2', f, '<Latin>:<Français>')
    m.assert_called_with('latin2')
    captured = capsys.readouterr()
    assert captured.err == \
        'WARNING: following lines do not match the pattern '\
        '"<Latin>:<Français>" and have been ignored:\n'\
        '✘ aedilis,  is, m.  édile\n'\
        '✘ ambitus, us, m. la brigue\n'\
        '✘ amicitia,  ae, f. amitié\n'\
        'End of ignored lines list\n'
    commands.show('latin2')
    captured = capsys.readouterr()
    assert captured.out == \
        ' id |         Latin        |       Français      \n'\
        '----+----------------------+---------------------\n'\
        '  1 |    actio, onis, f.   | procès , plaidoirie \n'\
        '  2 | admiratio,  onis, f. |      admiration     \n'\
        '  3 |   adventus,  us, m.  |       arrivée       \n'\
        '  4 |  aetas, atis, f âge  |         vie         \n'\
        '  5 |   ambitio, onis, f.  |       ambition      \n'\
        '  6 |    amicus,  i, m.    |         ami         \n'\
        '  7 |    amor,  oris, m.   |        amour        \n'\
        '  8 |    anima,  ae, f.    |      coeur, âme     \n'


def test_create_already_existing_table_or_template(testdb, capsys, fs):
    fs.create_file('some_source.txt')

    with pytest.raises(DestinationExistsError) as excinfo:
        commands.create('table1', 'some_source.txt', '<Latin>:<Français>')
    assert str(excinfo.value) == 'Action cancelled: a table named '\
        '"table1" already exists. Please rename or remove it '\
        'before using this name.'

    fs.create_file(template.path('already_in_use'))
    with pytest.raises(DestinationExistsError) as excinfo:
        commands.create('already_in_use', 'some_source.txt',
                        '<Latin>:<Français>')
    assert str(excinfo.value) == 'Action cancelled: a template named '\
        '"already_in_use" already exists. Please rename or remove it '\
        'before using this name.'


def test_generate(mocker):
    m = mocker.patch('vocashaker.core.document.generate')
    commands.generate('table1', 4)
    m.assert_called_with('table1', nb=4)
