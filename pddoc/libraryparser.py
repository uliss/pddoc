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
from .pd.obj import PdObject
from .pdpage import PdPage


class LibraryParser(object):
    WINDOW_WIDTH = 715
    WINDOW_HEIGHT = 500
    HEADER_HEIGHT = 40
    OBJECT_OFFSET = 30
    DESCRIPTION_OFFSET = 175

    def __init__(self, fname):
        self._fname = fname
        self._xml = None
        self._root = None
        self._lib_name = ""
        self._lib_version = ""
        self._lib_authors = []
        self._lib_license = ""
        self._lib_website = ""
        self._lib_contacts = ""
        self._lib_info = ""
        self._current_y = self.HEADER_HEIGHT + 10
        self._pd_cats = {}
        self._pp = PdPage("lib", self.WINDOW_WIDTH, self.WINDOW_HEIGHT)

    def lib_name(self):
        return self._lib_name

    def process(self):
        self._xml = etree.parse(self._fname)
        self._xml.xinclude()
        self._root = self._xml.getroot()
        self.process_xml()
        self.add_header()
        self.add_footer()

    def process_xml(self):
        self.get_meta()
        # order matters! add_xlet_db() should called after get_meta()
        self.add_xlet_db()
        self.add_lib_description()
        self.process_xml_categories()

    def get_meta(self):
        self.get_lib_name()
        self.get_lib_version()
        self.get_lib_website()
        self.get_lib_license()

    def process_xml_categories(self):
        for c in self._root.findall("category"):
            self.process_xml_category(c)

    def process_xml_category(self, c):
        self.add_category_section(self._current_y, c.get('name'))
        self.process_xml_category_entries(c)

    def process_xml_category_entries(self, c):
        cat_name = c.get('name')
        for e in c.findall('entry'):
            self.add_object_description(e, cat_name)

    def add_xlet_db(self):
        PdObject.xlet_calculator.add_db(self._lib_name + ".db")

    def get_lib_name(self):
        self._lib_name = self._root.get("name")

    def get_lib_version(self):
        version = self._root.find("meta/version")
        if version is not None:
            self._lib_version = version.text
        else:
            self._lib_version = "0.0"

    def get_lib_website(self):
        el = self._root.find("meta/library-info/website")
        if el is not None:
            self._lib_website = el.text

    def get_lib_license(self):
        el = self._root.find("meta/library-info/license")
        if el is not None:
            self._lib_license = el.text

    def add_lib_description(self):
        lib_descr = self._root.find("meta/library-info/description")
        if lib_descr is not None:
            descr = self._pp.add_txt(lib_descr.text, self.OBJECT_OFFSET, self._current_y)
            self._current_y += descr.height + 10

    def add_object_description(self, obj, cat_name):
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

        self._pd_cats[cat_name].append(pdobj)
        self._pd_cats[cat_name].append(info)

    def __str__(self):
        return self._pp.to_string()

    def add_header(self):
        title = "{0}".format(self._lib_name)
        h = self._pp.add_header(title)
        return h

    def add_footer(self):
        f = self._pp.make_footer(self._current_y)
        self._pp.append_object(f)

        info = self._pp.make_txt("version: v{0}, license: {1}".format(
            self._lib_version, self._lib_license), 20, f.top)
        self._pp.append_object(info)

        if self._lib_website:
            lnk = self._pp.make_link(20, f.top + info.height + 3, self._lib_website, self._lib_website)
            self._pp.append_object(lnk)
        return f

    def add_category_section(self, y, txt):
        l, r, brect = self._pp.add_section(txt, y)
        self._current_y = brect[1] + brect[3] + 10
        self._pd_cats[txt] = []
