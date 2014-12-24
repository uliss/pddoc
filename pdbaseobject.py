#!/usr/bin/env python

#   Copyright (C) 2014 by Serge Poltavski                                 #
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
import re


class PdBaseObject(object):
    brect_calculator = None
    XLET_MESSAGE, XLET_SOUND, XLET_GUI = range(0, 3)

    def __init__(self, x=0, y=0, w=0, h=0):
        self._x = int(x)
        self._y = int(y)
        self._height = int(h)
        self._width = int(w)

    x = property(lambda c: c.get_x(), lambda c, v: c.set_x(v))
    y = property(lambda c: c.get_y(), lambda c, v: c.set_y(v))
    height = property(lambda c: c.get_height(), lambda c, v: c.set_height(v))
    width = property(lambda c: c.get_width(), lambda c, v: c.set_width(v))

    def is_null(self):
        return not self.x and not self.y and not self.width and not self.height

    def brect(self):
        return (self.x, self.y, self.width, self.height)

    def move_by(self, x, y):
        self.x += x
        self.y += y

    @property
    def top(self):
        return self.y

    @property
    def bottom(self):
        return self.y + self.height

    @property
    def left(self):
        return self.x

    @property
    def right(self):
        return self.x + self.width

    def get_x(self):
        return self._x

    def set_x(self, x):
        self._x = int(x)

    def get_y(self):
        return self._y

    def set_y(self, y):
        self._y = int(y)

    def get_height(self):
        return self._height

    def set_height(self, h):
        self._height = int(h)

    def get_width(self):
        return self._width

    def set_width(self, w):
        self._width = int(w)

    def draw(self, painter):
        assert not "Not implemented"

    def inlets(self):
        return ()

    def outlets(self):
        return ()

    def traverse(self, visitor):
        assert not "Not implemented"

    def calc_brect(self):
        self.brect_calculator.calc(self)

    @staticmethod
    def unescape(string):
        return re.sub(r'\\(.)', r'\1', string)
