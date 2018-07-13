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

from .obj import *
from termcolor import colored
import six
import logging

from . import XLET_GUI
from .abstractvisitor import AbstractVisitor


class Color:
    def __init__(self, r=0, g=0, b=0):
        assert isinstance(r, float) or isinstance(r, int)
        assert isinstance(g, float) or isinstance(g, int)
        assert isinstance(b, float) or isinstance(b, int)
        self._r = r
        self._g = g
        self._b = b

    @staticmethod
    def black():
        return Color(0, 0, 0)

    @staticmethod
    def white():
        return Color(255, 255, 255)

    def rgb(self):
        return self._r, self._g, self._b

    def set_rgb(self, rgb):
        self._r = rgb[0]
        self._g = rgb[1]
        self._b = rgb[2]

    def from_pd(self, value):
        v = abs(int(value) + 1)
        r = v // 4096
        g = (v % 4096) // 64
        b = (v % 4096) % 64
        self._r = int(round(r / 63.0 * 255.0)) % 256
        self._g = int(round(g / 63.0 * 255.0)) % 256
        self._b = int(round(b / 63.0 * 255.0)) % 256

    @staticmethod
    def from_hex(hex_str):
        c = Color()

        if hex_str[0] == '#':
            hex_str = hex_str[1:]

        if len(hex_str) == 6:
            r = int(hex_str[0:2], 16)
            g = int(hex_str[2:4], 16)
            b = int(hex_str[4:6], 16)
            c.set_rgb((r, g, b))
        elif len(hex_str) == 3:
            r = int(hex_str[0], 16) * 0x11
            g = int(hex_str[1], 16) * 0x11
            b = int(hex_str[2], 16) * 0x11
            c.set_rgb((r, g, b))
        else:
            assert False

        return c

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
        return round(self._r / 255.0, 5), round(self._g / 255.0, 5), round(self._b / 255.0, 5)

    def to_pd(self):
        return -4096 * int(round(self._r * (63 / 255.0))) \
               - 64 * int(round(self._g * (63 / 255.0))) \
               - 1 * int(round(self._b * (63 / 255.0))) - 1

    def to_hex_str(self):
        return "#{0:02X}{1:02X}{2:02X}".format(self._r, self._g, self._b)

    def __str__(self):
        res = colored("RGB[%i,%i,%i]" % (self._r, self._g, self._b), "green")
        return res

    def __eq__(self, other):
        return self.compare(other)


def color_from_str(value):
    c = Color()

    if isinstance(value, int):
        c.from_pd(value)
    elif isinstance(value, six.string_types):
        if value[0] == '#':
            return Color.from_hex(value)
        else:
            c.from_pd(value)
    else:
        assert False

    return c


class CoreGui(PdObject):
    POS_LEFT, POS_RIGHT, POS_TOP, POS_BOTTOM = (0, 1, 2, 3)

    @classmethod
    def is_coregui(cls, name):
        return name in ("bng", "tgl", "floatatom", "symbolatom",
                        "nbx", "hslider", "vslider",  "vsl", "hsl", "vu",
                        "hrd", "vrd", "hradio", "vradio")

    def __init__(self, name, x, y, args, **kwargs):
        PdObject.__init__(self, name, x, y, 0, 0, args)
        self._send = kwargs.get("send", "empty")
        self._receive = kwargs.get("receive", "empty")
        self._label = kwargs.get("label", "empty")
        self._label_xoff = int(kwargs.get("label_xoff", 17))
        self._label_yoff = int(kwargs.get("label_yoff", 7))
        self._font_type = int(kwargs.get("font_type", 0))
        self._font_size = int(kwargs.get("font_size", 10))
        self._bg_color = color_from_str(kwargs.get("bg_color", -262144))
        self._fg_color = color_from_str(kwargs.get("fg_color", -1))
        self._label_color = color_from_str(kwargs.get("label_color", -1))

    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, v):
        self._label = v

    @property
    def send(self):
        return self._send

    @send.setter
    def send(self, v):
        self._send = v

    def no_label(self):
        return not self._label or self.label == "empty"

    @property
    def receive(self):
        return self._receive

    @receive.setter
    def receive(self, v):
        self._receive = v

    def __str__(self):
        return "[GUI:%-36s {x:%i,y:%i,id:%i}" % (self.name + "]", self._x, self._y, self._id)

    def bgcolor(self):
        return self._bg_color.rgb_float()

    def fgcolor(self):
        return self._fg_color.rgb_float()

    def lbcolor(self):
        return self._label_color.rgb_float()

    def inlets(self):
        return [XLET_GUI]

    def outlets(self):
        return [XLET_GUI]

    def traverse(self, visitor):
        assert isinstance(visitor, AbstractVisitor)

        if visitor.skip_core_gui(self):
            return

        visitor.visit_core_gui(self)

    def draw_bbox(self, painter, **kwargs):
        vertexes = (
            (self.x, self.y),
            (0, self.height),
            (self.width, 0),
            (0, -self.height)
        )

        painter.draw_poly(vertexes, fill=self.bgcolor(), outline=(0, 0, 0), **kwargs)

    def show_inlets(self):
        return not self.receive or self.receive == "empty"

    def show_outlets(self):
        return not self.send or self.send == "empty"

    def draw_xlets(self, painter):
        if self.show_inlets():
            painter.draw_inlets(self.inlets(), self.x, self.y, self.width)
        if self.show_outlets():
            painter.draw_outlets(self.outlets(), self.x, self.bottom, self.width)

    def draw_label(self, painter):
        if not self.no_label():
            lx, ly = self._get_label_xy()
            ly += self._font_size / 2  # TODO hardcoded
            painter.draw_text(lx, ly, self.label,
                              color=self.lbcolor(),
                              font_size=self._font_size,  # FIXME! hardcoded font family
                              font="Menlo")

    def draw_on_parent(self):
        return True

    def _get_label_xy(self):
        return self.x + self._label_xoff, self.y + self._label_yoff  # font height correction

    def _get_label_pos(self, pos):
        if isinstance(pos, int):
            if pos not in (self.POS_LEFT, self.POS_TOP, self.POS_BOTTOM, self.POS_RIGHT):
                logging.warning("invalid label position: {0:d}".format(pos))
                return None

            return pos
        elif isinstance(pos, six.string_types):
            lmap = {"left": self.POS_LEFT,
                    "right": self.POS_RIGHT,
                    "top": self.POS_TOP,
                    "bottom": self.POS_BOTTOM}

            if pos.lower() in lmap:
                return lmap[pos.lower()]
            else:
                logging.warning("invalid label position: {0:s}".format(pos))
                return None
        else:
            logging.warning("invalid label position: {0:s}".format(str(pos)))
            return None

    def to_atoms(self):
        return {}
