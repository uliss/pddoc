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

from pddoc.pd.externals.ceammc.ui_base import UIBase
from pddoc.cairopainter import CairoPainter


def create_by_name(name, args, **kwargs):
    return UILink(0, 0, **kwargs)


class UILink(UIBase):
    def __init__(self, x, y, **kwargs):
        UIBase.__init__(self, "ui.link", x, y, **kwargs)
        self._properties.pop('@size', None)

    def inlets(self):
        return ()

    def outlets(self):
        return ()

    def url(self):
        return self._properties['@url']

    def text(self):
        if '@title' not in self._properties:
            return '<no-title>'

        return self._properties['@title']

    def draw(self, painter):
        assert isinstance(painter, CairoPainter)
        painter.draw_text(self.x + 4, self.y + 12, self.text(), color=(0, 0, 1))

    def calc_brect(self):
        x, y, w, h = self.brect_calc().string_brect(self.text(), None)
        self.width = w
        self.height = h
