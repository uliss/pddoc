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

from .docobject import DocPdascii
from .idocobjectvisitor import IDocObjectVisitor
from .txt.parser import Parser


class ListObjectVisitor(IDocObjectVisitor):
    def render(self):
        pass

    def __init__(self):
        IDocObjectVisitor.__init__(self)
        self._pdascii = None

    def alias_begin(self, a):
        print(a.text())

    def pdascii_begin(self, pdascii: DocPdascii):
        self._pdascii = pdascii.text()

        p = Parser()
        if not p.parse(self._pdascii):
            logging.info("<pdascii> parse failed: {0}".format(self._pdascii))

        for n in filter(lambda x: x.is_object() and x.pd_object is not None and x.type == 'OBJECT', p.nodes):
            print(n.pd_object.to_string())

    def see_begin(self, see):
        print(see.text())
