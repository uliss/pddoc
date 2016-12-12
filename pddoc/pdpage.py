#!/usr/bin/env python
# coding=utf-8

#   Copyright (C) 2016 by Serge Poltavski                                 #
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

from pd.canvas import Canvas
from pd.gcanvas import GCanvas
from pd.coregui import Color
from pd.brectcalculator import BRectCalculator
from pd.externals.pddp.pddplink import PddpLink
from pd.comment import Comment
import re


class PdPageStyle(object):
    HRULE_COLOR = Color(200, 200, 200)
    SECTION_FONT_SIZE = 17


class PdPage(object):
    WIDTH = 600
    HEIGHT = 500

    brect_calc = BRectCalculator()

    def __init__(self, title, width=600, height=500):
        self._title = title.replace(' ', '_')
        self._width = int(width)
        self._height = int(height)
        self._canvas = Canvas(0, 0, self._width, self._height)
        self._pd = {} # subpatches dict

    @property
    def canvas(self):
        return self._canvas

    def make_background(self, x, y, width, height, color):
        cnv = GCanvas(x, y, width=width, height=height, size=1)
        cnv._bg_color = color
        return cnv

    def make_hrule(self, x, y, width, height=1, color=Color(200, 200, 200)):
        return self.make_background(x, y, width, height, color)

    def make_styled_hrule(self, y):
        return self.make_hrule(20, y, width=self._width - 24, color=PdPageStyle.HRULE_COLOR)

    def make_label(self, x, y, txt, font_size, color=Color.black(), bg_color=Color.white()):
        w, h = self.brect_calc.string_brect(txt, font_size)[2:]

        cnv = GCanvas(x, y, width=w, height=h, size=1, font_size=font_size, label_xoff=0, label_yoff=font_size/2)
        cnv.label = txt.replace(' ', '_')
        cnv._label_color = color
        cnv._bg_color = bg_color
        return cnv

    def make_section(self, y, txt, font_size=PdPageStyle.SECTION_FONT_SIZE):
        l = self.make_label(20, y, txt, font_size)
        r = self.make_styled_hrule(y + l.height + 10)
        return l, r

    def make_link(self, x, y, url, name):
        return PddpLink(x, y, url, name)

    def make_txt(self, txt, x, y):
        txt = re.sub(' +', ' ', txt)
        txt = txt.replace('.', '\\.')
        txt = txt.replace(',', ' \\,')
        return Comment(x, y, txt.split(' '))

    def make_subpatch(self, name, x, y, w, h):
        pd = Canvas(x, y, w, h, name=name)
        pd.type = Canvas.TYPE_SUBPATCH
        self._pd[name] = pd
        return pd

    def add_to_subpatch(self, name, obj):
        assert name in self._pd
        self._pd[name].append_object(obj)

    def group_brect(self, seq):
        for el in seq:
            el.calc_brect()

        br = map(lambda x: x.brect(), seq)
        left = min(lambda x: x[0], br)
        top = min(lambda x: x[1], br)
        right = max(lambda x: x[0] + x[2], br)
        bottom = max(lambda x: x[1] + x[3], br)
        return left, top, right - left, bottom - top

    def move_to_x(self, seq, x):
        for o in seq:
            o.x = x

    def move_to_y(self, seq, y):
        for o in seq:
            o.y = y

    def move_to(self, seq, x, y):
        for o in seq:
            o.x = x
            o.y = y

    def move_by(self, seq, x, y):
        for o in seq:
            o.x += x
            o.y += y

    def move_by_x(self, seq, x):
        for o in seq:
            o.x += x

    def move_by_y(self, seq, y):
        for o in seq:
            o.x += y

    def bottom(self):
        for o in self._canvas.objects:
            o.calc_brect()

        max(lambda x: x.bottom, self._canvas.objects)

    def place_under(self, old_obj, new_obj, y_off=0):
        old_obj.calc_brect()
        new_obj.y = old_obj.bottom + y_off

    def place_right_side(self, old_obj, new_obj, x_space=0):
        old_obj.calc_brect()
        new_obj.x = old_obj.right + x_space

    def place_top_right(self, obj, x_pad=0, y_pad=0):
        obj.calc_brect()
        obj.x = self._width - obj.width - x_pad
        obj.y = y_pad

    def place_bottom_right(self, obj, x_pad=0, y_pad=0):
        obj.calc_brect()
        obj.x = self._width - obj.width - x_pad
        obj.y = self._height - obj.height - y_pad

    def place_bottom_left(self, obj, x_pad=0, y_pad=0):
        obj.calc_brect()
        obj.x = x_pad
        obj.y = self._height - obj.height - y_pad

    def place_in_row(self, seq, x, x_pad=0):
        for o in seq:
            o.calc_brect()

        for o in seq:
            o.x = x
            x += o.width + x_pad

    def place_in_col(self, seq, y, y_pad=0):
        for o in seq:
            o.calc_brect()

        for o in seq:
            o.y = y
            y += o.height + y_pad
