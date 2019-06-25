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

import re


def parse_pattern(pattern):
    """
    Return a tuple containing the separator and the list of tags.

    Pattern example:
    '<tag1>:<tag2>' would return (':', ['tag1', 'tag2'])

    Exactly one separator must be found.
    """
    sep = {s.split('>')[-1] for s in pattern.split('<')}
    sep = {s for s in sep if s != ''}
    if len(sep) == 1:
        sep = sep.pop()
    else:
        raise ValueError('Cannot find a separator between tags in this '
                         'string: {}'.format(pattern))
    tags = re.findall(r'<.*?>', pattern)
    tags = [t[1:-1] for t in tags]
    return (sep, tags)


def parse_line(line, pattern):
    """Parse one line of data, according to pattern"""
    sep, _ = parse_pattern(pattern)
    return [l.strip() for l in line.split(sep)]
