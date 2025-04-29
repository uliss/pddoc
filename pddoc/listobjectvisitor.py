#!/usr/bin/env python
# coding=utf-8

#   Copyright (C) 2015 by Serge Poltavski                                 #
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

__author__ = 'Serge Poltavski'

import logging

from .docobject import DocPdascii, DocAlias, DocSee, DocMethod, DocProperty
from .idocobjectvisitor import IDocObjectVisitor
from .txt.parser import Parser


class ListObjectVisitor(IDocObjectVisitor):
    def render(self):
        pass

    def __init__(self,
                 show_objects: bool = False,
                 show_aliases: bool = False,
                 show_methods: bool = False,
                 show_properties: bool = False):

        IDocObjectVisitor.__init__(self)

        self._pdascii = None
        self._show_objects = show_objects
        self._show_aliases = show_aliases
        self._show_properties = show_properties
        self._show_methods = show_methods

        self._objects: set[str] = set()
        self._methods: set[str] = set()
        self._properties: set[str] = set()

    def __str__(self):
        if self._show_objects or self._show_aliases:
            return '\n'.join(sorted(self._objects))

        if self._show_methods:
            return '\n'.join(sorted(self._methods))

        if self._show_properties:
            return '\n'.join(sorted(self._properties))

        return ''

    def alias_begin(self, a: DocAlias):
        if self._show_objects or self._show_aliases:
            self._objects.add(a.text())

    def method_begin(self, m: DocMethod):
        if self._show_methods:
            self._methods.add(m.name())

    def property_begin(self, p: DocProperty):
        if self._show_properties:
            self._properties.add(p.name())

    def pdascii_begin(self, pdascii: DocPdascii):
        if not self._show_objects:
            return

        self._pdascii = pdascii.text()

        p = Parser()
        if not p.parse(self._pdascii):
            logging.info("<pdascii> parse failed: {0}".format(self._pdascii))

        for n in filter(lambda x: x.is_object() and x.pd_object is not None and x.type == 'OBJECT', p.nodes):
            self._objects.add(n.pd_object.to_string())

    def see_begin(self, see: DocSee):
        if self._show_objects:
            self._objects.add(see.text())
