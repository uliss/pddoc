#!/usr/bin/env python
# coding=utf-8

# Copyright (C) 2015 by Serge Poltavski                                 #
# serge.poltavski@gmail.com                                             #
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

from .coregui import *


class Nbx(CoreGui):
    def __init__(self, x, y, **kwargs):
        CoreGui.__init__(self, "nbx", x, y, [], **kwargs)
        self._digits = int(kwargs.get("digits", 5))  # number of digits the element displays
        self._height = int(kwargs.get("height", 14))  # vertical size of element in pixels
        self._min = float(kwargs.get("min", -1e+037))  # minimum value
        self._max = float(kwargs.get("max", 1e+037))  # maximum value
        self._log = int(kwargs.get("log", 0))  # linear when unset, logarithmic when set
        self._init = float(kwargs.get("init", 0))
        # logarithmic steps, accepts values from 10 to 2000, default is 256
        self._log_height = int(kwargs.get("log_height", 256))

    @staticmethod
    def from_atoms(atoms):
        assert len(atoms) == 19
        assert atoms[0] == "nbx"

        return Nbx(0, 0, digits=atoms[1],
                   height=atoms[2],
                   min=atoms[3],
                   max=atoms[4],
                   log=atoms[5],
                   init=atoms[6],
                   send=atoms[7],
                   receive=atoms[8],
                   label=atoms[9],
                   label_xoff=atoms[10],
                   label_yoff=atoms[11],
                   font_type=atoms[12],
                   font_size=atoms[13],
                   bg_color=atoms[14],
                   fg_color=atoms[15],
                   label_color=atoms[16],
                   log_height=atoms[18])

    def get_width(self):
        return (self._digits + 1) * self._font_size * 0.85

    def get_height(self):
        return self._height

    def draw_value(self, painter):
        h = self.height / 2
        painter.draw_line(self.left, self.top, self.left + h, self.top + h, color=self.fgcolor())
        painter.draw_line(self.left, self.bottom, self.left + h, self.top + h, color=self.fgcolor())

        yoff = self._font_size / 5
        painter.draw_text(self.left + h + 2, self.bottom - yoff, str(self._init),
                          color=self.fgcolor(),
                          font="Menlo",
                          font_size=self._font_size)

    def draw(self, painter):
        skos = 4
        vertexes = (
            (self.x, self.y),
            (0, self.height),
            (self.width, 0),
            (0, -self.height + skos),
            (-skos, -skos)
        )

        painter.draw_poly(vertexes, fill=self.bgcolor(), outline=(0, 0, 0))

        self.draw_value(painter)
        self.draw_label(painter)
        self.draw_xlets(painter)
