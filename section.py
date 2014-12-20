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

import common


class Container(object):
    allowed_tags = ()
    def __init__(self):
        self._xml = None
        self._elements = []
        self._text = ""

    def add_child(self, child):
        self._elements.append(child)

    def from_xml(self, element):
        pass

    def clear(self):
        self._elements = []


class Para(Container):
    def from_xml(self, para):
        self._xml = para
        self._text = para.text


class Inlets(Container):
    pass


class Outlets(Container):
    pass


class Arguments(Container):
    pass


class Inlet(Container):
    pass


class Caution(Container):
    pass


class Table(Container):
    pass


class Pdexample(Container):
    pass


class Section(Container):
    allowed_tags = ("para", "table", "pdexample", "caution", "inlet")

    def __init__(self):
        self._title = ""
        self._elements = []
        self._xml = None

    def from_xml(self, element):
        self._xml = element

        if element.attrib.has_key("title"):
            self._title = element.attrib["title"]

        for child in element:
            if child.tag not in self.allowed_tags:
                common.warning("tag not allowed in %s: %s" % (element.tag, child.tag))

            klass = globals()[child.tag.capitalize()]
            obj = klass()
            obj.from_xml(child)
            self.add_child(obj)


