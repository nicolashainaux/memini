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

import shutil
from textwrap import wrap
from itertools import zip_longest

from .prefs import TERMINAL_SIZE_FALLBACK


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
        answer = input(f'{question} {yn} ')
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


def _allocate_widths(widths):
    """
    Allocate space in a "smart" way if the total required width is larger
    than the terminal's.
    """
    term_width = shutil.get_terminal_size(TERMINAL_SIZE_FALLBACK).columns
    cols_nb = len(widths)
    if sum(widths) >= term_width:
        # The text to tabulate is larger than the terminal:
        # Width available for each column if we allocate it equally:
        mean_width = term_width // cols_nb
        # Width left for larger cols if we remove the narrower ones
        # (larger being larger than the mean; narrower, narrower than the mean)
        width_narrower = sum([w for w in widths if w < mean_width])
        left_for_larger = term_width - width_narrower - 1
        nb_of_larger = len([w for w in widths if w >= mean_width])
        width_larger = left_for_larger // nb_of_larger
        # Now replace the widths of the larger ones by width_larger
        widths = [w if w < mean_width else width_larger for w in widths]
    return widths


def _expand_rows(rows, widths):
    """Expand each row that contains too wide text in several rows."""
    result = []
    for row in rows:
        new_rows = []
        texts = []
        for i, text in enumerate(row):
            texts.append(wrap(text, widths[i]))
        for new_row in zip_longest(*texts, fillvalue=''):
            new_rows.append(new_row)
        for row in new_rows:
            result.append(row)
    return result


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
        widths.append(max({len(text) for text in col}) + 2)
    widths = _allocate_widths(widths)
    rows = _expand_rows(rows, widths)
    headers = vsep.join([_hcenter(text, width)
                         for (text, width) in zip(rows[0], widths)])
    ruler = isep.join([hsep * w for w in widths])
    content = []
    for r in rows[1:]:
        content.append(vsep.join([_hcenter(text, width)
                                  for (text, width) in zip(r, widths)]))
    table = [headers, ruler, *content]
    return '\n'.join(table)
