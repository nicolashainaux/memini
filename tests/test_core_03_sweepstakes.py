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
import datetime

import pytest

from vocashaker.core.env import USER_SWEEPSTAKES_PATH
from vocashaker.core.errors import NoSuchSweepstakeError
from vocashaker.core.sweepstakes import _serialize, _deserialize
from vocashaker.core.sweepstakes import _new_sweepstake, _get_sweepstakes
from vocashaker.core.sweepstakes import list_sweepstakes
from vocashaker.core.sweepstakes import _get_sweepstake_name
from vocashaker.core.sweepstakes import _rotate_sweepstakes
from vocashaker.core.sweepstakes import store_sweepstake, load_sweepstake


class MockedDatetime(datetime.datetime):
    @classmethod
    def now(cls):
        return cls(2020, 7, 2, 15, 13, 22, 210269)


datetime.datetime = MockedDatetime


@pytest.fixture
def sw1():
    return os.path.join(USER_SWEEPSTAKES_PATH, '1_2020-07-02@15:13:22.json')


@pytest.fixture
def sw2():
    return os.path.join(USER_SWEEPSTAKES_PATH, '2_2020-07-02@15:13:23.json')


@pytest.fixture
def sweepstakes():
    return [os.path.join(USER_SWEEPSTAKES_PATH, '1_2020-07-02@15:13:22.json'),
            os.path.join(USER_SWEEPSTAKES_PATH, '2_2020-07-02@15:13:23.json'),
            os.path.join(USER_SWEEPSTAKES_PATH, '3_2020-07-02@15:13:24.json'),
            os.path.join(USER_SWEEPSTAKES_PATH, '4_2020-07-02@15:13:25.json'),
            os.path.join(USER_SWEEPSTAKES_PATH, '5_2020-07-02@15:13:26.json'),
            os.path.join(USER_SWEEPSTAKES_PATH, '6_2020-07-02@15:13:27.json'),
            os.path.join(USER_SWEEPSTAKES_PATH, '7_2020-07-02@15:13:28.json'),
            os.path.join(USER_SWEEPSTAKES_PATH, '8_2020-07-02@15:13:29.json'),
            os.path.join(USER_SWEEPSTAKES_PATH, '9_2020-07-02@15:13:30.json')]


def test_serialization():
    data = [('adventus,  us, m.', 'arrivée'),
            ('candidus,  a, um', 'blanc'),
            ('sol, solis, m', 'soleil')]
    assert _serialize(data) == {
        0: ['adventus,  us, m.', 'arrivée'],
        1: ['candidus,  a, um', 'blanc'],
        2: ['sol, solis, m', 'soleil']
        }
    assert _deserialize(_serialize(data)) == data


def test_new_sweepstake(mocker, sw1):
    assert _new_sweepstake() == sw1


def test_get_sweepstakes(fs, sweepstakes):
    for sw in sweepstakes:
        fs.create_file(sw)
    assert _get_sweepstakes() == sweepstakes


def test_list_sweepstakes(fs, sweepstakes):
    for sw in sweepstakes:
        fs.create_file(sw)
    assert list_sweepstakes() == ['1_2020-07-02@15:13:22.json',
                                  '2_2020-07-02@15:13:23.json',
                                  '3_2020-07-02@15:13:24.json',
                                  '4_2020-07-02@15:13:25.json',
                                  '5_2020-07-02@15:13:26.json',
                                  '6_2020-07-02@15:13:27.json',
                                  '7_2020-07-02@15:13:28.json',
                                  '8_2020-07-02@15:13:29.json',
                                  '9_2020-07-02@15:13:30.json']


def test_get_sweepstake_name(fs, sw1, sw2, sweepstakes):
    for sw in sweepstakes:
        fs.create_file(sw)
    assert _get_sweepstake_name(1) == sw1
    assert _get_sweepstake_name(2) == sw2
    with pytest.raises(NoSuchSweepstakeError) as excinfo:
        _get_sweepstake_name(10)
    assert str(excinfo.value) == 'Cannot find a sweepstake starting with "10"'


def test_rotate_sweepstakes(fs, sweepstakes):
    # With no sweepstake files, it will just do nothing:
    _rotate_sweepstakes()
    # Now we add faked files to let _rotate_sweepstakes() really rotate them:
    for sw in sweepstakes:
        fs.create_file(sw)
    _rotate_sweepstakes()
    assert [os.path.basename(f) for f in _get_sweepstakes()] \
        == ['2_2020-07-02@15:13:22.json',
            '3_2020-07-02@15:13:23.json',
            '4_2020-07-02@15:13:24.json',
            '5_2020-07-02@15:13:25.json',
            '6_2020-07-02@15:13:26.json',
            '7_2020-07-02@15:13:27.json',
            '8_2020-07-02@15:13:28.json',
            '9_2020-07-02@15:13:29.json']


def test_store_load_sweepstakes(fs):
    data = [('adventus,  us, m.', 'arrivée'),
            ('candidus,  a, um', 'blanc'),
            ('sol, solis, m', 'soleil')]
    fs.create_dir(USER_SWEEPSTAKES_PATH)
    store_sweepstake('table1', data)
    assert load_sweepstake() == [('table1', )] + data
