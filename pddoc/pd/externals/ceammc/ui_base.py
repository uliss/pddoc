#!/usr/bin/env python
# coding=utf-8

#   Copyright (C) 2017 by Serge Poltavski                                 #
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

from __future__ import print_function
from pddoc.pd import PdObject
from pddoc.cairopainter import CairoPainter


class UIBase(PdObject):
    def __init__(self, name, x, y, **kwargs):
        PdObject.__init__(self, name, x, y, 100, 25, [])
        self._fixed_size = True
        self._properties = kwargs
        self.parse_props()

    def parse_props(self):
        if '@size' in self._properties:
            sz = self._properties['@size'].split('x')
            if len(sz) == 2:
                self.set_property('@size', sz[0] + ' ' + sz[1])
        else:
            self.set_property('@size', '100 25')

    def set_property(self, name, value):
        self._properties[name] = value
        if name == '@size':
            self.width = int(value.split(' ')[0])
            self.height = int(value.split(' ')[1])

    def get_property(self, name, default=None):
        return self._properties.get(name, default)

    @property
    def args(self):
        res = []
        sorted_list = sorted(self._properties.items(), key=lambda x: x[0])

        for item in sorted_list:
            k = item[0]
            v = item[1]
            res.append(k)
            if not v:
                continue

            for p in v.split(' '):
                res.append(str(p))

        return res

    def calc_brect(self):
        pass

    def draw(self, painter):
        assert isinstance(painter, CairoPainter)
        pass

    def set_bg_color(self, color):
        self.set_property('@background_color', ' '.join(map(lambda c: str(c), color.rgb_float())))

