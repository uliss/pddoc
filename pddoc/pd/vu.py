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

from .coregui import CoreGui
from . import XLET_GUI

# [width]? - horizontal size of element
# [height]? - vertical size of element
# [receive]? - receive symbol name
# [label]? - label
# [x_off]? - horizontal position of the label text relative to the upperleft corner of the object
# [y_off]? - vertical position of the label text relative to the upperleft corner of the object
# [font]? - font type
# [fontsize]? - font size
# [bg_color]? - background color
# [label_color]? - label color
# [scale]? - when set the logarithmic scale is displayed
# [?]? - unknown value, default is zero


class PdVu(CoreGui):
    def __init__(self, x, y, **kwargs):
        CoreGui.__init__(self, "vu", x, y, [], **kwargs)
        self._width = int(kwargs.get("width", 15))  # number of digits the element displays
        self._height = int(kwargs.get("height", 120))  # vertical size of element in pixels
        self._scale = bool(int(kwargs.get("scale", 0)))  # when set the logarithmic scale is displayed

    @staticmethod
    def from_atoms(atoms):
        assert len(atoms) == 13
        assert atoms[0] == "vu"

        return PdVu(0, 0, width=atoms[1],
                    height=atoms[2],
                    receive=atoms[3],
                    label=atoms[4],
                    label_xoff=atoms[5],
                    label_yoff=atoms[6],
                    font_type=atoms[7],
                    font_size=atoms[8],
                    bg_color=atoms[9],
                    label_color=atoms[10],
                    scale=atoms[11])

    def inlets(self):
        return [XLET_GUI] * 2

    def outlets(self):
        return [XLET_GUI] * 2

    def get_width(self):
        return self._width + 2

    def get_height(self):
        return self._height

    def draw_scale(self, painter):
        scale_txt = (">+12", "+6", "+2", "-0dB", "-2", "-6", "-12", "-20", "-30", "-50", "<-99")
        x = self.right + 5
        y = self.top + 4
        ystep = self.get_height() / (len(scale_txt) - 1)

        for txt in scale_txt:
            painter.draw_text(x, y, txt, color=self.lbcolor())
            y += ystep

    def draw(self, painter):
        self.draw_bbox(painter)
        self.draw_label(painter)
        self.draw_xlets(painter)

        if self._scale:
            self.draw_scale(painter)
