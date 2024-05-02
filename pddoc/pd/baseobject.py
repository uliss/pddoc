#!/usr/bin/env python
# coding=utf-8

#   Copyright (C) 2014 by Serge Poltavski                                 #
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

import re


class BaseObject(object):
    def __init__(self, name: str, x: int = 0, y: int = 0, w: int = 0, h: int = 0):
        self._id = -1
        self._x = x
        self._y = y
        self._height = h
        self._width = w
        self._name = name

    def is_null(self):
        return not self.x and not self.y and not self.width and not self.height

    def brect(self):
        return self.x, self.y, self.width, self.height

    def move_by(self, x, y):
        self.x += x
        self.y += y

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, n: str):
        assert len(n) > 0
        self._name = n

    @property
    def x(self) -> int:
        return int(self._x)

    @x.setter
    def x(self, x: int):
        self._x = x

    @property
    def y(self) -> int:
        return int(self._y)

    @y.setter
    def y(self, y: int):
        self._y = y

    @property
    def height(self) -> int:
        return self._height

    @height.setter
    def height(self, h: int):
        self._height = h

    @property
    def width(self) -> int:
        return self._width

    @width.setter
    def width(self, w: int):
        self._width = w

    @property
    def top(self) -> int:
        return self.y

    @property
    def bottom(self) -> int:
        return self.y + self.height

    @property
    def left(self) -> int:
        return self.x

    @property
    def right(self) -> int:
        return self.x + self.width

    def get_height(self) -> int:
        return self._height

    def set_height(self, h: float):
        self._height = int(h)

    def get_width(self) -> int:
        return self._width

    def set_width(self, w: float):
        self._width = int(w)

    def draw(self, painter):
        assert not "Not implemented"

    def draw_on_parent(self):
        return False

    def inlets(self):
        return ()

    def outlets(self):
        return ()

    def traverse(self, visitor):
        assert not "Not implemented"

    @staticmethod
    def unescape(string):
        return re.sub(r'\\(.)', r'\1', string)

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, oid):
        self._id = int(oid)
