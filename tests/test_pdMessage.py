#!/usr/bin/env python

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


# -*- coding: utf-8 -*-
from unittest import TestCase

__author__ = 'Serge Poltavski'

from pdmessage import *


class TestPdMessage(TestCase):
    def test_init(self):
        m = PdMessage(0, 0, "sample message".split())
        self.assertEqual(m.name, "msg")
        self.assertEqual(m.outlets(), [PdObject.XLET_MESSAGE])

    def test_draw(self):
        class P:
            def draw_message(self, m):
                self._msg = m

        m = PdMessage(0, 0, "sample message".split())
        p = P()

        self.assertEqual(hasattr(p, "_msg"), False)
        m.draw(p)
        self.assertEqual(hasattr(p, "_msg"), True)

    def test_visitor(self):
        class V:
            def visit_message(self, m):
                self._msg = m

        m = PdMessage(0, 0, "sample message".split())
        v = V()

        self.assertEqual(hasattr(v, "_msg"), False)
        m.traverse(v)
        self.assertEqual(hasattr(v, "_msg"), True)

    def test_str__(self):
        m = PdMessage(1, 1, "sample message".split())
        self.assertEqual(str(m), "[sample message(                          {x:1,y:1,id:-1}")


    def test_inlets(self):
        m = PdMessage(0, 0, "sample message".split())
        self.assertEqual(m.inlets(), [PdObject.XLET_MESSAGE])

    def test_outlets(self):
        m = PdMessage(0, 0, "sample message".split())
        self.assertEqual(m.outlets(), [PdObject.XLET_MESSAGE])
