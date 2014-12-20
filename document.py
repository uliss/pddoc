# /usr/bin/env python

# Copyright (C) 2014 by Serge Poltavski                                 #
#   serge.poltavski@gmail.com                                            #
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


# -*- coding: utf-8 -*-

__author__ = 'Serge Poltavski'

import xml.etree.ElementTree as ET
import os
import common
from section import Section


class Meta(object):
    allowed_tags = ("title", "description", "authors", "author", "date", "license", "contacts")

    def __init__(self):
        self._authors = []
        self._descr = ""
        self._props = {}


    def from_xml(self, xmlobj):
        self._authors = []
        self._props = {}
        self._descr = ""

        for child in xmlobj:
            if child.tag not in self.allowed_tags:
                common.warning("tag not allowed: %s" % (child.tag))
                continue

            if child.tag == "title":
                self._title = child.text
            elif child.tag == "description":
                self._descr = child.text
            elif child.tag == "authors":
                for a in child:
                    self._authors.append(a.text)
            elif child.tag == "date":
                self._props["date"] = child.text
            elif child.tag == "license":
                self._props["license"] = child.text
                if child.attrib.has_key("url"):
                    self._props["license_url"] = child.attrib["url"]
            elif child.tag == "contacts":
                self._props["contacts"] = child.text
            else:
                common.warning("Unknown tag in meta: %s" % (child.tag))


class Document(object):
    allowed_tags = ("object")

    def __init__(self, title, **kwargs):
        self._title = title
        self._props = kwargs
        self._meta = Meta()
        self._sections = []
        self._xml = None
        self._pddoc = None


    def set_title(self, title):
        self._title = title

    def set_description(self, descr):
        self._descr = descr

    def set_author(self, author):
        self._author = author

    def from_xml(self, fname):
        if not os.path.exists(fname):
            common.warning("File not exits: %s" % (fname))
            return False

        self._xml = ET.parse(fname)
        self._pddoc = self._xml.getroot()

        print self._pddoc.attrib

        for child in self._pddoc:
            if child.tag not in self.allowed_tags:
                common.warning("tag not allowed in \"%s\": <%s>" % (self._pddoc.tag, child.tag))
                continue

            if child.tag == "object":

                self._meta.from_xml(child)
            elif child.tag == "section":
                self.read_section(child)
            elif child.tag == "title":
                self.set_title(child.text)

            else:
                print child.tag

    def read_section(self, section):
        s = Section()
        s.from_xml(section)
        self._sections.append(s)


    def save_to_xml(self, fname):
        pass


if __name__ == '__main__':
    doc = Document("test document")

    doc.from_xml("tests/float.pddoc")

    # print doc