#!/usr/bin/env python
# coding=utf-8

# Copyright (C) 2014 by Serge Poltavski                                 #
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

from .abstractvisitor import AbstractVisitor
from .baseobject import *
from .obj import PdObject
from ..pdpainter import PdPainter


class Comment(BaseObject):
    def __init__(self, x: int, y: int, args: list[str], width: int = 0):
        super(Comment, self).__init__("", x, y, 0, 0)
        self.args = []
        self._line_width = width

        for a in args:
            if a:
                self.args.append(a.strip())

    @staticmethod
    def unescape(s: str):
        return s.strip() \
            .replace(chr(13), "") \
            .replace(chr(10), "") \
            .replace("\\;", ";") \
            .replace("\\,", ",")

    @staticmethod
    def escape(s: str):
        res = ""
        for c in s:
            if c == ';':
                res += " \\; "
            elif c == ',':
                res += " \\, "
            elif c in (chr(10), chr(13)):
                continue
            else:
                res += c

        return res

    def text(self):
        res = ""

        for a in self.args:
            a = self.unescape(a)

            if a == ",":
                res += ","
            elif a == ";":
                res += ";"
            else:
                res += " " + a

        res = res.strip()

        return res

    def __str__(self):
        res = "# %-39s {x:%i,y:%i}, f %i" % (self.text(), self._x, self._y, self._line_width)
        return res

    def draw(self, painter: PdPainter):
        painter.draw_comment(self)

    def traverse(self, visitor: AbstractVisitor):
        if visitor.skip_comment(self):
            return

        visitor.visit_comment(self)

    def calc_brect(self):
        brect = PdObject.brect_calc().comment_brect(self)
        self._width = brect[2]
        self._height = brect[3]

    def line_width(self):
        return self._line_width
