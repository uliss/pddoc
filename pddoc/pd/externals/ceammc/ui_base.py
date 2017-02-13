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

from pddoc.pd import PdObject


class UIBase(PdObject):
    def __init__(self, name, x, y, **kwargs):
        PdObject.__init__(self, name, x, y, 100, 25, [])
        self._fixed_size = True
        self.parse_args(kwargs)

    def parse_args(self, args):
        if '@size' in args:
            sz = args.get('@size', '100x25').split('x')
            if len(sz) == 2:
                self.set_width(sz[0])
                self.set_height(sz[1])
            else:
                self.set_width(100)
                self.set_height(25)
        else:
            self.set_width(100)
            self.set_height(25)

        self.append_arg('@size')
        self.append_arg(str(self.width))
        self.append_arg(str(self.height))

    def calc_brect(self):
        pass
