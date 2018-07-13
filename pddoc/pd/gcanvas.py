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


class GCanvas(CoreGui):
    # X [size]? [width]? [height]? [send]? [receive]? [label]?
    # [x_off]? [y_off]? [font]? [font_size]? [bg_color]? [label_color]? [?]?;\r\n
    def __init__(self, x, y, **kwargs):
        CoreGui.__init__(self, "cnv", x, y, [], **kwargs)
        self._size = int(kwargs.get("size", 15))
        self.width = int(kwargs.get("width", 100))
        self.height = int(kwargs.get("height", 60))

    @staticmethod
    def from_atoms(atoms):
        assert len(atoms) == 13
        return GCanvas(0, 0,
                       size=atoms[0],
                       width=atoms[1],
                       height=atoms[2],
                       send=atoms[3],
                       receive=atoms[4],
                       label=atoms[5],
                       label_xoff=atoms[6],
                       label_yoff=atoms[7],
                       font_type=atoms[8],
                       font_size=atoms[9],
                       bg_color=atoms[10],
                       label_color=atoms[11])

    def draw(self, painter):
        painter.draw_rect(self.x, self.y, self.width, self.height, fill=self.bgcolor())
        self.draw_label(painter)

    def to_atoms(self):
        return ["#X", "obj", self.x, self.y, "cnv", self._size, self.width, self.height,
                self.send, self.receive,
                self.label, self._label_xoff, self._label_yoff,
                self._font_type, self._font_size, self._bg_color.to_pd(), self._label_color.to_pd(), 0]
