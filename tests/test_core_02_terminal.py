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

from unittest.mock import patch
from collections import namedtuple

from vocashaker.core import terminal


def test_ask_yes_no(capsys):
    with patch('builtins.input') as mock_input:
        mock_input.return_value = 'YES'
        answer = terminal.ask_yes_no('Will you do it?')
        assert answer
        mock_input.assert_called_with('Will you do it? [y/N] ')

        answer = terminal.ask_yes_no('Will you do it?', default=True)
        assert answer
        mock_input.assert_called_with('Will you do it? [Y/n] ')

        values = ['Y', 'y', 'yes', 'Yes', 'yEs', 'yeS', 'YEs', 'yES', 'YeS']
        mock_input.side_effect = values
        for i in range(len(values)):
            assert terminal.ask_yes_no('Will you do it?')

        values = ['N', 'n', 'no', 'No', 'nO', 'NO']
        mock_input.side_effect = values
        for i in range(len(values)):
            assert not terminal.ask_yes_no('Will you do it?')

        mock_input.side_effect = ['', '']
        assert not terminal.ask_yes_no('Will you do it?')
        assert terminal.ask_yes_no('Will you do it?', default=True)

        mock_input.side_effect = ['maybe', 'Y']
        terminal.ask_yes_no('Will you do it?')
        captured = capsys.readouterr()
        assert captured.out == 'Sorry, I didn\'t understand.\n'


def test_hcenter():
    assert terminal._hcenter('hello', 11) == '   hello   '
    assert terminal._hcenter('hello', 12) == '    hello   '


def test_allocate_widths(mocker):
    TSize = namedtuple('TSize', 'columns lines')
    t1 = TSize(168, 44)
    mocker.patch('shutil.get_terminal_size', return_value=t1)
    assert terminal._allocate_widths([80, 120]) == [80, 87]
    t2 = TSize(80, 40)
    mocker.patch('shutil.get_terminal_size', return_value=t2)
    assert terminal._allocate_widths([90, 90]) == [39, 39]
    assert terminal._allocate_widths([20, 40, 40]) == [20, 29, 29]


def test_expand_rows():
    data = [('id', 'col1', 'col2'),
            ('1', 'adven tus,us, m.', 'arriv ée')]
    assert terminal._expand_rows(data, [4, 7, 6]) == \
        [('id', 'col1', 'col2'),
         ('1', 'adven', 'arriv'),
         ('', 'tus,us,', 'ée'),
         ('', 'm.', '')]
    data = [('id', 'col1', 'col2'),
            ('1', 'adventus,  us, m.', 'arrivée'),
            ('2', 'aqua , ae, f', 'eau'),
            ('3', 'candidus,  a, um', 'blanc'),
            ('4', 'sol, solis, m', 'soleil')]
    assert terminal._expand_rows(data, [4, 19, 9]) == data


def test_tabulate(testdb):
    data = [('id', 'col1', 'col2'),
            ('1', 'adventus,  us, m.', 'arrivée'),
            ('2', 'aqua , ae, f', 'eau'),
            ('3', 'candidus,  a, um', 'blanc'),
            ('4', 'sol, solis, m', 'soleil')]
    assert terminal.tabulate(data) == \
        " id |        col1       |   col2  \n"\
        "----+-------------------+---------\n"\
        "  1 | adventus,  us, m. | arrivée \n"\
        "  2 |    aqua , ae, f   |   eau   \n"\
        "  3 |  candidus,  a, um |  blanc  \n"\
        "  4 |   sol, solis, m   |  soleil "
    data = [('id', 'col1', 'col2'),
            ('1', '', 'arrivée')]
    assert terminal.tabulate(data) == \
        " id | col1 |   col2  \n"\
        "----+------+---------\n"\
        "  1 |      | arrivée "
