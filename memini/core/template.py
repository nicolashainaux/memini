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

import os
import re
import glob
import shutil
import zipfile
import subprocess
import xml.etree.ElementTree as ET
from tempfile import NamedTemporaryFile

from memini.core.errors import NotATemplateError
from memini.core.prefs import EDITOR, ENCODING
from memini.core.env import USER_TEMPLATES_PATH, TEMPLATE_EXT, TEMPLATE_DIR
from memini.core.env import CONTENTXML_PATH, DATADIR
from memini.core.database import get_cols


def path(table_name):
    """Return the path to template matching table_name."""
    return os.path.join(USER_TEMPLATES_PATH, f'{table_name}.{TEMPLATE_EXT}')


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
    src = os.path.join(DATADIR, f'content{cols_nb}.xml')
    with open(src, 'r', encoding=ENCODING) as f:
        contentxml = f.read()
    contentxml = contentxml.replace('__TITLE__', table_name)
    for i in range(cols_nb):
        contentxml = contentxml.replace(f'__COL{str(i + 1)}__', cols_titles[i])
    return contentxml


def create(table_name):
    """Create the template (.odt) file."""
    with open(CONTENTXML_PATH, 'w', encoding=ENCODING) as f:
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


def _check(filename):
    """Check the filename is a template file created by me."""
    with zipfile.ZipFile(filename) as z:
        with z.open('meta.xml') as f:
            meta_xml = f.readlines()
    if b'        <meta:initial-creator>memini\n' in meta_xml:
        return True
    else:
        return False


def _LO_saved_content_xml_detected(filename):
    """Check if content contains empty relatorio nodes."""
    tree = ET.parse(filename)
    root = tree.getroot()
    for node in root.findall('.//{*}body/{*}text/{*}table//{*}a'):
        if (node.text is None or not node.text.strip()) and not list(node):
            return True
    return False


def _fix_LO_saved_content_xml(content):
    """Remove empty relatorio nodes from content."""
    output = []
    pattern = re.compile(
        r'<text:a xlink:type="simple" xlink:href="relatorio'
        r'[^<]*?(?<!text:span>)(?<!text:span)[^a-z]</text:a>')
    for line in content:
        try:  # If line is provided as byte-like object, do decode it into str
            line = line.decode()
        except AttributeError:  # If not, keep line as is
            pass
        output.append(pattern.sub('', line))
    return '\n'.join(output)


def get_cols_nb(filename):
    """Find out the number of columns in the provided template."""
    if not _check(filename):
        raise NotATemplateError(filename)
    with zipfile.ZipFile(filename) as z:
        with z.open('content.xml') as f:
            content_xml = f.readlines()
    content_xml = ''.join([str(line.strip()) for line in content_xml])
    if '<text:span text:style-name="T1">row.col4</text:span>' in content_xml:
        return 4
    if '<text:span text:style-name="T1">row.col3</text:span>' in content_xml:
        return 3
    if '<text:span text:style-name="T1">row.col2</text:span>' in content_xml:
        return 2
    raise NotATemplateError(filename)


def sanitize(filename):
    """Remove empty relatorio nodes from template, if any."""
    updated = False
    with NamedTemporaryFile() as tmp_file:
        tmpname = os.path.basename(tmp_file.name)
        with zipfile.ZipFile(filename, 'r') as zin:
            with zin.open('content.xml') as f:
                if _LO_saved_content_xml_detected(f):
                    f.seek(0)
                    updated = True
                    # Create a temp copy of the template without content.xml
                    with zipfile.ZipFile(tmpname, 'w') as zout:
                        zout.comment = zin.comment  # preserve the comment
                        for item in zin.infolist():
                            if item.filename != 'content.xml':
                                zout.writestr(item, zin.read(item.filename))
                    # Now create and add the new content.xml
                    f.seek(0)
                    new_content = _fix_LO_saved_content_xml(f.readlines())
                    with zipfile.ZipFile(tmpname, 'a',
                                         zipfile.ZIP_DEFLATED) as zf:
                        zf.writestr('content.xml', new_content)
        if updated:
            # Replace with the temp archive
            os.remove(filename)
            shutil.copyfile(tmpname, filename)
    return updated
