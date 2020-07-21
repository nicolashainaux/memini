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

import re

from memini.core.prefs import ENCODING
from memini.core.errors import MissingSeparatorError, LineDoesNotMatchError
from memini.core.errors import EmptyFileError


def parse_pattern(pattern, sep_list=False):
    """
    Return a tuple containing a regex and the list of tags.

    Pattern example:
    '<tag1>:<tag2>' would return ('(.*?):(.*?)', ['tag1', 'tag2'])
    """
    missing_tag_position = pattern.find('><')
    if missing_tag_position != -1:
        raise MissingSeparatorError(pattern, missing_tag_position)
    tags = re.findall(r'<.*?>', pattern)
    regex = pattern
    for t in tags:
        regex = regex.replace(t, '(.*?)')
    tags = [t[1:-1] for t in tags]
    if sep_list:
        regex = regex.split('(.*?)')[1:-1]
    return (regex, tuple(tags))


def parse_line(pattern, line):
    """Parse one line of data, according to pattern"""
    regex, _ = parse_pattern(pattern)
    match = re.fullmatch(regex, line)
    if match:
        result = tuple(g.strip() for g in match.groups())
    else:
        raise LineDoesNotMatchError(line, pattern)
    return result


def parse_file(filename, pattern):
    """Parse one entire file of data lines, according to pattern"""
    result = []
    nomatch = []
    with open(filename, encoding=ENCODING) as f:
        for line in f.readlines():
            if line.strip():
                try:
                    to_add = parse_line(pattern, line.strip())
                except LineDoesNotMatchError:
                    nomatch.append(line.strip())
                else:
                    result.append(to_add)
    if not result and not nomatch:
        raise EmptyFileError('The provided file seems empty, could not find '
                             'a single line to parse.')
    return (result, nomatch)
