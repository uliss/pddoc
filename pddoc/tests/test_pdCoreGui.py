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

from unittest import TestCase

__author__ = 'Serge Poltavski'

from pddoc.cairopainter import *
from pddoc.pd.coregui import CoreGui
from pddoc.pd.parser import Parser
from pddoc.pddrawer import *

tgl = ['15', '0', 'empty', 'empty', 'empty', '17', '7', '0', '10', '-262144', '-1', '-1', '0', '1']


class TestPdCoreGui(TestCase):
    def test_init(self):
        pco = CoreGui("tgl", 0, 0, tgl)
        self.assertEqual(pco.inlets(), [XLET_GUI])
        self.assertEqual(pco.outlets(), [XLET_GUI])
        self.assertEqual(pco.send, "empty")
        self.assertEqual(pco.receive, "empty")

    def test_str__(self):
        pco = CoreGui("tgl", 5, 6, tgl)
        self.assertEqual(str(pco), "[GUI:tgl]                                 {x:5,y:6,id:-1}")

    def test_draw(self):
        p = Parser()
        p.parse("core_gui.pd")
        canvas = p.canvas
        self.assertTrue(canvas)
        self.assertEqual(canvas.width, 600)
        self.assertEqual(canvas.height, 500)
        painter = CairoPainter(canvas.width, canvas.height, "out/core_gui.png")
        drawer = PdDrawer()
        drawer.draw(canvas, painter)

    def test_is_core_gui(self):
        self.assertFalse(CoreGui.is_coregui("ui.scope"))
        self.assertTrue(CoreGui.is_coregui("vsl"))
        self.assertFalse(CoreGui.is_coregui("unknown"))
