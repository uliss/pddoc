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

from .baseobject import *
from .abstractvisitor import AbstractVisitor
from .obj import PdObject


class Comment(BaseObject):
    def __init__(self, x, y, args):
        super(Comment, self).__init__(x, y, 0, 0)
        self.args = args

    @staticmethod
    def unescape(s):
        return s.strip() \
            .replace(chr(13), "") \
            .replace(chr(10), "") \
            .replace("\\;", ";") \
            .replace("\\,", ",")

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
        res = "# %-39s {x:%i,y:%i}" % (self.text(), self._x, self._y)
        return res

    def draw(self, painter):
        painter.draw_comment(self)

    def traverse(self, visitor):
        assert isinstance(visitor, AbstractVisitor)

        if visitor.skip_comment(self):
            return

        visitor.visit_comment(self)

    def calc_brect(self):
        brect = PdObject.brect_calc().comment_brect(self)
        self._width = brect[2]
        self._height = brect[3]
