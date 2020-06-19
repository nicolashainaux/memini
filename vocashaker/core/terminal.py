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
    spaces = width - len(word)
    after = before = ' ' * (spaces // 2)
    if spaces % 2:
        before += ' '
    return f'{before}{word}{after}'


def tabulate(rows, vsep=None, hsep=None, isep=None):
    """Tabulate the given rows. First row is assumed to contain the headers."""
    if vsep is None:
        vsep = '|'
    if hsep is None:
        hsep = '-'
    if isep is None:
        isep = '+'
    cols = []
    for i, _ in enumerate(rows[0]):
        cols.append([rows[j][i] for j in range(len(rows))])
    widths = []
    for col in cols:
        widths.append(max({len(word) for word in col}) + 2)
    headers = vsep.join([_hcenter(word, width)
                         for (word, width) in zip(rows[0], widths)])
    ruler = isep.join([hsep * w for w in widths])
    content = []
    for r in rows[1:]:
        content.append(vsep.join([_hcenter(word, width)
                                  for (word, width) in zip(r, widths)]))
    table = [headers, ruler, *content]
    return '\n'.join(table)
