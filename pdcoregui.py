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
    def __init__(self, r=0, g=0, b=0):
        self._r = r
        self._g = g
        self._b = b

    def rgb(self):
        return (self._r, self._g, self._b)

    def parse(self, value):
        # print value
        v = abs(int(value))
        r = ((0b111111000000000000 & v) >> 12) * 4
        g = ((0b111111000000 & v) >> 6) * 4
        b = ((0b111111 & v)) * 4
        self._r = r
        self._g = g
        self._b = b

    def compare(self, rgb):
        if isinstance(rgb, list) or isinstance(rgb, tuple):
            return self._r == rgb[0] and self._g == rgb[1] and self._b == rgb[2]
        elif isinstance(rgb, self.__class__):
            return self._r == rgb._r and self._g == rgb._g and self._b == rgb._b
        else:
            return False

    def is_black(self):
        return self.compare((0, 0, 0))

    def to_float(self):
        return (self._r / 255.0, self._g / 255.0, self._b / 255.0)


    def __str__(self):
        res = colored("RGB[%i,%i,%i]" % (self._r, self._g, self._b), "green")
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

        self.props = {}
        self.parse_props(args)


    def __str__(self):
        return "[GUI:%-36s {x:%i,y:%i,id:%i}" % (self.args[0] + "]", self.x, self.y, self.id)

    def draw(self, painter):
        painter.draw_core_gui(self)

    def parse_props(self, args):
        if self.name == "tgl":
            # square size of the gui element
            self.props["size"] = int(args[1])
            # set on load
            self.props["init"] = int(args[2])
            self.props["send"] = args[3]
            self.props["receive"] = args[4]
            self.props["label"] = args[5]
            # horizontal position of the label text relative to the upperleft corner of the object
            self.props["label_xoff"] = int(args[6])
            # vertical position of the label text relative to the upperleft corner of the object
            self.props["label_yoff"] = int(args[7])
            self.props["font"] = args[8]
            self.props["font_size"] = args[9]

            c = PdColor()
            c.parse(args[10])
            self.props["bg_color"] = c
            self.props["fg_color"] = args[11]
            self.props["label_color"] = args[12]
            # value sent when the [init] attribute is set
            self.props["init_value"] = int(args[13])
            # default_value when the [init]? attribute is not set
            self.props["default_value"] = int(args[14])
            pass

    def inlets(self):
        if self.name in ("tgl", "bng", "hsl", "vsl"):
            if not self.props.has_key("receive") or self.props["receive"] == "empty":
                return [self.XLET_GUI]
            else:
                return []

    def outlets(self):
        if self.name in ("tgl", "bng", "hsl", "vsl"):
            if not self.props.has_key("receive") or self.props["receive"] == "empty":
                return [self.XLET_GUI]
            else:
                return []