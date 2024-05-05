#!/usr/bin/env python
# coding=utf-8
# Copyright (C) 2014 by Serge Poltavski                                 #
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

import textwrap
from typing import List

from .abstractvisitor import AbstractVisitor
from .canvas import Canvas
from .comment import Comment
from .message import Message
from .obj import BaseObject, PdObject


class BRectCalculator(AbstractVisitor):
    def __init__(self):
        from pddoc.cairopainter import CairoPainter
        self._cairo = CairoPainter(1, 1, None, "png")
        self._bboxes: List[tuple[int, int, int, int]] = []

    def clear(self):
        self._bboxes = []

    @property
    def bboxes(self):
        return self._bboxes

    def brect(self):
        left = min(self._bboxes, key=lambda o: o[0])[0]
        top = min(self._bboxes, key=lambda o: o[1])[1]
        right = max(self._bboxes, key=lambda o: o[0] + o[2])
        right = right[0] + right[2]
        bottom = max(self._bboxes, key=lambda o: o[1] + o[3])
        bottom = bottom[1] + bottom[3]

        return left, top, right - left, bottom - top

    def object_brect(self, obj: PdObject):
        if obj.is_fixed_size():
            return obj.x, obj.y, obj.width, obj.height

        if obj.fixed_width:
            lines = textwrap.wrap(obj.to_string().ljust(obj.fixed_width, "."), obj.fixed_width)
            obj_str = "\n".join(lines)
            w, h = self._cairo.box_size(obj_str)
        else:
            w, h = self._cairo.box_size(obj.to_string())

        return int(round(obj.x)), int(round(obj.y)), int(round(w)), int(round(h))

    @staticmethod
    def break_lines(text: str, width: int = 61):
        lines = []
        for line in textwrap.wrap(text, width, break_long_words=False, break_on_hyphens=False):
            line = ";\n".join(line.split(";")).split("\n")
            for subl in line:
                if subl.strip():
                    lines.append(subl.strip())

        return lines

    def text_brect(self, text: str, line_width: int = 61):
        lines = self.break_lines(text, width=line_width)

        max_w = 0
        max_h = 0
        for line in lines:
            w, h = self._cairo.text_size(line)
            max_w = max(max_w, w)
            max_h = max(max_h, h)

        return 0, 0, int(round(max_w * 1.06)), int(round(len(lines) * max_h * 1.08))

    def comment_brect(self, comment: Comment):
        wd = 61
        if comment.line_width():
            wd = comment.line_width()
        return self.text_brect(comment.text(), line_width=wd)

    def subpatch_brect(self, cnv: Canvas):
        assert cnv.type == Canvas.TYPE_SUBPATCH

        txt = "pd " + cnv.args_to_string()
        w, h = self._cairo.box_size(txt)
        return cnv.x, cnv.y, int(round(w)), int(round(h))

    def box_brect(self, boxstr: str):
        w, h = self._cairo.box_size(boxstr)
        return 0, 0, int(round(w)), int(round(h))

    def string_brect(self, string: str, font_size):
        w, h = self._cairo.text_size(string, font_size)
        return 0, 0, int(round(w)), int(round(h))

    def message_brect(self, message: Message):
        w, h = self._cairo.message_size(message.to_string())
        return int(message.x), int(message.y), int(round(w)), int(round(h))

    def visit_object(self, obj: PdObject):
        bbox = self.object_brect(obj)
        obj.set_width(bbox[2])
        obj.set_height(bbox[3])
        self._bboxes.append(bbox)

    def visit_message(self, msg: Message):
        bbox = self.message_brect(msg)
        msg.set_width(bbox[2])
        msg.set_height(bbox[3])
        self._bboxes.append(bbox)

    def visit_comment(self, comment: Comment):
        (x, y, w, h) = self.comment_brect(comment)
        self._bboxes.append((comment.x, comment.y, w, h))

    def visit_core_gui(self, gui: BaseObject):
        self._bboxes.append((gui.x, gui.y, gui.width, gui.height))

    def visit_graph(self, g):
        pass

    def visit_connection(self, c):
        pass

    def visit_canvas_end(self, canvas):
        pass

    def visit_canvas_begin(self, canvas):
        pass
