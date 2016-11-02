#!/usr/bin/env python
# coding=utf-8
import copy

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

__author__ = 'Serge Poltavski'


class LayoutItem(object):
    def __init__(self, x=0, y=0, width=0, height=0):
        self._x = x
        self._y = y
        self._w = width
        self._h = height

    def x(self):
        return self._x

    def y(self):
        return self._y

    def width(self):
        return self._w

    def height(self):
        return self._h

    def brect(self):
        return self._x, self._y, self._w, self._h

    def __str__(self):
        return "(%i,%i,%ix%i)" % (self._x, self._y, self._w, self._h)

    def right(self):
        return self._x + self._w

    def bottom(self):
        return self._y + self._h

    def top(self):
        return self._y

    def left(self):
        return self._x

    def move_by(self, x, y):
        self._x += x
        self._y += y


class Layout(object):
    HORIZONTAL, VERTICAL = range(1, 3)

    def __init__(self, direction, distance=0):
        self._parent = None
        self._elements = []
        self._dir = direction
        self._distance = distance

    @staticmethod
    def vertical(distance=0):
        return Layout(Layout.VERTICAL, distance)

    @staticmethod
    def horizontal(distance=0):
        return Layout(Layout.HORIZONTAL, distance)

    def is_vertical(self):
        return self._dir == Layout.VERTICAL

    def is_horizontal(self):
        return self._dir == Layout.HORIZONTAL

    def parent(self):
        return self._parent

    def set_parent(self, parent):
        self._parent = parent

    def count(self):
        return len(self._elements)

    def _add_vertical(self, item):
        if self.count() > 0:
            prev_item = self._elements[-1]
            item.move_by(0, prev_item.bottom() + self._distance)

        self._elements.append(item)

    def _add_horizontal(self, item):
        if self.count() > 0:
            prev_item = self._elements[-1]
            item.move_by(prev_item.right() + self._distance, 0)

        self._elements.append(item)

    def add_item(self, item):
        assert item != self

        if item in self._elements:
            item2 = copy.copy(item)
            return self.add_item(item2)

        assert isinstance(item, LayoutItem)
        if self._dir == self.HORIZONTAL:
            self._add_horizontal(item)
        elif self._dir == self.VERTICAL:
            self._add_vertical(item)
        else:
            assert False

    def pop_item(self):
        return self._elements.pop()

    def add_layout(self, layout):
        assert layout != self

        if layout in self._elements:
            layout2 = copy.deepcopy(layout)
            return self.add_layout(layout2)

        if self.count() > 0:
            prev_item = self._elements[-1]

            if self._dir == self.HORIZONTAL:
                layout.move_by(prev_item.right() + self._distance, 0)
            elif self._dir == self.VERTICAL:
                layout.move_by(0, prev_item.bottom() + self._distance)
            else:
                assert False

        self._elements.append(layout)

    def item(self, num):
        assert num < len(self._elements)
        return self._elements[num]

    def brect(self):
        if self.count() == 0:
            return 0, 0, 0, 0

        left = []
        top = []
        right = []
        bottom = []

        for item in self._elements:
            br = item.brect()
            left.append(br[0])
            top.append(br[1])
            right.append(br[0] + br[2])
            bottom.append(br[1] + br[3])

        x0 = min(left)
        y0 = min(top)
        x1 = max(right)
        y1 = max(bottom)
        return x0, y0, x1 - x0, y1 - y0

    def x(self):
        return self.brect()[0]

    def y(self):
        return self.brect()[1]

    def width(self):
        return self.brect()[2]

    def height(self):
        return self.brect()[3]

    def top(self):
        return self.y()

    def left(self):
        return self.x()

    def bottom(self):
        br = self.brect()
        return br[1] + br[3]

    def right(self):
        br = self.brect()
        return br[0] + br[2]

    def move_by(self, x, y):
        for item in self._elements:
            item.move_by(x, y)

    def __str__(self):
        res = ""
        if self._dir == self.HORIZONTAL:
            s = ""
            for item in self._elements:
                s += "[%i:%ix%i] " % (item.x(), item.width(), item.height())

            s = s.strip()
            res += "-" * (len(s) + 4)
            res += "\n| {0:s} |\n".format(s)
            res += "-" * (len(s) + 4)
        elif self._dir == self.VERTICAL:
            col_len = 0
            els = []
            for item in self._elements:
                els.append("[%i:%ix%i]" % (item.y(), item.width(), item.height()))
                col_len = max(col_len, len(els[-1]))

            res += "-" * (col_len + 4)
            res += "\n"
            fmt = "| %{0:d}s |\n".format(col_len)
            for e in els:
                res += fmt % (e)
            res += "-" * (col_len + 4)

        return res
