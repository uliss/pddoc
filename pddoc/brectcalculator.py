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

from pddrawstyle import *
import cairo
import textwrap
from pdcomment import *
from pdobject import *
from pdmessage import *


class BRectCalculator(object):
    def __init__(self):
        self._style = PdDrawStyle()
        self._ims = cairo.ImageSurface(cairo.FORMAT_ARGB32, 10, 10)
        self._cr = cairo.Context(self._ims)

        self.st_font_slant = cairo.FONT_SLANT_NORMAL
        self.st_font_weight = cairo.FONT_WEIGHT_NORMAL
        self.st_line_join = cairo.LINE_JOIN_ROUND
        self._cr.select_font_face(self._style.font_family, self.st_font_slant, self.st_font_weight)
        self._cr.set_font_size(self._style.font_size)

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
        assert isinstance(obj, PdObject)
        txt = obj.to_string()
        (x, y, width, height, dx, dy) = self._cr.text_extents(txt)

        w = max(width + self._style.obj_pad_x * 2, self._style.obj_min_width)
        h = self._style.obj_height
        return obj.x, obj.y, w, h

    def text_brect(self, text):
        lines = []
        for line in textwrap.wrap(text, 59):
            line = ";\n".join(line.split(";")).split("\n")
            for subl in line:
                if subl:
                    lines.append(subl.strip())

        maxwd = 0
        for line in lines:
            maxwd = max(maxwd, self._cr.text_extents(line)[2])

        height = len(lines) * self._style.font_size
        return 0, 0, maxwd, height

    def comment_brect(self, comment):
        assert isinstance(comment, PdComment)
        return self.text_brect(comment.text())

    def message_brect(self, message):
        assert  isinstance(message, PdMessage)
        (x, y, width, height, dx, dy) = self._cr.text_extents(message.to_string())
        w = width + self._style.obj_pad_x * 4
        h = self._style.obj_height
        return message.x, message.y, w, h

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
        pass

    def visit_graph(self, g):
        pass

    def visit_connection(self, c):
        pass