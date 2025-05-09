#!/usr/bin/env python
# coding=utf-8
import re
from typing import List

from . import Rectangle, Point
from .pd.baseobject import BaseObject
from .pd.brectcalculator import BRectCalculator
from .pd.canvas import Canvas
from .pd.comment import Comment
from .pd.coregui import Color
from .pd.externals.ceammc.ui_link import UILink
from .pd.gcanvas import GCanvas
from .pd.obj import PdObject
from .pd.pdexporter import PdExporter


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


class PdPageStyle(object):
    HRULE_COLOR = Color(200, 200, 200)
    HRULE_LEFT_MARGIN = 20
    HRULE_RIGHT_MARGIN = 20
    SECTION_FONT_SIZE = 17
    SECTION_FONT_COLOR = Color(50, 50, 50)
    HEADER_HEIGHT = 40
    HEADER_FONT_SIZE = 20
    HEADER_BG_COLOR = Color(100, 100, 100)
    HEADER_FONT_COLOR = Color(0, 255, 255)
    FOOTER_HEIGHT = 40
    FOOTER_BG_COLOR = Color(200, 200, 200)
    INFO_BG_COLOR = Color(240, 255, 255)
    MAIN_BG_COLOR = Color(250, 250, 250)
    HEADER_RIGHT_MARGIN = 20


