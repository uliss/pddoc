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

from .pd.canvas import Canvas
from .pd.gcanvas import GCanvas
from .pd.coregui import Color
from .pd.brectcalculator import BRectCalculator
from .pd.externals.pddp.pddplink import PddpLink
from .pd.externals.ceammc.ui_link import UILink
from .pd.comment import Comment
from .pd.pdexporter import PdExporter
import re


class PdPageStyle(object):
    HRULE_COLOR = Color(200, 200, 200)
    SECTION_FONT_SIZE = 17
    SECTION_FONT_COLOR = Color(50, 50, 50)
    HEADER_HEIGHT = 40
    HEADER_FONT_SIZE = 20
    HEADER_BG_COLOR = Color(100, 100, 100)
    HEADER_FONT_COLOR = Color(0, 255, 255)
    FOOTER_HEIGHT = 40
    FOOTER_BG_COLOR = Color(200, 200, 200)
    INFO_BG_COLOR = Color(240, 255, 255)


class PdPage(object):
    brect_calc = BRectCalculator()

    def __init__(self, title, width=600, height=500):
        self._title = title.replace(' ', '_')
        self._width = int(width)
        self._height = int(height)
        self._canvas = Canvas(0, 0, self._width, self._height, font_size=12)
        self._canvas.type = Canvas.TYPE_WINDOW
        self._pd = {} # subpatches dict

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

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
        return self.make_hrule(20, y, width=self._width - 30, color=PdPageStyle.HRULE_COLOR)

    def make_label(self, x, y, txt, font_size, color=Color.black(), bg_color=Color.white()):
        w, h = self.brect_calc.string_brect(txt, font_size)[2:]

        cnv = GCanvas(x, y, width=w + 10, height=h * 1.6, size=5, font_size=font_size, label_xoff=4,
                      label_yoff=font_size - 4)
        cnv.label = txt.replace(' ', '_')
        cnv._label_color = color
        cnv._bg_color = bg_color
        return cnv

    def make_header(self, title):
        cnv = GCanvas(1, 1,
                      width=self._width - 3,
                      height=PdPageStyle.HEADER_HEIGHT,
                      size=5,
                      font_size=PdPageStyle.HEADER_FONT_SIZE,
                      label_xoff=PdPageStyle.HEADER_FONT_SIZE,
                      label_yoff=PdPageStyle.HEADER_FONT_SIZE)
        cnv.label = title.replace(' ', '_')
        cnv._label_color = PdPageStyle.HEADER_FONT_COLOR
        cnv._bg_color = PdPageStyle.HEADER_BG_COLOR
        return cnv

    def make_footer(self, bottom, height=PdPageStyle.FOOTER_HEIGHT):
        y = max(bottom, self._height - height - 2)
        cnv = GCanvas(1, y,
                      width=self._width - 3,
                      height=height,
                      size=5)

        cnv._bg_color = PdPageStyle.FOOTER_BG_COLOR
        return cnv

    def make_section_label(self, y, txt, font_size=PdPageStyle.SECTION_FONT_SIZE):
        return self.make_label(20, y, txt, font_size, PdPageStyle.SECTION_FONT_COLOR)

    def make_section(self, y, txt):
        l = self.make_section_label(y, txt)
        r = self.make_styled_hrule(y + l.height + 10)
        return l, r, self.group_brect([l, r])

    def make_link(self, x, y, url, name):
        kw = {'@url': url, '@title': name}
        return UILink(x, y + 3, **kw)

    def make_header_alias_link(self, objname, title):
        lnk = self.make_link(0, 0, "{0}-help.pd".format(objname), "[{0}]".format(title))
        lnk.set_bg_color(PdPageStyle.HEADER_BG_COLOR)
        return lnk

    def make_txt(self, txt, x, y):
        if txt:
            txt = re.sub(' +', ' ', txt)
            #  match only number with end dot: 1. - used for enums
            txt = re.sub('(\d+)\\.(?!\d)', '\\1\\.', txt)
            txt = re.sub(' *, *', ' \\, ', txt)
        else:
            txt = ""

        return Comment(x, y, txt.split(' '))

    def make_subpatch(self, name, x, y, w, h):
        pd = Canvas(x, y, w, h, name=name)
        pd.type = Canvas.TYPE_SUBPATCH
        self._pd[name] = pd
        return pd

    def add_header(self, title):
        h = self.make_header(title)
        h.calc_brect()
        self._canvas.append_object(h)
        return h

    def add_to_subpatch(self, name, obj):
        assert name in self._pd
        self._pd[name].append_object(obj)

    def add_pd_txt(self, pd, txt, x, y):
        t = self.make_txt(txt, x, y)
        pd.append_object(t)
        t.calc_brect()
        return t

    def add_txt(self, txt, x, y):
        return self.add_pd_txt(self._canvas, txt, x, y)

    def add_link(self, txt, url, x, y):
        lnk = self.make_link(x, y, url, txt)
        self._canvas.append_object(lnk)
        return lnk

    def add_bg_txt(self, txt, color, x, y):
        t = self.make_txt(txt, x, y)
        t.calc_brect()
        bg = self.make_background(x, y, t.width + 8, t.height + 8, color=color)
        self._canvas.append_object(bg)
        self._canvas.append_object(t)
        return t, bg

    def add_description(self, txt, y):
        d = self.add_bg_txt(txt, PdPageStyle.INFO_BG_COLOR, 0, y)
        br = self.group_brect(d)
        self.move_to_x(d, self._width - br[2] - 20)

    def add_section(self, title, y):
        l, r, brect = self.make_section(y, title)
        self._canvas.append_object(l)
        self._canvas.append_object(r)
        return l, r, brect

    def add_subpatch_txt(self, name, txt, x, y):
        return self.add_pd_txt(self._pd[name], txt, x, y)

    def add_subpatch_obj(self, name, obj):
        self._pd[name].append_object(obj)
        obj.calc_brect()
        return obj

    def append_object(self, obj):
        self._canvas.append_object(obj)
        obj.calc_brect()
        return obj

    def append_list(self, obj):
        for o in obj:
            self.append_object(o)

    def group_brect(self, seq):
        for el in seq:
            el.calc_brect()

        left = min(seq, key=lambda x: x.left).left
        top = min(seq, key=lambda x: x.top).top
        right = max(seq, key=lambda x: x.right).right
        bottom = max(seq, key=lambda x: x.bottom).bottom
        return left, top, right - left, bottom - top

    def move_to_x(self, seq, x):
        if len(seq) < 1:
            return

        x_off = x - seq[0].x

        for o in seq:
            o.x += x_off

    def move_to_y(self, seq, y):
        if len(seq) < 1:
            return

        y_off = y - seq[0].y
        for o in seq:
            o.y += y_off

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

    def to_string(self):
        pd_exporter = PdExporter()
        self._canvas.traverse(pd_exporter)
        return '\n'.join(pd_exporter.result[:-1])
