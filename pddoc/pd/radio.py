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


class Radio(CoreGui):
    def __init__(self, name, x, y, **kwargs):
        CoreGui.__init__(self, name, x, y, [], **kwargs)
        self._size = int(kwargs.get("size", 15))
        self._newold = int(kwargs.get("newold", 1))
        self._init = int(kwargs.get("init", 0))
        self._number = int(kwargs.get("number", 8))
        self._value = int(kwargs.get("value", 0))
        self._sq_offset = 3

    @staticmethod
    def from_atoms(atoms):
        assert len(atoms) == 16
        assert atoms[0] in ("vradio", "hradio")

        if atoms[0] == "vradio":
            return PdVRadio(0, 0,
                            size=atoms[1],
                            newold=atoms[2],
                            init=atoms[3],
                            number=atoms[4],
                            send=atoms[5],
                            receive=atoms[6],
                            label=atoms[7],
                            label_xoff=atoms[8],
                            label_yoff=atoms[9],
                            font_type=atoms[10],
                            font_size=atoms[11],
                            bg_color=atoms[12],
                            fg_color=atoms[13],
                            label_color=atoms[14],
                            default_value=atoms[15]
                            )
        else:
            return PdHRadio(0, 0,
                            size=atoms[1],
                            newold=atoms[2],
                            init=atoms[3],
                            number=atoms[4],
                            send=atoms[5],
                            receive=atoms[6],
                            label=atoms[7],
                            label_xoff=atoms[8],
                            label_yoff=atoms[9],
                            font_type=atoms[10],
                            font_size=atoms[11],
                            bg_color=atoms[12],
                            fg_color=atoms[13],
                            label_color=atoms[14],
                            default_value=atoms[15])

    def to_atoms(self):
        return ["#X", "obj", self.x, self.y, self.name, self._size, self._newold,
                self._init, self._number,
                self.send, self.receive,
                self.label, self._label_xoff, self._label_yoff,
                self._font_type, self._font_size,
                self._bg_color.to_pd(), self._fg_color.to_pd(), self._label_color.to_pd(),
                "0"]

class PdHRadio(Radio):
    def __init__(self, x, y, **kwargs):
        Radio.__init__(self, "hradio", x, y, **kwargs)

    def get_height(self):
        return self._size

    def get_width(self):
        return self._size * self._number

    def draw(self, painter):
        self.draw_bbox(painter)

        # draw cells
        assert self._number > 0
        step = self.width / self._number
        for i in range(1, self._number):
            x = self.x + i * step
            painter.draw_line(x, self.top, x, self.bottom, color=(0, 0, 0))

        # draw switch
        sx = self.x + self._size * self._value + self._sq_offset
        sy = self.y + self._sq_offset
        sz = self._size - 2 * self._sq_offset
        painter.draw_rect(sx, sy, sz, sz, fill=self.fgcolor())

        self.draw_label(painter)
        self.draw_xlets(painter)


class PdVRadio(Radio):
    def __init__(self, x, y, **kwargs):
        Radio.__init__(self, "vradio", x, y, **kwargs)

    def get_width(self):
        return self._size

    def get_height(self):
        return self._size * self._number

    def draw(self, painter):
        self.draw_bbox(painter)

        # draw cells
        assert self._number > 0
        step = self.height / self._number
        for i in range(1, self._number):
            y = self.y + i * step
            painter.draw_line(self.left, y, self.right, y, color=(0, 0, 0))

        # draw switch
        sy = self.y + self._size * self._value + self._sq_offset
        sx = self.x + self._sq_offset
        sz = self._size - 2 * self._sq_offset
        painter.draw_rect(sx, sy, sz, sz, fill=self.fgcolor())

        self.draw_label(painter)
        self.draw_xlets(painter)
