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


from pddoc.pd import PdObject
from pddoc.cairopainter import CairoPainter


def create(atoms):
    assert len(atoms)
    return PddpDsp(atoms[0], atoms[1:])


class PddpDsp(PdObject):
    def __init__(self, name, args):
        PdObject.__init__(self, name, 0, 0, 0, 0, args)

    def inlets(self):
        return ()

    def outlets(self):
        return ()

    def url(self):
        return self.args[0]

    def get_height(self):
        return 18

    def get_width(self):
        return 60

    def draw(self, painter):
        assert isinstance(painter, CairoPainter)
        painter.draw_rect(self.x, self.y, self.width, self.height, color=(0, 0, 0), fill=(0.5, 1, 0.5), width=1)
        line_x = int(self.left + 18)
        painter.draw_line(line_x, self.top, line_x, self.bottom, color=(0, 0, 0), width=1)
        painter.draw_text(line_x + 5, self.bottom - 3, "dsp", color=(0, 0, 0), font_size=14, font="Monospace")