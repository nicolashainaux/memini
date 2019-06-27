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


class VocaShakerError(Exception):
    """Basic exception for errors raised by VocaShaker."""
    def __init__(self, msg):
        super().__init__(msg)


class PatternError(VocaShakerError):
    """When an incorrect pattern is provided."""
    def __init__(self, pattern, missing_tag_position):
        msg = 'Missing separator in pattern:\n{}\n{}'\
            .format(pattern, ' ' * (missing_tag_position + 1) + '^')
        super().__init__(msg)


class MismatchError(VocaShakerError):
    """When a line does not match the provided pattern."""
    def __init__(self, line, pattern):
        msg = 'This line: {}\ndoes not match provided pattern: {}'\
            .format(line, pattern)
        super().__init__(msg)
