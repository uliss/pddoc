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
from copy import deepcopy
from pd.externals.pddp.pddplink import PddpLink


class LibraryParser(object):
    WINDOW_WIDTH = 600
    WINDOW_HEIGHT = 500
    HEADER_BG_COLOR = Color(100, 100, 100)
    HEADER_TXT_COLOR = Color(0, 255, 255)
    HEADER_HEIGHT = 40
    HEADER_FONT_SIZE = 20
    FOOTER_HEIGHT = 40
    FOOTER_BG_COLOR = Color(200, 200, 200)

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
        self._current_y = self.HEADER_HEIGHT + 10
        self._pd_cats = {}

    def lib_name(self):
        return self._lib_name

    def process(self):
        self._xml = etree.parse(self._fname)
        self._xml.xinclude()
        self._root = self._xml.getroot()
        self.process_xml()
        self.add_header()

    def process_xml(self):
        self._lib_name = self._root.get("name")
        PdObject.xlet_calculator.add_db(self._lib_name + ".db")

        # get version
        version = self._root.find("meta/version")
        if version is not None:
            self._lib_version = version.text
        else:
            self._lib_version = "0.0"

        # general info
        lib_descr = self._root.find("meta/library-info/description")
        if lib_descr is not None:
            descr = self.add_text(20, self._current_y, lib_descr.text)
            descr.calc_brect()

            self._current_y += descr.height + 10

        # process categories
        cats = self._root.findall("category")
        for c in cats:
            cat_name = c.get('name')
            self.add_category_section(self._current_y, cat_name)
            entries = c.findall('entry')
            for e in entries:
                self.add_object_description(e, cat_name)

    def add_object_description(self, obj, cat_name):
        pdobj = make_by_name(obj.get('name'))
        pdobj.calc_brect()
        pdobj.x = 20
        pdobj.y = self._current_y
        self._cnv.append_object(pdobj)
        t1 = self.add_text(150, self._current_y, obj.get('descr'))
        t1.calc_brect()
        self._current_y += max(t1.height, pdobj.height) + 10

        self._pd_cats[cat_name].append(pdobj)
        self._pd_cats[cat_name].append(t1)

    def __str__(self):
        pd_exporter = PdExporter()
        self._cnv.traverse(pd_exporter)
        return '\n'.join(pd_exporter.result[:-1])

    def add_header(self):
        cnv = GCanvas(1, 1, width=self.WINDOW_WIDTH - 3, height=self.HEADER_HEIGHT,
                      label="{0}({1})".format(self._lib_name, self._lib_version),
                      font_size=self.HEADER_FONT_SIZE,
                      label_xoff=20, label_yoff=20)
        cnv._bg_color = self.HEADER_BG_COLOR
        cnv._label_color = self.HEADER_TXT_COLOR
        self._cnv.append_object(cnv)

    def add_category_section(self, y, txt):
        lbl = GCanvas(20, y + 10, width=100, height=20, size=10, label=txt, font_size=14)
        lbl._label_color = Color(50, 50, 50)
        self._cnv.append_object(lbl)
        self._current_y += 30
        self.add_delimiter(self._current_y)
        self._current_y += 20

        # add new entry in category dict
        self._pd_cats[txt] = []

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

    def process_categories(self):
        for name in sorted(self._pd_cats.keys()):
            info = ""
            cat_xml = self._root.find("category[@name='{0}']/category-info".format(name))
            if cat_xml is not None:
                info = cat_xml.text

            data = self.generate_category(name, info)
            fname = "{0}.{1}-help.pd".format(self._lib_name, name)
            with open(fname, "w") as f:
                f.write(data)

    def generate_category(self, name, descr):
        if len(self._pd_cats[name]) < 1:
            return

        pd_cat = Canvas(0, 0, self.WINDOW_WIDTH, self.WINDOW_HEIGHT)
        pd_cat.type = Canvas.TYPE_WINDOW

        # category doc header
        cnv = GCanvas(1, 1,
                      width=self.WINDOW_WIDTH - 3,
                      height=self.HEADER_HEIGHT,
                      label="{0}::{1}".format(self.lib_name(), name),
                      font_size=self.HEADER_FONT_SIZE,
                      label_xoff=20,
                      label_yoff=20)
        cnv._bg_color = self.HEADER_BG_COLOR
        cnv._label_color = self.HEADER_TXT_COLOR
        pd_cat.append_object(cnv)

        y_off = self.HEADER_HEIGHT + 10
        # category doc description
        if descr:
            info = Comment(20, y_off, descr.split(' '))
            pd_cat.append_object(info)
            y_off += 25

            # delimiter
            hrule = self.make_delimeter(y_off)
            pd_cat.append_object(hrule)
            y_off += 15

        # category doc objects
        y_off = self._pd_cats[name][0].y - y_off
        last_obj_y = y_off
        for o in self._pd_cats[name]:
            cat_obj = deepcopy(o)
            cat_obj.y -= y_off
            last_obj_y = cat_obj.y
            pd_cat.append_object(cat_obj)

        # category footer
        footer_y = max(self.WINDOW_HEIGHT, last_obj_y) - self.FOOTER_HEIGHT - 2
        ft_bg = GCanvas(1, footer_y, width=self.WINDOW_WIDTH - 3, height=self.FOOTER_HEIGHT)
        ft_bg._bg_color = self.FOOTER_BG_COLOR
        pd_cat.append_object(ft_bg)
        label1 = self.make_txt(20, footer_y + 2, "library: ")
        pd_cat.append_object(label1)
        lib_lnk = PddpLink(80, footer_y + 2, "{0}-help.pd".format(self.lib_name()), self.lib_name())
        pd_cat.append_object(lib_lnk)
        label2 = self.make_txt(20, footer_y + 20, "version: {0}".format(self._lib_version))
        pd_cat.append_object(label2)

        pd_exporter = PdExporter()
        pd_cat.traverse(pd_exporter)
        return '\n'.join(pd_exporter.result[:-1])
