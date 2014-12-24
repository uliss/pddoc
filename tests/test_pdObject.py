# /usr/bin/env python

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
import unittest

__author__ = 'Serge Poltavski'

from pdobject import *


class TestPdObject(unittest.TestCase):
    def test_init(self):
        po = PdObject("pd")
        self.assertEqual(po.id, -1)
        self.assertEqual(len(po.args), 0)

    @unittest.expectedFailure
    def test_init_fail(self):
        po = PdObject("")

    def test_id(self):
        po = PdObject("pd")
        self.assertEqual(po.id, -1)
        po.id = "5"
        self.assertEqual(po.id, 5)
        po.id = 2
        self.assertEqual(po.id, 2)

    def test_name(self):
        po = PdObject("pd")
        self.assertEqual(po.name, "pd")
        po.name = "import"
        self.assertEqual(po.name, "import")

    def test_args_to_string(self):
        po = PdObject("pd")
        self.assertEqual(po.args_to_string(), "")
        del (po)
        po = PdObject("tabread", 0, 0, 0, 0, ['\\$0-file', '1', '0', '-123'])
        self.assertEqual(po.args_to_string(), "$0-file 1 0 -123")

    def test_str__(self):
        po = PdObject("pd")
        self.assertEqual(str(po), "[pd]                                      {x:0,y:0,id:-1}")
        del (po)
        po = PdObject("s", 10, 0, 20, 16, ["\\$0-out"])
        po.id = 1
        self.assertEqual(str(po), "[s $0-out]                                {x:10,y:0,id:1}")

    def test_inlets(self):
        po = PdObject("float")
        po._inlets.append(PdObject.XLET_MESSAGE)
        self.assertEqual(po.inlets(), [PdObject.XLET_MESSAGE] * 2)
        po._xlets_method = None
        self.assertEqual(po.inlets(), [])
        po._xlets_method = PdObject.XMETHOD_EXPLICIT
        self.assertEqual(po.inlets(), [PdObject.XLET_MESSAGE])

    def test_draw(self):
        class P:
            def draw_object(self, o):
                self._o = o

        po = PdObject("float")
        painter = P()

        self.assertEqual(hasattr(painter, "_o"), False)
        po.draw(painter)
        self.assertEqual(hasattr(painter, "_o"), True)

    def test_traverse(self):
        class T:
            def visit_object(self, o):
                self._o = o

        po = PdObject("float")
        visitor = T()

        self.assertEqual(hasattr(visitor, "_o"), False)
        po.traverse(visitor)
        self.assertEqual(hasattr(visitor, "_o"), True)


