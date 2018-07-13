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

from .coregui import CoreGui
from . import XLET_MESSAGE


class FloatAtom(CoreGui):
    def __init__(self, x, y, **kwargs):
        CoreGui.__init__(self, "floatatom", x, y, [])

        self._digits = int(kwargs.get("digits", 5))
        assert self._digits >= 0

        self._min = kwargs.get("min", 0)
        self._max = kwargs.get("max", 0)
        assert self._min <= self._max

        self._label_pos = self.POS_LEFT
        if "label_pos" in kwargs:
            pos = self._get_label_pos(kwargs["label_pos"])
            if pos is not None:
                self._label_pos = pos

        self.label = kwargs.get("label", "-")
        self.send = kwargs.get("send", "-")
        self.receive = kwargs.get("receive", "-")

        self._value = float(kwargs.get("value", 0))

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, v):
        assert isinstance(v, float) or isinstance(v, int)
        self._value = v

    @staticmethod
    def from_atoms(atoms):
        assert isinstance(atoms, list)
        assert len(atoms) == 9

        x = atoms[0]
        y = atoms[1]

        return FloatAtom(x, y,
                         digits=int(atoms[2]),
                         min=float(atoms[3]),
                         max=float(atoms[4]),
                         label_pos=int(atoms[5]),
                         label=atoms[6],
                         send=atoms[7],
                         receive=atoms[8])

    def get_height(self):
        return 17

    def get_width(self):
        return max(self._digits * 7, 20)

    def show_inlets(self):
        return self.receive == "-"

    def show_outlets(self):
        return self.send == "-"

    def has_label(self):
        return self._label and self._label != "-"

    def outlets(self):
        return [XLET_MESSAGE]

    def inlets(self):
        return [XLET_MESSAGE]

    def _is_int(self):
        return abs(self._value - int(self._value)) < 0.001

    def _str_value(self):
        if self._is_int():
            return str(int(self._value))
        else:
            return "{0:.2f}".format(self.value)

    def _label_brect(self):
        if not self.has_label():
            return 0, 0, 0, 0
        return self.brect_calc().text_brect(self._label)

    def draw(self, painter):
        vertexes = (
            (self.x, self.y),
            (0, self.height),
            (self.width, 0),
            (0, -10),
            (-7, -7)
        )

        text_yoff = 13

        painter.draw_poly(vertexes, fill=(0.88, 0.88, 0.88), outline=(0.75, 0.75, 0.75))
        painter.draw_text(self.x + 2, self.top + text_yoff, self._str_value())
        if self.show_inlets():
            painter.draw_inlets(self.inlets(), self.x, self.y, self.width)
        if self.show_outlets():
            painter.draw_outlets(self.outlets(), self.x, self.bottom, self.width)

        if self.has_label():
            lx, ly, lw, lh = self._label_brect()
            pad = 3
            if self._label_pos == self.POS_LEFT:
                lx = self.x - lw - pad
                ly = self.y + text_yoff
            elif self._label_pos == self.POS_RIGHT:
                lx = self.right + pad
                ly = self.y + text_yoff
            elif self._label_pos == self.POS_BOTTOM:
                lx = self.left
                ly = self.bottom + text_yoff
            elif self._label_pos == self.POS_TOP:
                lx = self.left
                ly = self.top - pad
            else:
                assert False

            painter.draw_text(lx, ly, self._label)

    def to_atoms(self):
        return ["#X", "floatatom", self._x, self._y, self._digits,
                self._min, self._max,
                self._label_pos, self.label, self.send, self.receive]
