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

from vocashaker.core.errors import PatternError, MismatchError


def parse_pattern(pattern):
    """
    Return a tuple containing the separator and the list of tags.

    Pattern example:
    '<tag1>:<tag2>' would return (':', ['tag1', 'tag2'])

    Exactly one separator must be found.
    """
    missing_tag_position = pattern.find('><')
    if missing_tag_position != -1:
        raise PatternError(pattern, missing_tag_position)
    tags = re.findall(r'<.*?>', pattern)
    regex = pattern
    for t in tags:
        regex = regex.replace(t, '(.*?)')
    tags = [t[1:-1] for t in tags]
    return (regex, tags)


def parse_line(pattern, line):
    """Parse one line of data, according to pattern"""
    regex, _ = parse_pattern(pattern)
    match = re.fullmatch(regex, line)
    if match:
        result = [g.strip() for g in match.groups()]
    else:
        raise MismatchError(line, pattern)
    return result


def parse_file(filename, pattern):
    """Parse one entire file of data lines, according to pattern"""
