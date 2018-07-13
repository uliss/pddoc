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


class PdToggle(CoreGui):
    @staticmethod
    def from_atoms(atoms):
        return PdToggle(0, 0,
                        size=atoms[0],
                        init=atoms[1],
                        send=atoms[2],
                        receive=atoms[3],
                        label=atoms[4],
                        label_xoff=atoms[5],
                        label_yoff=atoms[6],
                        font_type=atoms[7],
                        font_size=atoms[8],
                        bg_color=atoms[9],
                        fg_color=atoms[10],
                        label_color=atoms[11],
                        init_value=atoms[12],
                        default_value=atoms[13])

    def __init__(self, x, y, **kwargs):
        # tgl_defaults = ['15', '0', 'empty', 'empty', 'empty', '17', '7', '0', '10', '-262144', '-1', '-1', '0', '1']
        CoreGui.__init__(self, "tgl", x, y, [], **kwargs)
        # square size of the gui element
        self._size = int(kwargs.get("size", 15))
        self._init = int(kwargs.get("init", 0))
        # value sent when the [init] attribute is set
        self._init_value = int(kwargs.get("init_value", 0))
        # default_value when the [init]? attribute is not set
        self._default_value = int(kwargs.get("default_value", 1))
        self._checked = kwargs.get("checked", False)

    def get_width(self):
        return self._size

    def get_height(self):
        return self._size

    def draw(self, painter):
        self.draw_bbox(painter)

        if self._checked:
            painter.draw_line(self.left, self.top, self.right, self.bottom, color=self.fgcolor())
            painter.draw_line(self.left, self.bottom, self.right, self.top, color=self.fgcolor())

        self.draw_label(painter)
        self.draw_xlets(painter)

    def to_atoms(self):
        return ["#X", "obj", self.x, self.y, "tgl", self._size, self._init,
                self.send, self.receive,
                self.label, self._label_xoff, self._label_yoff,
                self._font_type, self._font_size,
                self._bg_color.to_pd(), self._label_color.to_pd(), self._fg_color.to_pd(),
                self._init_value, self._default_value]
