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
import json
import shutil

import datetime
from glob import glob

from .env import USER_SWEEPSTAKES_PATH
from .prefs import SWEEPSTAKES_MAX
from .errors import NoSuchSweepstakeError


def _serialize(rows):
    return {i: list(row) for i, row in enumerate(rows)}


def _deserialize(data):
    return [tuple(v) for v in data.values()]


def _new_sweepstake():
    dt = str(datetime.datetime.now().replace(microsecond=0)).replace(' ', '@')
    return os.path.join(USER_SWEEPSTAKES_PATH, f'1_{dt}.json')


def _get_sweepstakes():
    return sorted(
        [f for f in glob(os.path.join(USER_SWEEPSTAKES_PATH, '*.json'))])


def list_sweepstakes():
    return [os.path.basename(sw) for sw in _get_sweepstakes()]


def _get_sweepstake_name(sw_id=1):
    for name in list_sweepstakes():
        if name.startswith(f'{sw_id}_') and name.endswith('.json'):
            return os.path.join(USER_SWEEPSTAKES_PATH, name)
    raise NoSuchSweepstakeError(sw_id=sw_id)


def _rotate_sweepstakes():
    for f in reversed(sorted(_get_sweepstakes())):
        b = os.path.basename(f)
        f_id = int(b.split('_')[0])
        if f_id >= SWEEPSTAKES_MAX:
            os.remove(f)
        else:
            new_name = os.path.join(USER_SWEEPSTAKES_PATH,
                                    str(f_id + 1) + f"_{b.split('_')[1]}")
            shutil.move(f, new_name)


def store_sweepstake(rows):
    _rotate_sweepstakes()
    with open(_new_sweepstake(), 'w') as f:
        json.dump(_serialize(rows), f, indent=4)
        f.write('\n')


def load_sweepstake(sw_id=1):
    with open(_get_sweepstake_name(sw_id), 'r') as f:
        return _deserialize(json.load(f))
