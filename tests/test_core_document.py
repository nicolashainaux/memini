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

import pytest
from unittest.mock import patch

from vocashaker.core.env import TEMPLATE_EXT, TEST_TEMPLATE1_PATH
from vocashaker.core.errors import SchemeSyntaxError, SchemeLogicalError
from vocashaker.core.errors import SchemeColumnsMismatchError
from vocashaker.core.document import _default_scheme, _parse_scheme
from vocashaker.core.document import _process_data, generate


def test_default_scheme():
    assert _default_scheme(2) == '__1'
    assert _default_scheme(3) == '___2'
    assert _default_scheme(4) == '____3'
    assert _default_scheme(5) == '_____4'


def test_parse_scheme():
    with pytest.raises(SchemeSyntaxError) as excinfo:
        _parse_scheme('_F*')
    assert str(excinfo.value) == 'Incorrect scheme: "_F*". A scheme should '\
        'contain underscore and star chars ("_" and "*"), plus possibly one '\
        'digit as last char.'
    with pytest.raises(SchemeLogicalError) as excinfo:
        _parse_scheme('_*_3')
    assert str(excinfo.value) == 'Incorrect scheme: "_*_3". It shows 3 '\
        'columns, hence 2 of them at most can be blank, not more (3).'
    with pytest.raises(SchemeLogicalError) as excinfo:
        _parse_scheme('_*_4')
    assert str(excinfo.value) == 'Incorrect scheme: "_*_4". It shows 3 '\
        'columns, hence 2 of them at most can be blank, not more (4).'
    with pytest.raises(SchemeLogicalError) as excinfo:
        _parse_scheme('***')
    assert str(excinfo.value) == 'Incorrect scheme: "***". A scheme should '\
        'contain at least one possible blank column ("_").'
    with pytest.raises(SchemeLogicalError) as excinfo:
        _parse_scheme('**_2')
    assert str(excinfo.value) == 'Incorrect scheme: "**_2". It shows less '\
        'possible blank columns (1 "_") than it requires (2).'

    assert _parse_scheme('**_') == ([2], 1, 3)
    assert _parse_scheme('___') == ([0, 1, 2], 2, 3)
    assert _parse_scheme('___1') == ([0, 1, 2], 1, 3)


def test_process_data(mocker):
    data = [('adventus,  us, m.', 'arrivée'),
            ('candidus,  a, um', 'blanc'),
            ('sol, solis, m', 'soleil')]
    scheme = '___'
    with pytest.raises(SchemeColumnsMismatchError) as excinfo:
        _process_data(data, scheme)
    assert str(excinfo.value) == 'The provided scheme (___) does not have '\
        'the same number of columns as the table (2).'

    # Test default scheme
    result = _process_data(data)
    expected_answers = [{'col1': 'adventus,  us, m.', 'col2': 'arrivée'},
                        {'col1': 'candidus,  a, um', 'col2': 'blanc'},
                        {'col1': 'sol, solis, m', 'col2': 'soleil'}]
    assert result['answers'] == expected_answers
    assert len(result['rows']) == 3
    assert ((result['rows'][0]['col1'] == 'adventus,  us, m.'
             and result['rows'][0]['col2'] == '')
            or (result['rows'][0]['col1'] == ''
                and result['rows'][0]['col2'] == 'arrivée'))
    assert ((result['rows'][1]['col1'] == 'candidus,  a, um'
             and result['rows'][1]['col2'] == '')
            or (result['rows'][1]['col1'] == ''
                and result['rows'][1]['col2'] == 'blanc'))
    assert ((result['rows'][2]['col1'] == 'sol, solis, m'
             and result['rows'][2]['col2'] == '')
            or (result['rows'][2]['col1'] == ''
                and result['rows'][2]['col2'] == 'soleil'))

    data = [('bieten', 'bot, hat geboten', 'offrir'),
            ('bleiben', 'blieb, ist geblieben', 'rester'),
            ('gelingen', 'gelang, ist gelungen', 'réussir'),
            ('schmelzen', 'schmolz, ist geschmolzen', 'fondre'),
            ('ziegen', 'zog, hat OU ist gezogen', 'tirer OU déménager'),
            ]
    scheme = '__*'
    result = _process_data(data, scheme)
    expected_answers = \
        [{'col1': 'bieten', 'col2': 'bot, hat geboten', 'col3': 'offrir'},
         {'col1': 'bleiben', 'col2': 'blieb, ist geblieben', 'col3': 'rester'},
         {'col1': 'gelingen', 'col2': 'gelang, ist gelungen',
          'col3': 'réussir'},
         {'col1': 'schmelzen', 'col2': 'schmolz, ist geschmolzen',
          'col3': 'fondre'},
         {'col1': 'ziegen', 'col2': 'zog, hat OU ist gezogen',
          'col3': 'tirer OU déménager'}]
    assert result['answers'] == expected_answers
    expected_rows = \
        [{'col1': '', 'col2': '', 'col3': 'offrir'},
         {'col1': '', 'col2': '', 'col3': 'rester'},
         {'col1': '', 'col2': '', 'col3': 'réussir'},
         {'col1': '', 'col2': '', 'col3': 'fondre'},
         {'col1': '', 'col2': '', 'col3': 'tirer OU déménager'}]
    assert result['rows'] == expected_rows

    scheme = '__*1'
    result = _process_data(data, scheme)
    assert result['answers'] == expected_answers
    for row in result['rows']:
        assert list(row.keys()) == ['col1', 'col2', 'col3']
        assert list(row.values())[:-1].count('') == 1


def test_generate(mocker):
    mocker.patch('vocashaker.core.database.draw_rows')
    mt = mocker.patch('vocashaker.core.template.path')
    mt.return_value = TEST_TEMPLATE1_PATH
    m = mocker.patch('vocashaker.core.document._process_data')
    m.return_value = {'rows': [{'col1': 'adventus,  us, m.', 'col2': ''},
                               {'col1': '', 'col2': 'eau'},
                               {'col1': '', 'col2': 'blanc'},
                               {'col1': 'sol, solis, m', 'col2': ''},
                               {'col1': 'spes, ei f', 'col2': ''}],
                      'answers': [{'col1': 'adventus,  us, m.',
                                   'col2': 'arrivée'},
                                  {'col1': 'aqua , ae, f', 'col2': 'eau'},
                                  {'col1': 'candidus,  a, um',
                                   'col2': 'blanc'},
                                  {'col1': 'sol, solis, m', 'col2': 'soleil'},
                                  {'col1': 'spes, ei f', 'col2': 'espoir'}]}
    mo = mocker.mock_open()
    with patch('builtins.open', mo, create=True):
        generate('table1', 5)
    mo.assert_called_with('table1.{}'.format(TEMPLATE_EXT), 'wb')
