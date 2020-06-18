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


def ask_yes_no(question, default=False):
    """
    Ask the user to give a positive or negative answer to the given question.
    Accepted answers are case insensitive 'yes', 'no', 'y' or 'n'.
    If the user only types "enter" then the default answer is returned.
    The default answer depends on the default keyword argument: False for "no",
    True for "yes".
    If any unaccepted answer is given, then the user is asked again.
    """
    result = None
    yn = '[Y/n]' if default else '[y/N]'
    while result is None:
        answer = input('{} {} '.format(question, yn))
        if answer.lower() in ['y', 'yes']:
            result = True
        elif answer.lower() in ['n', 'no']:
            result = False
        elif answer == '':
            result = default
        if result is None:
            print('Sorry, I didn\'t understand.')
    return result


def _hcenter(word, width):
    """Add spaces before and after word to get to the given width."""
    left = width - len(word)
    after = before = ' ' * (left // 2)
    if left % 2:
        after += ' '
    return f'{before}{word}{after}'
