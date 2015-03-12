#!/usr/bin/env python
# coding=utf-8

# Copyright (C) 2014 by Serge Poltavski                                 #
# serge.poltavski@gmail.com                                             #
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

from unittest import TestCase

__author__ = 'Serge Poltavski'

from pddoc.pd.brectcalculator import *
from pddoc.pd.pdparser import *
from pddoc.pddrawer import *
from pddoc.cairopainter import *


class TestBRectCalculator(TestCase):
    def test_calc_brect(self):
        p = PdParser()
        p.parse("objects.pd")
        self.assertTrue(p.canvas)

        br = BRectCalculator()

        p.canvas.traverse(br)
        self.assertEqual(br.brect(), (26, 23, 366, 227))

        pnt = CairoPainter(223, 227, "out/objects.png", "png", xoffset=-26, yoffset=-23)
        d = PdDrawer()
        d.draw(p.canvas, pnt)

        for b in br.bboxes:
            p = 5
            pnt.draw_rect(b[0] - p, b[1] - p, b[2] + 2 * p, b[3] + 2 * p, width=1, color=(1, 0, 0))

    def test_comment_brect(self):
        br = BRectCalculator()
        self.assertEqual(br.text_brect("test"), (0, 0, 24, 12))
        self.assertEqual(br.text_brect("test; line break"), (0, 0, 60, 24))

    def test_comment(self):
        p = PdParser()
        p.parse("comments.pd")
        self.assertTrue(p.canvas)

        br = BRectCalculator()

        p.canvas.traverse(br)
        self.assertEqual(br.brect(), (67, 35, 348.0, 110))

        pnt = CairoPainter(p.canvas.width, p.canvas.height, "out/comments.png", "png")
        d = PdDrawer()
        d.draw(p.canvas, pnt)

        for b in br.bboxes:
            p = 0
            pnt.draw_rect(b[0] - p, b[1] - p, b[2] + 2 * p, b[3] + 2 * p, width=1, color=(1, 0, 0))

        bbox = br.brect()
        p = 5
        pnt.draw_rect(bbox[0] - p, bbox[1] - p, bbox[2] + p * 2, bbox[3] + p * 2, color=(0, 0, 1))
