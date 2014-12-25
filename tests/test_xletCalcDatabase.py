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

from xletcalcdatabase import *
from pdobject import *


class TestXletCalcDatabase(TestCase):
    def test_inlets(self):
        xd = XletCalcDatabase()
        self.assertEqual(xd.inlets(12), [])
        pdo = PdObject("mtof")
        self.assertEqual(xd.inlets(pdo), [PdObject.XLET_MESSAGE])
        pdo.name = "not-exists"
        self.assertEqual(xd.inlets(pdo), [])
        pdo.name = "min"
        self.assertEqual(xd.inlets(pdo), [PdObject.XLET_MESSAGE] * 2)
        pdo.name = "line"
        self.assertEqual(xd.inlets(pdo), [PdObject.XLET_MESSAGE] * 3)

        pdo.name = "s"
        self.assertEqual(xd.inlets(pdo), [PdObject.XLET_MESSAGE] * 2)
        pdo.append_arg(12)
        self.assertEqual(xd.inlets(pdo), [PdObject.XLET_MESSAGE])
        pdo.name = "s~"
        self.assertEqual(xd.inlets(pdo), [PdObject.XLET_SOUND])

        pdo.name = "dac~"
        pdo._args = []
        self.assertEqual(xd.inlets(pdo), [PdObject.XLET_SOUND] * 2)
        pdo.append_arg(1)
        self.assertEqual(xd.inlets(pdo), [PdObject.XLET_SOUND] * 1)
        pdo.append_arg(2)
        self.assertEqual(xd.inlets(pdo), [PdObject.XLET_SOUND] * 2)
        pdo.append_arg(3)
        self.assertEqual(xd.inlets(pdo), [PdObject.XLET_SOUND] * 3)
        pdo.append_arg(4)
        self.assertEqual(xd.inlets(pdo), [PdObject.XLET_SOUND] * 4)

        pdo.name = "osc~"
        self.assertEqual(xd.inlets(pdo), [PdObject.XLET_SOUND, PdObject.XLET_MESSAGE])
        pdo._args = []
        pdo.name = "*~"
        self.assertEqual(xd.inlets(pdo), [PdObject.XLET_SOUND] * 2)
        pdo.append_arg(0.5)
        self.assertEqual(xd.inlets(pdo), [PdObject.XLET_SOUND, PdObject.XLET_MESSAGE])

    def test_outlets(self):
        xd = XletCalcDatabase()
        self.assertEqual(xd.inlets(12), [])
        pdo = PdObject("osc~")
        self.assertEqual(xd.outlets(pdo), [PdObject.XLET_SOUND])
        pdo.name = "mtof"
        self.assertEqual(xd.outlets(pdo), [PdObject.XLET_MESSAGE])