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

import unittest

from pddoc.cairopainter import CairoPainter
from pddoc.pddrawer import PdDrawer
import pddoc.pd as pd


class TestCairoPainter(unittest.TestCase):
    def test_simple(self):
        parser = pd.Parser()
        # f = "/Applications/Pd-extended.app/Contents/Resources/doc/5.reference/float-help.pd"
        f = "/Applications/Pd-extended.app/Contents/Resources/doc/5.reference/intro-help.pd"
        parser.parse(f)

        canvas = parser.canvas
        canvas.height = 4700

        cp = CairoPainter(canvas.width, canvas.height, "out/output_cairo.png")
        drawer = PdDrawer()
        drawer.draw(canvas, cp)

        cp2 = CairoPainter(canvas.width, canvas.height, "out/output_cairo.pdf", fmt="pdf")
        drawer.draw(canvas, cp2)
