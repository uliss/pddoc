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

from .coregui import *
import six


class PdBng(CoreGui):
    # default arguments:
    # X obj 256 25 bng 15 250 50 0 empty empty empty 17 7 0 10 -262144 -1 -1;

    def __init__(self, x, y, **kwargs):
        CoreGui.__init__(self, "bng", x, y, [], **kwargs)
        self._size = int(kwargs.get("size", 15))
        assert self._size > 0

        self._hold = int(kwargs.get("hold", 250))
        assert 50 <= self._hold <= 1000000000

        self._interrupt = int(kwargs.get("interrupt", 50))
        assert 10 <= self._interrupt <= 250

        self._init = int(kwargs.get("init", 0))
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

    def draw(self, painter):
        self.draw_bbox(painter)
        cx, cy = self.center()

        circle_color = self.bgcolor()
        if self._pressed:
            circle_color = self.fgcolor()
        painter.draw_circle(cx, cy, (self.width-1.5)/2, fill=circle_color)

        self.draw_label(painter)
        self.draw_xlets(painter)

    def to_atoms(self):
        return ["#X", "obj", self.x, self.y, "bng", self._size, self._hold,
                self._interrupt, self._init,
                self.send, self.receive,
                self.label, self._label_xoff, self._label_yoff,
                self._font_type, self._font_size,
                self._bg_color.to_pd(), self._fg_color.to_pd(), self._label_color.to_pd()]
