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
    # X obj 10 45 pddplink URL -text TXT;
    if len(atoms) == 2:
        return PddpLink(0, 0, atoms[1])
    elif len(atoms) == 4:
        return PddpLink(0, 0, atoms[1], atoms[3])
    else:
        assert False


class PddpLink(pd.PdObject):
    def __init__(self, x, y, url, text=None):
        if text:
            pd.PdObject.__init__(self, "pddp/pddplink", x, y, 0, 0, [url, "-text", text])
        else:
            pd.PdObject.__init__(self, "pddp/pddplink", x, y, 0, 0, [url])

        self._text = text
        self._url = url

    def inlets(self):
        return ()

    def outlets(self):
        return ()

    def url(self):
        return self._url

    def text(self):
        if self._text:
            return self._text
        else:
            return self.url()

    def draw(self, painter):
        assert isinstance(painter, CairoPainter)
        painter.draw_text(self.x + 4, self.y + 12, self.text(), color=(0, 0, 1))

    def calc_brect(self):
        x, y, w, h = self.brect_calc().string_brect(self.text(), None)
        self.width = w
        self.height = h