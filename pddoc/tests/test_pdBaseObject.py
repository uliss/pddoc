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
from pddoc.pdbaseobject import *


class TestPdBaseObject(unittest.TestCase):
    def test_init(self):
        pbo = PdBaseObject()
        self.assertEqual(pbo.is_null(), True)
        self.assertEqual(pbo.x, 0)
        self.assertEqual(pbo.get_x(), 0)

        del (pbo)

        pbo = PdBaseObject(1, 2, 3, 4)
        self.assertEqual(pbo.left, 1)
        self.assertEqual(pbo.right, 4)
        self.assertEqual(pbo.top, 2)
        self.assertEqual(pbo.bottom, 6)

        pbo.width = 20
        pbo.height = 10
        self.assertEqual(pbo.width, 20)
        self.assertEqual(pbo.height, 10)

    def test_x(self):
        pbo = PdBaseObject(2)
        self.assertEqual(pbo.x, 2)
        pbo.x = 3
        self.assertEqual(pbo.x, 3)
        self.assertEqual(pbo.get_x(), 3)

    def test_override(self):
        class A(PdBaseObject):
            def get_x(self):
                return 44

        pbo = A()
        self.assertEqual(pbo.x, 44)
        self.assertEqual(pbo.get_x(), 44)
        pbo.x = 100
        self.assertEqual(pbo.x, 44)
        pbo.set_x(100)
        self.assertEqual(pbo.x, 44)

    def test_brect(self):
        pbo = PdBaseObject(10, 20, 30, 40)
        self.assertEqual(pbo.brect(), (10, 20, 30, 40))
        pbo.move_by(2, 3)
        self.assertEqual(pbo.brect(), (12, 23, 30, 40))

    def test_xlets(self):
        pbo = PdBaseObject(10, 20, 30, 40)
        self.assertEqual(len(pbo.inlets()), 0)
        self.assertEqual(len(pbo.outlets()), 0)

    @unittest.expectedFailure
    def test_draw(self):
        pbo = PdBaseObject()
        pbo.draw(None)

    @unittest.expectedFailure
    def test_traverse(self):
        pbo = PdBaseObject()
        pbo.traverse(None)

    def test_unescape(self):
        self.assertEqual(PdBaseObject.unescape("\\;\\,\\$"), ";,$")