class PdPage(object):
    def __init__(self, title: str, width: int = 700, height: int = 500):
        self._brect_calc = BRectCalculator()
        self._title = title.replace(' ', '_')
        self._width = int(width)
        self._height = int(height)
        self._canvas = Canvas(0, 0, self._width, self._height, font_size=12)
        self._canvas.type = Canvas.TYPE_WINDOW
        self._pd = {}  # subpatches dict

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @property
    def canvas(self):
        return self._canvas

    @staticmethod
    def make_background(x: int, y: int, width: int, height: int, color: Color):
        cnv = GCanvas(x, y, width=width, height=height, size=1)
        cnv._bg_color = color
        return cnv

    def make_hrule(self, x: int, y: int, width: int, height: int = 1, color: Color = Color(200, 200, 200)) -> GCanvas:
        return self.make_background(x, y, width, height, color)

    def make_styled_hrule(self, y: int) -> GCanvas:
        return self.make_hrule(20, y,
                               width=self._width - (PdPageStyle.HRULE_LEFT_MARGIN + PdPageStyle.HRULE_RIGHT_MARGIN),
                               color=PdPageStyle.HRULE_COLOR)

    def brect_string(self, txt: str, font_size: int):
        return self._brect_calc.string_brect(txt, font_size)

    def brect_box(self, txt: str):
        return self._brect_calc.box_brect(txt)

    def brect_obj(self, obj: PdObject):
        return self._brect_calc.object_brect(obj)

    def make_label(self, x: int, y: int, txt: str, font_size,
                   **kwargs) -> GCanvas:
        w, h = self.brect_string(txt, font_size)[2:]

        cnv = GCanvas(x, y, width=kwargs.get('width', w + 10), height=kwargs.get('height', h * 1.6),
                      size=kwargs.get('size', 5),
                      font_size=font_size,
                      label_xoff=kwargs.get('label_xoff', 4),
                      label_yoff=kwargs.get('label_yoff', h - 4))

        if kwargs.get('replace_ws', True):
            cnv.label = txt.replace(' ', '_')
        else:
            cnv.label = txt.replace(' ', '\\ ')
        cnv._label_color = kwargs.get('color', PdPageStyle.SECTION_FONT_COLOR)
        cnv._bg_color = kwargs.get('bg_color', Color.white())
        return cnv

    def make_header(self, title: str, replace_ws: bool = True):
        cnv = GCanvas(1, 1,
                      width=self._width - PdPageStyle.HEADER_RIGHT_MARGIN,
                      height=PdPageStyle.HEADER_HEIGHT,
                      size=5,
                      font_size=PdPageStyle.HEADER_FONT_SIZE,
                      label_xoff=PdPageStyle.HEADER_FONT_SIZE,
                      label_yoff=PdPageStyle.HEADER_FONT_SIZE)
        if replace_ws:
            cnv.label = title.replace(' ', '_')
        else:
            cnv.label = title.replace(' ', r'\ ')
        cnv._label_color = PdPageStyle.HEADER_FONT_COLOR
        cnv._bg_color = PdPageStyle.HEADER_BG_COLOR
        return cnv

    def make_footer(self, bottom, height=PdPageStyle.FOOTER_HEIGHT):
        y = max(bottom, self._height - height - 2)
        cnv = GCanvas(1, y,
                      width=self._width - PdPageStyle.HEADER_RIGHT_MARGIN,
                      height=height,
                      size=5)

        cnv._bg_color = PdPageStyle.FOOTER_BG_COLOR
        return cnv

    def make_section_label(self, y: int, txt: str, font_size: int = PdPageStyle.SECTION_FONT_SIZE,
                           **kwargs):
        return self.make_label(20, y, txt, font_size, **kwargs)

    # returns label object, hrule object and their bbox
    def make_section(self, y: int, txt: str, **kwargs):
        label = self.make_section_label(y, txt, **kwargs)
        r = self.make_styled_hrule(y + label.height + 10)
        return label, r, self.group_brect([label, r])

    @staticmethod
    def make_link(x: int, y: int, url: str, name: str):
        kw = {'@url': url, '@title': name}
        return UILink(x, y + 3, **kw)

    def make_header_alias_link(self, objname: str, title: str):
        lnk = self.make_link(0, 0, "{0}-help.pd".format(objname), "[{0}]".format(title))
        lnk.set_bg_color(PdPageStyle.HEADER_BG_COLOR)
        return lnk

    @staticmethod
    def make_txt(txt: str, x: int, y: int, **kwargs):
        if txt:
            #  match only number with end dot: 1. - used for enums
            txt = re.sub(r'(\d+)\.(?!\d)', r'\1\.', txt)
            txt = re.sub(r' *, *', ' \\, ', txt)
            txt = re.sub(r'\s+', ' ', txt)
        else:
            txt = ""

        return Comment(x, y, txt.split(' '), **kwargs)

    def make_subpatch(self, name: str, x: int, y: int, w: int, h: int):
        pd = Canvas(x, y, w, h, name=name)
        pd.type = Canvas.TYPE_SUBPATCH
        self._pd[name] = pd
        return pd

    def add_header(self, title: str, replace_ws: bool = True):
        h = self.make_header(title, replace_ws)
        h.calc_brect()
        self._canvas.append_object(h)
        return h

    def add_to_subpatch(self, name, obj):
        assert name in self._pd
        self._pd[name].append_object(obj)

    def add_pd_txt(self, pd, txt: str, x: int, y: int, **kwargs):
        t = self.make_txt(txt, x, y, **kwargs)
        pd.append_object(t)
        t.calc_brect()
        return t

    def add_txt(self, txt: str, x: int, y: int, **kwargs):
        return self.add_pd_txt(self._canvas, txt, x, y, **kwargs)

    def add_link(self, txt: str, url: str, x: int, y: int):
        lnk = self.make_link(x, y, url, txt)
        self._canvas.append_object(lnk)
        return lnk

    def add_bg_txt(self, txt: str, color: Color, x: int, y: int) -> tuple[Comment, GCanvas]:
        t = self.make_txt(txt, x, y)
        t.calc_brect()
        bg = self.make_background(x, y, t.width + 8, t.height + 8, color=color)
        self._canvas.append_object(bg)
        self._canvas.append_object(t)
        return t, bg

    def add_description(self, txt: str, y: int) -> Rectangle:
        (comm, bg) = self.add_bg_txt(txt, PdPageStyle.INFO_BG_COLOR, 0, y)
        bg.x = self._width - (bg.width + PdPageStyle.HEADER_RIGHT_MARGIN)
        comm.x = bg.x + 5  # comment x-padding from background rect
        return bg.bounding_rect()

    # return label object, hrule and their bbox
    def add_section(self, title: str, y: int):
        l, r, brect = self.make_section(y, title)
        self._canvas.append_object(l)
        self._canvas.append_object(r)
        return l, r, brect

    def add_subpatch_txt(self, name, txt: str, x: int, y: int):
        return self.add_pd_txt(self._pd[name], txt, x, y)

    def add_subpatch_obj(self, name: str, obj):
        self._pd[name].append_object(obj)
        obj.calc_brect()
        return obj

    def append_object(self, obj: PdObject):
        self._canvas.append_object(obj)
        obj.calc_brect()
        return obj

    def append_list(self, objects: List[PdObject]):
        for o in objects:
            self.append_object(o)

    @staticmethod
    def group_brect(seq: List[PdObject]):
        for el in seq:
            el.calc_brect()

        left = min(seq, key=lambda x: x.left).left
        top = min(seq, key=lambda x: x.top).top
        right = max(seq, key=lambda x: x.right).right
        bottom = max(seq, key=lambda x: x.bottom).bottom
        return left, top, right - left, bottom - top

    @staticmethod
    def move_to_x(seq: list, x: float):
        if len(seq) < 1:
            return

        x_off = x - seq[0].x

        for o in seq:
            o.x += x_off

    @staticmethod
    def move_to_y(seq: list, y: float):
        if len(seq) < 1:
            return

        y_off = y - seq[0].y
        for o in seq:
            o.y += y_off

    @staticmethod
    def move_to(seq: list, x: float, y: float):
        for o in seq:
            o.x = x
            o.y = y

    @staticmethod
    def move_by(seq: list, x: float, y: float):
        for o in seq:
            o.x += x
            o.y += y

    @staticmethod
    def move_by_x(seq: list, x: float):
        for o in seq:
            o.x += x

    @staticmethod
    def move_by_y(seq: list, y: float):
        for o in seq:
            o.x += y

    def bottom(self):
        for o in self._canvas.objects:
            o.calc_brect()

        max(lambda x: x.bottom, self._canvas.objects)

    @staticmethod
    def place_under(old_obj: PdObject, new_obj: BaseObject, y_off: int = 0):
        old_obj.calc_brect()
        new_obj.y = old_obj.bottom + y_off

    @staticmethod
    def place_right_side(old_obj: PdObject, new_obj: BaseObject, x_space: int = 0):
        old_obj.calc_brect()
        new_obj.x = old_obj.right + x_space

    def place_top_right(self, obj: PdObject, x_pad: int = 0, y_pad: int = 0):
        obj.calc_brect()
        obj.x = self._width - obj.width - x_pad
        obj.y = y_pad

    def place_bottom_right(self, obj: PdObject, x_pad: int = 0, y_pad: int = 0):
        obj.calc_brect()
        obj.x = self._width - obj.width - x_pad
        obj.y = self._height - obj.height - y_pad

    def place_bottom_left(self, obj: PdObject, x_pad: int = 0, y_pad: int = 0):
        obj.calc_brect()
        obj.x = x_pad
        obj.y = self._height - obj.height - y_pad

    @staticmethod
    def place_in_row(seq, x: int, x_pad: int = 0):
        for o in seq:
            o.calc_brect()

        for o in seq:
            o.x = x
            x += o.width + x_pad

    @staticmethod
    def place_in_col(seq: List[PdObject], y: int, y_pad: int = 0) -> Rectangle:
        for o in seq:
            o.calc_brect()

        for o in seq:
            o.y = y
            y += o.height + y_pad

        if len(seq) > 0:
            return Rectangle.from_points(Point(seq[0].x, seq[0].y), Point(seq[-1].right, seq[-1].bottom))
        else:
            return Rectangle(Point(0, y), 0, 0)

    def to_string(self):
        pd_exporter = PdExporter()
        self._canvas.traverse(pd_exporter)
        return '\n'.join(pd_exporter.result[:-1])
