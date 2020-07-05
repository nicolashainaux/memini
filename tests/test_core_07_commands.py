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

from vocashaker.core.env import TESTS_DATADIR, USER_SWEEPSTAKES_PATH
from vocashaker.core import template
from vocashaker.core import commands
from vocashaker.core import database
from vocashaker.core import sweepstakes
from vocashaker.core.errors import NoSuchTableError, DestinationExistsError
from vocashaker.core.errors import NotFoundError, CommandError
from vocashaker.core.errors import ColumnsDoNotMatchError


@pytest.fixture
def sw():
    return [os.path.join(USER_SWEEPSTAKES_PATH, '0_2020-07-02@15:13:22.json'),
            os.path.join(USER_SWEEPSTAKES_PATH, '1_2020-07-02@15:13:23.json'),
            os.path.join(USER_SWEEPSTAKES_PATH, '2_2020-07-02@15:13:24.json')]


def test_list_(testdb, capsys, fs, sw):
    fs.create_file(template.path('template1'))
    fs.create_file(template.path('template2'))
    commands.list_('tables')
    captured = capsys.readouterr()
    assert captured.out == 'table1\ntable2\n'
    commands.list_('templates')
    captured = capsys.readouterr()
    assert captured.out == 'template1.odt\ntemplate2.odt\n'
    for s in sw:
        fs.create_file(s)
    commands.list_('sweepstakes')
    captured = capsys.readouterr()
    assert captured.out == \
        '0_2020-07-02@15:13:22.json\n'\
        '1_2020-07-02@15:13:23.json\n'\
        '2_2020-07-02@15:13:24.json\n'
    with pytest.raises(CommandError) as excinfo:
        commands.list_('foo')
    assert str(excinfo.value) == 'Sorry, I can only list "tables", '\
        '"templates" or "sweepstakes". Please use one of these three '\
        'keywords. I will not try to list "foo".'


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


def test_update(testdb, capsys):
    commands.update('table2', '  2 | take | took, taken |   prendre  ')
    commands.show('table2')
    captured = capsys.readouterr()
    assert captured.out == \
        " id |  col1  |      col2     |     col3     \n"\
        "----+--------+---------------+--------------\n"\
        "  1 |  begin |  began, begun |   commencer  \n"\
        "  2 |   take |   took, taken |     prendre  \n"\
        "  3 |   do   |   did, done   |     faire    \n"\
        "  4 |  give  |  gave, given  |    donner    \n"


def test_dump(testdb, capsys, fs):
    data = [('adventus,  us, m.', 'arrivée'),
            ('candidus,  a, um', 'blanc'),
            ('sol, solis, m', 'soleil')]
    fs.create_dir(USER_SWEEPSTAKES_PATH)
    sweepstakes.store_sweepstake(data)
    commands.dump(0)
    captured = capsys.readouterr()
    assert captured.out == "('adventus,  us, m.', 'arrivée')\n"\
        "('candidus,  a, um', 'blanc')\n"\
        "('sol, solis, m', 'soleil')\n"


def test_duplicate(testdb, fs, capsys):
    fs.create_file(template.path('table1'))
    commands.duplicate('table1', 'table3')
    assert os.path.exists(template.path('table1'))
    assert os.path.exists(template.path('table3'))
    assert database.table_exists('table1')
    assert database.table_exists('table3')
    commands.show('table1')
    table1_content = capsys.readouterr().out
    commands.show('table3')
    table3_content = capsys.readouterr().out
    assert table1_content == table3_content


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


