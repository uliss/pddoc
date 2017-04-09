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

from .message import Message
from .canvas import Canvas
from .abstractvisitor import AbstractVisitor


class BRectCalculator(AbstractVisitor):
    def __init__(self):
        from pddoc.cairopainter import CairoPainter
        self._cairo = CairoPainter(1, 1, None, "png")
        self._bboxes = []

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

    def object_brect(self, obj):
        if obj._fixed_size:
            return obj.x, obj.y, obj.width, obj.height

        w, h = self._cairo.box_size(obj.to_string())
        return obj.x, obj.y, int(w), int(h)

    def text_brect(self, text):
        lines = []
        for line in textwrap.wrap(text, 59):
            line = ";\n".join(line.split(";")).split("\n")
            for subl in line:
                if subl:
                    lines.append(subl.strip())

        max_w = 0
        max_h = 0
        for line in lines:
            w, h = self._cairo.text_size(line)
            max_w = max(max_w, w)
            max_h = max(max_h, h)

        return 0, 0, int(max_w * 1.1), int(len(lines) * max_h)

    def comment_brect(self, comment):
        return self.text_brect(comment.text())

    def subpatch_brect(self, cnv):
        assert isinstance(cnv, Canvas)
        assert cnv.type == Canvas.TYPE_SUBPATCH

        txt = "pd " + cnv.args_to_string()
        w, h = self._cairo.box_size(txt)
        return cnv.x, cnv.y, int(w), int(h)

    def string_brect(self, string, font_size):
        w, h = self._cairo.text_size(string, font_size)
        return 0, 0, w, h

    def message_brect(self, message):
        assert isinstance(message, Message)
        w, h = self._cairo.message_size(message.to_string())
        return message.x, message.y, int(w), int(h)

    def visit_object(self, obj):
        bbox = self.object_brect(obj)
        obj.set_width(bbox[2])
        obj.set_height(bbox[3])
        self._bboxes.append(bbox)

    def visit_message(self, msg):
        bbox = self.message_brect(msg)
        msg.set_width(bbox[2])
        msg.set_height(bbox[3])
        self._bboxes.append(bbox)

    def visit_comment(self, comment):
        (x, y, w, h) = self.comment_brect(comment)
        self._bboxes.append((comment.x, comment.y, w, h))

    def visit_core_gui(self, gui):
        self._bboxes.append((gui.x, gui.y, gui.width, gui.height))

    def visit_graph(self, g):
        pass

    def visit_connection(self, c):
        pass

    def visit_canvas_end(self, canvas):
        pass

    def visit_canvas_begin(self, canvas):
        pass
