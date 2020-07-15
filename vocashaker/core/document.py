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
import re
import random
import subprocess

from relatorio.templates.opendocument import Template


from vocashaker.core import database, template, terminal, sweepstakes
from vocashaker.core.env import TEMPLATE_EXT
from vocashaker.core.prefs import BLANK_CHAR, FILLED_CHAR, EDITOR, DEFAULT_Q_NB
from vocashaker.core.errors import SchemeSyntaxError, SchemeLogicalError
from vocashaker.core.errors import SchemeColumnsMismatchError
from vocashaker.core.errors import CommandCancelledError, NotFoundError
from vocashaker.core.errors import ColumnsDoNotMatchError


def _default_scheme(n):
    """
    Any column may be blank, only one column won't be blank at each row.
    See _parse_scheme() for scheme description and purpose.
    n is the number of columns.
    For example, for n=2, default will be __1
    For n=3: ___2
    For n=4: ____3
    """
    return '_' * n + str(n - 1)


def _parse_scheme(scheme):
    """
    Check the provided scheme is correct and return the matching distribution.

    The scheme is an information the user provides to tell how many blanks
    there will be in the table, and which columns may be blank.
    Syntax is: one underscore (_) for a column that may be blank. A star (*)
    for a column that will never be blank. And a number to tell how many blanks
    per row there should be.

    Scheme example: "__*1" to tell there will be one blank in one of the two
    first columns, each row. This method should return ([0, 1], 1)
    """
    original_scheme = scheme
    blanks_nb = scheme.count(BLANK_CHAR)
    filled_nb = scheme.count(FILLED_CHAR)
    if scheme[-1].isdigit():
        scheme, blanks_required = scheme[:-1], int(scheme[-1])
    else:
        blanks_required = min(len(scheme) - 1, blanks_nb)
    cols_nb = len(scheme)
    if blanks_nb + filled_nb != cols_nb:
        raise SchemeSyntaxError(scheme)
    elif (blanks_nb == 0 or blanks_required >= cols_nb
          or blanks_required > blanks_nb):
        raise SchemeLogicalError(original_scheme, blanks_nb, cols_nb,
                                 blanks_required)
    return ([m.start() for m in re.finditer(BLANK_CHAR, scheme)],
            blanks_required, cols_nb)


def _process_data(data, scheme=None):
    """Process data retrieved from a table for use with relatorio."""
    cols_nb = len(data[0])
    if scheme is None:
        scheme = _default_scheme(cols_nb)
    possible_blanks, blanks_nb, scheme_cols_nb = _parse_scheme(scheme)
    if cols_nb != scheme_cols_nb:
        raise SchemeColumnsMismatchError(scheme, cols_nb)
    answers = [{f'col{str(i + 1)}': d[i] for i in range(len(d))}
               for d in data]
    rows = []
    for a in answers:
        blanks = random.sample(possible_blanks, blanks_nb)
        line = dict(a)
        for b in blanks:
            line[f'col{str(b + 1)}'] = ''
        rows.append(line)
    result = {'rows': rows, 'answers': answers}
    return result


def generate(table_name, nb=DEFAULT_Q_NB, scheme=None, oldest_prevail=False,
             output=None, force=False, tpl=None, edit_after=True,
             use_previous=False):
    """
    Generate a new document using n data from the table and the matching
    template.
    """
    if use_previous:
        sw_data = sweepstakes.load_sweepstake(int(table_name))
        table_name, rows = sw_data[0], sw_data[1:]
        table_name = table_name[0]
        if len(rows[0]) != len(database.get_cols(table_name)):
            raise ColumnsDoNotMatchError(
                len(database.get_cols(table_name)), len(rows[0]),
                table_name, database.get_cols(table_name),
                sweepstakes._get_sweepstake_name(use_previous))
    if tpl is None:
        tpl_name = table_name
    else:
        if not os.path.isfile(template.path(tpl)):
            raise NotFoundError(f'Cannot find template file: {tpl}')
        tpl_name = tpl
    if output is None:
        output = f'{table_name}.{TEMPLATE_EXT}'
    if os.path.exists(output) and not force:
        overwrite = terminal.ask_yes_no(f'Output file {output} already '
                                        f'exists, overwrite it?')
        if not overwrite:
            raise CommandCancelledError('generate')
    if not use_previous:
        rows = database.draw_rows(table_name, nb,
                                  oldest_prevail=oldest_prevail)
    data = _process_data(rows, scheme=scheme)
    template.sanitize(template.path(tpl_name))
    basic = Template(source='', filepath=template.path(tpl_name))
    basic_generated = basic.generate(o=data).render()
    with open(output, 'wb') as f:
        f.write(basic_generated.getvalue())
    if edit_after:
        edit(output)


def edit(name):
    """Run the editor on provided file, if it exists."""
    if not os.path.isfile(name):
        raise NotFoundError(f'The file "{name}" cannot be found.')
    _ = subprocess.Popen([EDITOR, name])
