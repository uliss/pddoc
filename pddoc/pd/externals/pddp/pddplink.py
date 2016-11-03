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

import pddoc.pd as pd
from pddoc.cairopainter import CairoPainter


def create(atoms):
    assert len(atoms) > 1
    return PddpLink(atoms[0], atoms[1:])


class PddpLink(pd.PdObject):
    def __init__(self, name, args):
        pd.PdObject.__init__(self, name, 0, 0, 0, 0, args)

    def inlets(self):
        return ()

    def outlets(self):
        return ()

    def url(self):
        return self.args[0]

    def text(self):
        if len(self.args) > 2:
            return " ".join(self._args[2:])
        else:
            return self.url()

    def draw(self, painter):
        assert isinstance(painter, CairoPainter)
        painter.draw_text(self.x + 4, self.y + 12, self.text(), color=(0, 0, 1))