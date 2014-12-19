# /usr/bin/env python

#   Copyright (C) 2014 by Serge Poltavski                                 #
#   serge.poltavski@gmail.com                                            #
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


# -*- coding: utf-8 -*-

__author__ = 'Serge Poltavski'

# [size]? - square size of the gui element
# [init]? - set on load
# [send]? - send symbol name
# [receive]? - receive symbol name
# [label]? - label
# [x_off]? - horizontal position of the label text relative to the upperleft corner of the object
# [y_off]? - vertical position of the label text relative to the upperleft corner of the object
# [font]? - font type
# [fontsize]? - font size
# [bg_color]? - background color
# [fg_color]? - foreground color
# [label_color]? - label color
# [init_value]? - value sent when the [init]? attribute is set
# [default_value]? - default value when the [init]? attribute is not set

import pdobject
from termcolor import colored


class PdColor:
    def __init__(self, r, g, b):
        self._r = r
        self._g = g
        self._b = b

    def rgb(self):
        return (self._r, self._g, self._b)

    def parse(self, value):
        # color = ( [red]? * -65536) + ( [green]? * -256) + ( [blue]? * -1)
        value = int(value)
        q, r = divmod(value, -65536)
        self._r = abs(q)
        q, r = divmod(r, -256)
        self._g = abs(q)
        self._b = abs(r)

    def __str__(self):
        res = colored("RGB[%3i,%3i,%3i]" % (self._r, self._g, self._b), "green")
        return res


class PdCoreGui(pdobject.PdObject):
    def __init__(self, x, y, args):
        super(PdCoreGui, self).__init__(x, y, -1, -1, args)
        self.name = args[0]
        self.size = int(args[1])
        self.width = self.size
        self.height = self.size

        # self.init = args[2]
        self.send = args[3]
        self.color = PdColor(255, 0, 0)


    def __str__(self):
        return "[GUI:%-36s {x:%i,y:%i,id:%i}" % (self.args[0] + "]", self.x, self.y, self.id)

    def draw(self, painter):
        painter.draw_core_gui(self)