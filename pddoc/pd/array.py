#!/usr/bin/env python
# coding=utf-8
from typing import List

from .obj import PdObject
import logging

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


class Array(PdObject):
    STYLE_POINTS, STYLE_LINES, STYLE_CURVE = (1, 0, 2)

    def __init__(self, name, size, save=0, cnv_x=0, cnv_y=22, cnv_w=450, cnv_h=300):
        PdObject.__init__(self, name)
        self.width = 200
        self.height = 140
        self._fixed_size = True
        self._size = int(float(size))
        self._save = int(save)
        self._data = [0] * self._size
        self._xrange = (0, self._size)
        self._yrange = (-1, +1)
        self._cnv_x = cnv_x
        self._cnv_y = cnv_y
        self._cnv_w = cnv_w
        self._cnv_h = cnv_h
        self._style = self.STYLE_LINES
        self.calc_brect()

    def flags(self):
        return self._save | (1 << self._style)

    def save_flag(self):
        return self._save

    def size(self):
        return self._size

    def data(self):
        return self._data

    def set_data(self, atoms):
        assert len(atoms) == self._size
        self._data = list(map(lambda x: float(x), atoms))

    def xrange(self):
        return self._xrange

    def set_xrange(self, min_x, max_x):
        self._xrange = (min_x, max_x)

    def yrange(self):
        return self._yrange

    def set_yrange(self, min_y, max_y):
        self._yrange = (min_y, max_y)

    def set_style(self, style):
        if style not in (0, 1, 2):
            logging.error('invalid style value: %d', style)
        else:
            self._style = style

    @staticmethod
    def from_atoms(atoms: List[str]):
        assert len(atoms) == 4 or len(atoms) == 6
        return Array(atoms[0], atoms[1], int(atoms[3]))

    def draw(self, painter):
        painter.draw_rect(*self.brect())
        painter.draw_text(self.x, self.y - 5, self.name)

        if not self._data:
            return
        
        swd = self.width / self._size
        yrange = self._yrange[1] - self._yrange[0]
        sht = self.height / yrange
        for idx in range(0, self._size):
            x0 = self.left + swd * idx
            x1 = x0 + swd
            y = self.top + sht * self._data[idx] + (self.height * self._yrange[1])/yrange
            painter.draw_line(x0, y, x1, y, width=3, color=(0, 0, 0))

    def to_string(self):
        res = 'array ' + PdObject.unescape(self.name) + ' ' + self.args_to_string()
        return res.strip()

    def inlets(self):
        return []

    def outlets(self):
        return []

