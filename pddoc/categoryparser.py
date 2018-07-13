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
from .pd.factory import make_by_name
from .pdpage import PdPage
import logging


class CategoryParser(object):
    WINDOW_WIDTH = 715
    WINDOW_HEIGHT = 500
    HEADER_HEIGHT = 40
    OBJECT_OFFSET = 30
    DESCRIPTION_OFFSET = 175

    def __init__(self, fname):
        self._fname = fname
        self._xml = None
        self._root = None
        self._cat = None
        self._cat_name = ""
        self._lib_name = ""
        self._current_y = 0
        self._pp = None

    def process(self):
        self._xml = etree.parse(self._fname)
        self._xml.xinclude()
        self._root = self._xml.getroot()
        self._lib_name = self._root.get("name")
        self.process_xml()

    def process_xml(self):
        for c in self._root.findall("category"):
            self.process_xml_category(c)

    def process_xml_category(self, c):
        self._cat = c
        self._cat_name = c.get('name')
        self._current_y = self.HEADER_HEIGHT + 10
        self._pp = PdPage("cat", self.WINDOW_WIDTH, self.WINDOW_HEIGHT)
        self.add_menubar()
        self.add_info()
        self.process_xml_category_entries()
        self.add_header()
        self.add_footer()
        self.save()
        del self._pp
        self._pp = None

    def add_info(self):
        info = self._cat.find("category-info")
        if info is not None:
            self._pp.add_description(info.text, self.HEADER_HEIGHT + 10)

    def add_menubar(self):
        l1 = self._pp.make_link(0, self._current_y, "../index-help.pd", "index")
        l2 = self._pp.make_link(0, self._current_y,
                                "{0}-help.pd".format(self._lib_name),
                                "{0}".format(self._lib_name))
        delim = self._pp.make_txt("::", 0, self._current_y)
        menu = [l1, delim, l2]
        self._pp.place_in_row(menu, 20, 8)
        self._pp.append_list(menu)
        br = self._pp.group_brect(menu)
        self._current_y += br[1] + br[3]

    def process_xml_category_entries(self):
        for e in self._cat.findall('entry'):
            self.add_object_description(e)

    def add_object_description(self, obj):
        pdobj = make_by_name(obj.get('name'))
        pdobj.x = self.OBJECT_OFFSET
        pdobj.y = self._current_y

        ref_view = obj.get('ref_view', 'object')
        if ref_view == 'object':
            self._pp.append_object(pdobj)
        elif ref_view == 'link':
            name = format(obj.get('name'))
            help_file = '{0}-help.pd'.format(name)
            link_text = '[{0}]'.format(name)
            self._pp.add_link(link_text, help_file, self.OBJECT_OFFSET, self._current_y)

        info = self._pp.add_txt(obj.get('descr'), self.DESCRIPTION_OFFSET, self._current_y)
        self._current_y += max(info.height, pdobj.height) + 10

    def save(self):
        fname = "{0}.{1}-help.pd".format(self._lib_name, self._cat_name)
        with open(fname, "w") as f:
            f.write(self._pp.to_string())
            logging.info("{0} created".format(fname))

    def add_header(self):
        title = "{0}::{1}".format(self._lib_name, self._cat_name)
        h = self._pp.add_header(title)
        return h

    def add_footer(self):
        f = self._pp.make_footer(self._current_y)
        self._pp.append_object(f)

        info = self._pp.make_txt("library: {0}".format(self._lib_name), 20, f.top + 10)
        self._pp.append_object(info)
        return f
