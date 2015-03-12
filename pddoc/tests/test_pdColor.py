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

import unittest

__author__ = 'Serge Poltavski'

from pddoc.pd.pdcoregui import *


class TestPdColor(unittest.TestCase):
    def setUp(self):
        self.c = PdColor()

    def test_black(self):
        self.assertEqual(PdColor.black().rgb(), (0, 0, 0))

    def test_white(self):
        self.assertEqual(PdColor.white().rgb(), (255, 255, 255))
        self.assertEqual(PdColor.white().rgb_float(), (1, 1, 1))

    def test_rgb(self):
        c = PdColor(0.1, 0.2, 0.3)
        self.assertEqual(c.rgb(), (0.1, 0.2, 0.3))

    def test_from_pd(self):
        c = PdColor(0, 0, 0)
        c2 = PdColor()
        c2.from_pd(c.to_pd())
        self.assertEqual(c.compare(c2), True)

        c.set_rgb((255, 0, 0))
        c2.from_pd(c.to_pd())
        self.assertEqual(c == c2, True)

        c.set_rgb((255, 255, 0))
        c2.from_pd(c.to_pd())
        self.assertEqual(c == c2, True)

        c.set_rgb((255, 255, 255))
        c2.from_pd(c.to_pd())
        self.assertEqual(c == c2, True)

        for v in xrange(1, 4096, 4):
            c.from_pd(-v)
            self.assertEqual(c.to_pd(), -v)

    def test_compare(self):
        c = PdColor(0.1, 0, 0)
        self.assertEqual(self.c.compare(c), False)

    def test_is_black(self):
        self.assertEqual(self.c.is_black(), True)
        self.assertEqual(PdColor.white().is_black(), False)

    def test_to_float(self):
        c = PdColor(255, 255, 0)
        self.assertEqual(c.rgb_float(), (1.0, 1.0, 0))

    def test_to_pd(self):
        c = PdColor(0, 0, 0)
        self.assertEqual(c.to_pd(), -1)
        c.set_rgb((255, 0, 0))
        self.assertEqual(c.to_pd(), -258049)

        self.assertEqual(PdColor(0, 0, 0).to_pd(), -1)
        self.assertEqual(PdColor(0, 0, 4).to_pd(), -2)
        self.assertEqual(PdColor(0, 0, 8).to_pd(), -3)
        self.assertEqual(PdColor(0, 0, 168).to_pd(), -43)
        self.assertEqual(PdColor(0, 0, 255).to_pd(), -64)
        self.assertEqual(PdColor(0, 4, 0).to_pd(), -64 - 1)
        self.assertEqual(PdColor(0, 8, 0).to_pd(), -(64 * 2) - 1)
        self.assertEqual(PdColor(0, 12, 0).to_pd(), -(64 * 3) - 1)
        self.assertEqual(PdColor(0, 12, 4).to_pd(), -(64 * 3) - 2)
        self.assertEqual(PdColor(4, 0, 0).to_pd(), -4096 - 1)

    def test_to_hex_str(self):
        c = PdColor()
        self.assertEqual("#000000", c.to_hex_str())
        c = c.white()
        self.assertEqual("#FFFFFF", c.to_hex_str())
        c.set_rgb((0xDE, 0xAD, 0xBE))
        self.assertEqual("#DEADBE", c.to_hex_str())

    def test_from_hex(self):
        c = PdColor.from_hex("FA1234")
        self.assertEqual(c.to_hex_str(), "#FA1234")
        c = PdColor.from_hex("#123456")
        self.assertEqual(c.to_hex_str(), "#123456")
        c = PdColor.from_hex("#FAC")
        self.assertEqual(c.to_hex_str(), "#FFAACC")