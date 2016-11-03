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
import sys
import StringIO

__author__ = 'Serge Poltavski'

from pddoc.pddrawer import *
from pddoc.pdpainter import *
import pddoc.pd as pd


class TestPdDrawer(TestCase):
    def test_draw(self):
        # suppress output
        cout = sys.stdout
        sys.stdout = StringIO.StringIO()

        parser = pd.Parser()
        parser.parse("simple.pd")

        painter = PdPainter()

        d = PdDrawer()
        canvas = parser.canvas
        self.assertTrue(canvas)
        d.draw(parser.canvas, painter)

        # restore output
        sys.stdout = cout
