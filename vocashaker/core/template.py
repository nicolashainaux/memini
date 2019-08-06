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

from vocashaker.core.env import USER_TEMPLATES_PATH, TEMPLATE_EXT


def exists(table_name):
    """Tell if the template matching table_name does exist."""
    template_path = os.path.join(USER_TEMPLATES_PATH,
                                 '{}.{}'.format(table_name, TEMPLATE_EXT))
    return os.path.isfile(template_path)


def _prepare_content(table_name):
    """Prepare the temporary content.xml matching table_name."""


def create(table_name):
    """Create the template (.odt) file."""
