#!/usr/bin/env python
# coding=utf-8

# Copyright (C) 2015 by Serge Poltavski                                 #
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

from pdcoregui import *
import six


def color_from_str(value):
    c = PdColor()

    if isinstance(value, int):
        c.from_pd(value)
    elif isinstance(value, six.string_types):
        if value[0] == '#':
            return PdColor.from_hex(value)
        else:
            c.from_pd(value)
    else:
        assert False

    return c


class PdBng(PdCoreGui):
    # default arguments:
    # X obj 256 25 bng 15 250 50 0 empty empty empty 17 7 0 10 -262144 -1 -1;

    def __init__(self, x, y, **kwargs):
        PdCoreGui.__init__(self, "bng", x, y, [])
        self._size = int(kwargs.get("size", 15))
        assert self._size > 0

        self._hold = int(kwargs.get("hold", 250))
        assert 50 <= self._hold <= 1000000000

        self._interrupt = int(kwargs.get("interrupt", 50))
        assert 10 <= self._interrupt <= 250

        self._init = int(kwargs.get("init", 0))
        self._send = kwargs.get("send", "empty")
        self._receive = kwargs.get("receive", "empty")
        self._label = kwargs.get("label", "empty")

        self._label_xoff = int(kwargs.get("label_xoff", 17))
        self._label_yoff = int(kwargs.get("label_yoff", 7))
        self._font_type = int(kwargs.get("font_type", 0))
        self._font_size = int(kwargs.get("font_size", 10))
        self._bg_color = color_from_str(kwargs.get("bg_color", -262144))
        self._fg_color = color_from_str(kwargs.get("fg_color", -1))
        self._label_color = color_from_str(kwargs.get("label_color", -1))

        self._pressed = 'pressed' in kwargs and kwargs['pressed'].lower() == "true"

    @staticmethod
    def from_atoms(atoms):
        assert isinstance(atoms, list)
        assert len(atoms) == 14

        return PdBng(0, 0,
                     size=int(atoms[0]),
                     hold=int(atoms[1]),
                     interrupt=int(atoms[2]),
                     init=int(atoms[3]),
                     send=atoms[4],
                     receive=atoms[5],
                     label=atoms[6],
                     label_xoff=atoms[7],
                     label_yoff=atoms[8],
                     font_type=atoms[9],
                     font_size=atoms[10],
                     bg_color=atoms[11],
                     fg_color=atoms[12],
                     label_color=atoms[13])

    def get_height(self):
        return self._size

    def get_width(self):
        return self._size

    def center(self):
        return self.x + self.width/2 + 0.75, self.y + self.height/2 + 0.75

    def _get_label_pos(self):
        return self.x + self._label_xoff, self.y + self._label_yoff  # font height correction

    def draw(self, painter):
        vertexes = (
            (self.x, self.y),
            (0, self.height),
            (self.width, 0),
            (0, -self.height)
        )

        painter.draw_poly(vertexes, fill=self._bg_color.rgb_float(), outline=(0, 0, 0))
        cx, cy = self.center()

        circle_color = self._bg_color.rgb_float()
        if self._pressed:
            circle_color = self._fg_color.rgb_float()
        painter.draw_circle(cx, cy, (self.width-1.5)/2, fill=circle_color)

        if not self.no_label():
            lx, ly = self._get_label_pos()
            painter.draw_text(lx, ly, self.label, color=self._label_color.rgb_float())
        painter.draw_inlets(self.inlets(), self.x, self.y, self.width)
        painter.draw_outlets(self.outlets(), self.x, self.bottom, self.width)

