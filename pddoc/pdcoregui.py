#!/usr/bin/env python
# coding=utf-8

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

__author__ = 'Serge Poltavski'


import pdobject
from termcolor import colored


class PdColor:
    def __init__(self, r=0, g=0, b=0):
        assert isinstance(r, float) or isinstance(r, int)
        assert isinstance(g, float) or isinstance(g, int)
        assert isinstance(b, float) or isinstance(b, int)
        self._r = r
        self._g = g
        self._b = b

    @staticmethod
    def black():
        return PdColor(0, 0, 0)

    @staticmethod
    def white():
        return PdColor(1, 1, 1)

    def rgb(self):
        return self._r, self._g, self._b

    def set_rgb(self, rgb):
        self._r = rgb[0]
        self._g = rgb[1]
        self._b = rgb[2]

    def from_pd(self, value):
        v = abs(int(value) + 1)
        r = v / 4096
        g = (v % 4096) / 64
        b = (v % 4096) % 64
        self._r = int(round(r / 63.0 * 255)) % 256
        self._g = int(round(g / 63.0 * 255)) % 256
        self._b = int(round(b / 63.0 * 255)) % 256

    def compare(self, rgb):
        if isinstance(rgb, list) or isinstance(rgb, tuple):
            return self._r == rgb[0] and self._g == rgb[1] and self._b == rgb[2]
        elif isinstance(rgb, self.__class__):
            return self._r == rgb._r and self._g == rgb._g and self._b == rgb._b
        else:
            return False

    def is_black(self):
        return self.compare((0, 0, 0))

    def rgb_float(self):
        return self._r / 255.0, self._g / 255.0, self._b / 255.0

    def to_pd(self):
        return -4096 * int(round(self._r * (63 / 255.0))) \
               - 64 * int(round(self._g * (63 / 255.0))) \
               - 1 * int(round(self._b * (63 / 255.0))) - 1

    def __str__(self):
        res = colored("RGB[%i,%i,%i]" % (self._r, self._g, self._b), "green")
        return res

    def __eq__(self, other):
        return self.compare(other)


class PdCoreGui(pdobject.PdObject):
    tgl_defaults = ['15', '0', 'empty', 'empty', 'empty', '17', '7', '0', '10', '-262144', '-1', '-1', '0', '1']

    def __init__(self, name, x, y, args):
        pdobject.PdObject.__init__(self, name, x, y, 0, 0, args)
        assert len(args) > 0
        self._props = {}
        self.parse_args(args)

    def __str__(self):
        return "[GUI:%-36s {x:%i,y:%i,id:%i}" % (self.name + "]", self._x, self._y, self._id)

    def draw(self, painter):
        painter.draw_core_gui(self)

    def prop(self, key):
        return self._props[key]

    def parse_args(self, args):
        def color_from_pd(v):
            c = PdColor()
            c.from_pd(v)
            return c

        def slot_from_pd(slot):
            if slot == "empty":
                return None
            else:
                return slot

        if self.name == "tgl":
            # square size of the gui element
            self._props["size"] = int(args[0])
            self.width = self._props["size"]
            self.height = self._props["size"]
            # set on load
            self._props["init"] = int(args[1])
            self._props["send"] = slot_from_pd(args[2])
            self._props["receive"] = slot_from_pd(args[3])
            self._props["label"] = slot_from_pd(args[4])
            # horizontal position of the label text relative to the upperleft corner of the object
            self._props["label_xoff"] = int(args[5])
            # vertical position of the label text relative to the upperleft corner of the object
            self._props["label_yoff"] = int(args[6])
            self._props["font"] = args[7]
            self._props["font_size"] = args[8]
            self._props["bg_color"] = color_from_pd(args[9])
            self._props["fg_color"] = color_from_pd(args[10])
            self._props["label_color"] = color_from_pd(args[11])
            # value sent when the [init] attribute is set
            self._props["init_value"] = int(args[12])
            # default_value when the [init]? attribute is not set
            self._props["default_value"] = int(args[13])
            return

        if self.name == "cnv":
            self._props["size"] = int(args[0])  # size of selectable square
            self._props["width"] = int(args[1])  # horizontal size of the GUI-element
            self.width = self._props["width"]
            self._props["height"] = int(args[2])  # vertical size of the GUI-element
            self.height = self._props["height"]
            self._props["send"] = args[3]  # send symbol name
            self._props["receive"] = args[4]  # receive symbol name
            self._props["label"] = args[5]
            # horizontal position of the label text relative to the upperleft corner of the object
            self._props["label_xoff"] = int(args[6])
            # vertical position of the label text relative to the upperleft corner of the object
            self._props["label_yoff"] = int(args[7])
            self._props["font"] = args[8]
            self._props["fontsize"] = int(args[9])
            self._props["bg_color"] = color_from_pd(args[10])
            self._props["label_color"] = color_from_pd(args[11])
            return

    def bgcolor(self):
        return self.prop("bg_color").rgb_float()

    def fgcolor(self):
        return self.prop("fg_color").rgb_float()

    def lbcolor(self):
        return self.prop("label_color").rgb_float()

    def inlets(self):
        if self.name in ("tgl", "bng", "hsl", "vsl", "nbx"):
            if "receive" not in self._props or self._props["receive"] is None:
                return [self.XLET_GUI]
            else:
                return []

    def outlets(self):
        if self.name in ("tgl", "bng", "hsl", "vsl", "nbx"):
            if "send" not in self._props or self._props["send"] is None:
                return [self.XLET_GUI]
            else:
                return []

    def traverse(self, visitor):
        visitor.visit_core_gui(self)