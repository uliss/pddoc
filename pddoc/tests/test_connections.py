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

from unittest import TestCase
from pddoc.pd.parser import PdParser
from pddoc.cairopainter import *
from pddoc.pddrawer import *
 
__author__ = 'Serge Poltavski'


class TestConnections(TestCase):
    def test_connections0(self):
        parser = PdParser()
        parser.parse("connections.pd")

        canvas = parser.canvas

        cp = CairoPainter(canvas.width, canvas.height, "out/connections.png")
        drawer = PdDrawer()
        drawer.draw(canvas, cp)

    def test_connections1(self):
        parser = PdParser()
        parser.parse("connections1.pd")

        canvas = parser.canvas

        cp = CairoPainter(canvas.width, canvas.height, "out/connections1.png")
        drawer = PdDrawer()
        drawer.draw(canvas, cp)

        # canvas._print_connections()
