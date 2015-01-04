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

from pdcoregui import PdCoreGui


class PdFloatAtom(PdCoreGui):
    def __init__(self, x, y, **kwargs):
        PdCoreGui.__init__(self, "floatatom", x, y, [])
        self._digits = int(kwargs.get("digits", 5))
        assert self._digits > 0

        self._min = kwargs.get("min", 0)
        self._max = kwargs.get("max", 0)
        assert self._min <= self._max

        self._label_pos = kwargs.get("label_pos", 0)
        assert self._label_pos in xrange(0, 4)

        self.label = kwargs.get("label", "-")
        self.send = kwargs.get("send", "-")
        self.receive = kwargs.get("receive", "-")

    @staticmethod
    def from_atoms(atoms):
        assert isinstance(atoms, list)
        assert len(atoms) == 9

        x = atoms[0]
        y = atoms[1]

        return PdFloatAtom(x, y,
                           digits=int(atoms[2]),
                           min=int(atoms[3]),
                           max=int(atoms[4]),
                           label_pos=int(atoms[5]),
                           label=atoms[6],
                           send=atoms[7],
                           receive=atoms[8])

    def get_height(self):
        return 17

    def get_width(self):
        return max(self._digits * 7, 20)

    def no_send(self):
        return self.send == "-"

    def no_receive(self):
        return self.receive == "-"

    def outlets(self):
        if self.no_send():
            return [self.XLET_MESSAGE]
        else:
            return []

    def inlets(self):
        if self.no_receive():
            return [self.XLET_MESSAGE]
        else:
            return []

    def draw(self, painter):
        vertexes = (
            (self.x, self.y),
            (0, self.height),
            (self.width, 0),
            (0, -10),
            (-7, -7)
        )

        painter.draw_poly(vertexes, fill=(0.88, 0.88, 0.88), outline=(0.75, 0.75, 0.75))
        painter.draw_text(self.x + 2, self.y + 13, "0")
        painter.draw_inlets(self.inlets(), self.x, self.y, self.width)
        painter.draw_outlets(self.outlets(), self.x, self.y + self.height, self.width)

