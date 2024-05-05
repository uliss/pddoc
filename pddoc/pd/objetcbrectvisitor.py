#!/usr/bin/env python
# coding=utf-8

#   Copyright (C) 2015 by Serge Poltavski                                 #
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

from typing import Optional

from .abstractvisitor import AbstractVisitor
from .brectcalculator import BRectCalculator
from .canvas import Canvas
from .comment import Comment
from .message import Message
from .obj import PdObject


class ObjectBRectVisitor(AbstractVisitor):
    _brect_calc = BRectCalculator()

    def __init__(self):
        self._left = None
        self._right = None
        self._top = None
        self._bottom = None

    @property
    def brect_calc(self):
        ObjectBRectVisitor._brect_calc.clear()
        return ObjectBRectVisitor._brect_calc

    def add_brect(self, brect: tuple[float, float, float, float]):
        x, y, w, h = brect
        if self._left:
            self._left = min(self._left, x)
        else:
            self._left = x

        if self._top:
            self._top = min(self._top, y)
        else:
            self._top = y

        if self._right:
            self._right = max(self._right, x + w)
        else:
            self._right = x + w

        if self._bottom:
            self._bottom = max(self._bottom, y + h)
        else:
            self._bottom = y + h

    def clean(self):
        self._left = None
        self._right = None
        self._top = None
        self._bottom = None

    def brect(self) -> Optional[tuple[float, float, float, float]]:
        if self._left is None \
                or self._right is None \
                or self._top is None \
                or self._bottom is None:
            return None

        return self._left, self._top, self._right - self._left, self._bottom - self._top

    def visit_connection(self, conn):
        pass

    def visit_comment(self, comment: Comment):
        if not comment.width or not comment.height:
            br = self.brect_calc.comment_brect(comment)
            comment.set_width(br[2])
            comment.set_height(br[3])

        self.add_brect(comment.brect())

    def visit_object(self, obj: PdObject):
        if not obj.width or not obj.height:
            br = self.brect_calc.object_brect(obj)
            obj.set_width(br[2])
            obj.set_height(br[3])

        self.add_brect(obj.brect())

    def visit_message(self, msg: Message):
        if not msg.width or not msg.height:
            br = self.brect_calc.message_brect(msg)
            msg.set_width(br[2])
            msg.set_height(br[3])

        self.add_brect(msg.brect())

    def skip_children(self, cnv: Canvas):
        if cnv.type != Canvas.TYPE_WINDOW:
            return True

    def skip_connection(self, conn):
        return True

    def visit_canvas_begin(self, canvas: Canvas):
        if canvas.type != Canvas.TYPE_SUBPATCH:
            return

        # subpatch only
        # if not canvas.width or not canvas.height:
        br = self.brect_calc.subpatch_brect(canvas)
        canvas.set_width(br[2])
        canvas.set_height(br[3])

        self.add_brect(canvas.brect())

    def visit_canvas_end(self, canvas: Canvas):
        pass

    def visit_core_gui(self, gui):
        self.add_brect(gui.brect())
