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
import glob
import shutil
import subprocess

from vocashaker.core.prefs import EDITOR
from vocashaker.core.env import USER_TEMPLATES_PATH, TEMPLATE_EXT, TEMPLATE_DIR
from vocashaker.core.env import CONTENTXML_PATH, DATADIR
from vocashaker.core.database import get_cols


def path(table_name):
    """Return the path to template matching table_name."""
    return os.path.join(USER_TEMPLATES_PATH,
                        '{}.{}'.format(table_name, TEMPLATE_EXT))


def list_():
    """List all known templates."""
    return [os.path.basename(p) for p in glob.glob(path('*'))]


def exists(table_name):
    """Tell if the template matching table_name does exist."""
    return os.path.isfile(path(table_name))


def _prepare_content(table_name):
    """Return the content of content.xml to write, matching table_name."""
    cols_titles = get_cols(table_name)
    cols_nb = len(cols_titles)
    src = os.path.join(DATADIR, 'content{}.xml'.format(cols_nb))
    with open(src, 'r') as f:
        contentxml = f.read()
    contentxml = contentxml.replace('__TITLE__', table_name)
    for i in range(cols_nb):
        contentxml = contentxml.replace('__COL{}__'.format(str(i + 1)),
                                        cols_titles[i])
    return contentxml


def create(table_name):
    """Create the template (.odt) file."""
    with open(CONTENTXML_PATH, 'w') as f:
        f.write(_prepare_content(table_name))
    zipped = shutil.make_archive(table_name, 'zip', TEMPLATE_DIR)
    shutil.move(zipped, path(table_name))
    os.remove(CONTENTXML_PATH)


def edit(table_name):
    """Run the editor on table_name's template."""
    _ = subprocess.Popen([EDITOR, path(table_name)])


def remove(table_name):
    """Remove the template (.odt) file."""
    os.remove(path(table_name))
