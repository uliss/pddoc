#!/usr/bin/env python
# coding=utf-8
#   Copyright (C) 2016 by Serge Poltavski                                 #
#   serge.poltavski@gmail.com                                             #
#                                                                         #
#   This program is free software; you can redistribute it and/or modify  #
#   it under the terms of the GNU General Public License as published by  #
#   the Free Software Foundation; either version 3 of the License, or     #
#   (at your option) any later version.                                   #
#                                                                         #
#   This program is distributed in the hope that it will be useful,       #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of        #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         #
#   GNU General Public License for more details.                          #
#                                                                         #
#   You should have received a copy of the GNU General Public License     #
#   along with this program. If not, see <http://www.gnu.org/licenses/>   #

from lxml import etree
from pd.canvas import Canvas
from pd.pdexporter import PdExporter
from pd.gcanvas import GCanvas
from pd.coregui import Color
import re
from pd.comment import Comment
from pd.factory import make_by_name
from pd.obj import PdObject


class LibraryParser(object):
    WINDOW_WIDTH = 600
    WINDOW_HEIGHT = 500

    def __init__(self, fname):
        self._fname = fname
        self._xml = None
        self._root = None
        self._cnv = Canvas(0, 0, self.WINDOW_WIDTH, self.WINDOW_HEIGHT)
        self._cnv.type = Canvas.TYPE_WINDOW
        self._lib_name = ""
        self._lib_version = ""
        self._lib_authors = []
        self._lib_license = ""
        self._lib_website = ""
        self._lib_contacts = ""
        self._lib_info = ""
        self._current_y = 60

    def lib_name(self):
        return self._lib_name

    def process(self):
        self._xml = etree.parse(self._fname)
        self._root = self._xml.getroot()
        self.process_xml()
        self.add_header()

    def process_xml(self):
        self._lib_name = self._root.get("name")
        PdObject.xlet_calculator.add_db(self._lib_name + ".db")

        self._lib_version = self._root.get("version")

        cats = self._root.findall("category")
        for c in cats:
            self.add_category_section(self._current_y, c.get('name'))
            entries = c.findall('entry')
            for e in entries:
                self.add_object_description(e)

    def add_object_description(self, obj):
        pdobj = make_by_name(obj.get('name'))
        pdobj.calc_brect()
        pdobj.x = 20
        pdobj.y = self._current_y
        self._cnv.append_object(pdobj)
        t1 = self.add_text(150, self._current_y, obj.get('descr'))
        t1.calc_brect()
        self._current_y += max(t1.height, pdobj.height) + 10

    def __str__(self):
        pd_exporter = PdExporter()
        self._cnv.traverse(pd_exporter)
        return '\n'.join(pd_exporter.result[:-1])

    def add_header(self):
        cnv = GCanvas(1, 1, width=self.WINDOW_WIDTH - 3, height=60,
                      label="library:{0}".format(self._lib_name.upper()), font_size=20,
                      label_xoff=20, label_yoff=20)
        cnv._bg_color = Color(100, 100, 100)
        cnv._label_color = Color(0, 255, 255)
        self._cnv.append_object(cnv)

    def add_category_section(self, y, txt):
        lbl = GCanvas(20, y + 10, width=100, height=20, size=10, label=txt, font_size=14)
        lbl._label_color = Color(50, 50, 50)
        self._cnv.append_object(lbl)
        self._current_y += 30
        self.add_delimiter(self._current_y)
        self._current_y += 20

    def make_delimeter(self, y, **kwargs):
        delim = GCanvas(20, y, width=self.WINDOW_WIDTH - 24, height=1, size=1)
        delim._bg_color = Color(200, 200, 200)
        return delim

    def add_delimiter(self, y, **kwargs):
        obj = self.make_delimeter(y)
        self._cnv.append_object(obj)
        return obj

    def make_txt(self, x, y, txt):
        txt = re.sub(' +', ' ', txt)
        txt = txt.replace('.', '\\.')
        txt = txt.replace(',', ' \\,')
        return Comment(x, y, txt.split(' '))

    def add_text(self, x, y, txt):
        obj = self.make_txt(x, y, txt)
        self._cnv.append_object(obj)
        return obj
