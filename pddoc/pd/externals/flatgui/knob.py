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

from pddoc.pd import CoreGui
from pddoc.cairopainter import CairoPainter
from pddoc.pd import XLET_GUI
from math import pi, sin, cos


def create(atoms):
    assert len(atoms)
    return Knob.from_atoms(atoms)


# X obj 391 121
# name size  min max log init  send  receive  label lx ly  font font_size  bcolor   fcolor lcolor init_value steady
# knob 32 32 0   127 0   0     empty empty    empty 0  -8  0    8          -262144  -1     -1     0          1
class Knob(CoreGui):
    @staticmethod
    def from_atoms(atoms):
        return Knob(0, 0,
                    size=atoms[1],
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
                    init_value=atoms[17],
                    steady=atoms[18])

    def __init__(self, x, y, **kwargs):
        CoreGui.__init__(self, "knob", x, y, [], **kwargs)
        self._width = float(kwargs.get("size", 32))
        self._height = self._width
        self._min = float(kwargs.get("min", 0))
        self._max = float(kwargs.get("max", 127))
        assert self._min <= self._max
        self._log = int(kwargs.get("log", 0))
        self._init = int(kwargs.get("init", 0))
        self._default_value = int(kwargs.get("default_value", 0))
        self._steady = int(kwargs.get("steady", 0))

    def inlets(self):
        return [XLET_GUI]

    def outlets(self):
        return [XLET_GUI]

    def draw(self, painter):
        assert isinstance(painter, CairoPainter)

        self.draw_label(painter)
        # self.draw_xlets(painter)
        stroke_width = 3

        angle1 = 0.58 * pi
        angle2 = 2.42 * pi
        radius = self._width / 2
        x0 = self.x + radius
        y0 = self.y + radius
        painter.draw_arc(x0, y0, radius, angle1, angle2,
                         width=stroke_width,
                         outline=(0, 0, 0))

        x1 = x0 - (radius * sin(0.08 * pi))
        y1 = y0 + (radius * cos(0.08 * pi))
        painter.draw_line(x0, y0, x1, y1, width=stroke_width, color=self.fgcolor())