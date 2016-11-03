#!/usr/bin/env python
# coding=utf-8

# Copyright (C) 2015 by Serge Poltavski                                 #
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

from unittest import TestCase

from pddoc.pd.objetcbrectvisitor import ObjectBRectVisitor
from pddoc.pd import PdObject
import pddoc.pd as pd
from pddoc.cairopainter import CairoPainter


class TestObjectBRectVisitor(TestCase):
    def test_visit_object(self):
        ov = ObjectBRectVisitor()

        self.assertTrue(ov.brect() is None)
        ov.add_brect((10, 10, 20, 30))
        self.assertEqual(ov.brect(), (10, 10, 20, 30))
        ov.clean()
        pdo = PdObject("osc~")
        self.assertTrue(pdo.is_null())
        ov.visit_object(pdo)
        self.assertEqual(ov.brect(), (0, 0, 35, 17))
        self.assertFalse(pdo.is_null())

    def test_visit_canvas(self):
        p = pd.Parser()
        self.assertTrue(p.parse('misc.pd'))
        ov = ObjectBRectVisitor()

        p.canvas.traverse(ov)
        # self.assertEqual(ov.brect(), (31, 25, 755, 207))

        painter = CairoPainter(p.canvas.width, p.canvas.height, "out/TestObjectBRectVisitor.png")
        p.canvas.draw(painter)
        x, y, w, h = ov.brect()
        painter.draw_rect(x, y, w, h, color=(1, 0, 0))