def test_add(testdb, capsys, mocker):
    f = os.path.join(TESTS_DATADIR, 'latin_add.txt')
    commands.add('table1', f, '<Latin>:<Français>')
    commands.show('table1')
    captured = capsys.readouterr()
    assert captured.out == \
        ' id |         col1        |                col2                \n'\
        '----+---------------------+------------------------------------\n'\
        '  1 |  adventus,  us, m.  |               arrivée              \n'\
        '  2 |     aqua , ae, f    |                 eau                \n'\
        '  3 |   candidus,  a, um  |                blanc               \n'\
        '  4 |    sol, solis, m    |               soleil               \n'\
        '  5 |  judex,  dicis, m.  |                juge                \n'\
        '  6 |   judicium,  i, n.  |         jugement, décision         \n'\
        '  7 |     jus, uris, n    |                droit               \n'\
        '  8 |   justitia, ae, f.  |           justice (vertu)          \n'\
        '  9 |   juvenis, is , m   |      homme jeune (30 à45 ans)      \n'\
        ' 10 | juventus,  utis, f. |              jeunesse              \n'\
        ' 11 |   labor,  oris, m.  | peine, souffrance, travail pénible \n'\
        ' 12 |   lacrima,  ae, f.  |                larme               \n'\
        ' 13 |   laetitia, ae, f.  |               la joie              \n'


def test_add_parse_err(testdb, capsys, mocker):
    f = os.path.join(TESTS_DATADIR, 'latin_add_parse_err.txt')
    commands.add('table1', f, '<Latin>:<Français>')
    commands.show('table1')
    captured = capsys.readouterr()
    assert captured.out == \
        ' id |         col1        |                col2                \n'\
        '----+---------------------+------------------------------------\n'\
        '  1 |  adventus,  us, m.  |               arrivée              \n'\
        '  2 |     aqua , ae, f    |                 eau                \n'\
        '  3 |   candidus,  a, um  |                blanc               \n'\
        '  4 |    sol, solis, m    |               soleil               \n'\
        '  5 |  judex,  dicis, m.  |                juge                \n'\
        '  6 |   judicium,  i, n.  |         jugement, décision         \n'\
        '  7 |     jus, uris, n    |                droit               \n'\
        '  8 |   justitia, ae, f.  |           justice (vertu)          \n'\
        '  9 |   juvenis, is , m   |      homme jeune (30 à45 ans)      \n'\
        ' 10 | juventus,  utis, f. |              jeunesse              \n'\
        ' 11 |   labor,  oris, m.  | peine, souffrance, travail pénible \n'\
        ' 12 |   lacrima,  ae, f.  |                larme               \n'
    assert captured.err == \
        'WARNING: following lines do not match the pattern '\
        '"<Latin>:<Français>" and have been ignored:\n'\
        '✘ laetitia, ae, f. la joie\n'\
        'End of ignored lines list\n'


def test_add_to_nonexistent_table(testdb):
    f = os.path.join(TESTS_DATADIR, 'latin_add.txt')
    with pytest.raises(NoSuchTableError) as excinfo:
        commands.add('table3', f, '<Latin>:<Français>')
    assert str(excinfo.value) == 'Cannot find a table named "table3"'


def test_add_with_cols_nb_mismatch(testdb):
    f = os.path.join(TESTS_DATADIR, 'latin_add.txt')
    with pytest.raises(ColumnsDoNotMatchError) as excinfo:
        commands.add('table1', f, '<Latin>:<Français>:<Superflu>')
    assert str(excinfo.value) == '"<Latin>:<Français>:<Superflu>" '\
        'requires 3 columns, but "table1" has 2 columns '\
        '("col1" and "col2").'


def test_edit(fs, mocker):
    m = mocker.patch('vocashaker.core.template.edit')
    fs.create_file(template.path('tpl1'))
    assert os.path.isfile(template.path('tpl1'))
    commands.edit('tpl1')
    m.assert_called_with('tpl1')
    with pytest.raises(NotFoundError) as excinfo:
        commands.edit('tpl2.odt')
    assert str(excinfo.value) == 'Cannot find any template "tpl2.odt".'


def test_generate(mocker):
    m = mocker.patch('vocashaker.core.document.generate')
    commands.generate('table1', 4)
    m.assert_called_with('table1', 4, scheme=None, force=False, output=None,
                         tpl=None, edit_after=False, use_previous=None)
