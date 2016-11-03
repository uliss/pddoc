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

import pddoc.pd as pd


def make_pdo(name):
    a = name.split(" ")
    pdo = pd.PdObject(a[0], args=a[1:])
    return pdo


class TestXletCalcDatabase(TestCase):
    def test_inlets(self):
        xd = pd.XletCalculator()
        self.assertEqual(xd.inlets(12), [])
        pdo = pd.PdObject("mtof")
        self.assertEqual(xd.inlets(pdo), [pd.XLET_MESSAGE])
        pdo.name = "not-exists"
        self.assertEqual(xd.inlets(pdo), [])
        pdo.name = "min"
        self.assertEqual(xd.inlets(pdo), [pd.XLET_MESSAGE] * 2)
        pdo.name = "line"
        self.assertEqual(xd.inlets(pdo), [pd.XLET_MESSAGE] * 3)

        pdo.name = "s"
        self.assertEqual(xd.inlets(pdo), [pd.XLET_MESSAGE] * 2)
        pdo.append_arg(12)
        self.assertEqual(xd.inlets(pdo), [pd.XLET_MESSAGE])
        pdo.name = "s~"
        self.assertEqual(xd.inlets(pdo), [pd.XLET_SOUND])

        pdo.name = "dac~"
        pdo._args = []
        self.assertEqual(xd.inlets(pdo), [pd.XLET_SOUND] * 2)
        pdo.append_arg(1)
        self.assertEqual(xd.inlets(pdo), [pd.XLET_SOUND] * 1)
        pdo.append_arg(2)
        self.assertEqual(xd.inlets(pdo), [pd.XLET_SOUND] * 2)
        pdo.append_arg(3)
        self.assertEqual(xd.inlets(pdo), [pd.XLET_SOUND] * 3)
        pdo.append_arg(4)
        self.assertEqual(xd.inlets(pdo), [pd.XLET_SOUND] * 4)

        pdo.name = "osc~"
        self.assertEqual(xd.inlets(pdo), [pd.XLET_SOUND, pd.XLET_MESSAGE])
        pdo._args = []
        pdo.name = "*~"
        self.assertEqual(xd.inlets(pdo), [pd.XLET_SOUND] * 2)
        pdo.append_arg(0.5)
        self.assertEqual(xd.inlets(pdo), [pd.XLET_SOUND, pd.XLET_MESSAGE])
        pdo.name = "writesf~"
        pdo._args = []
        self.assertEqual(xd.inlets(pdo), [pd.XLET_SOUND])
        pdo.append_arg("4")
        self.assertEqual(xd.inlets(pdo), [pd.XLET_SOUND] * 4)
        pdo.name = "sprintf"
        pdo._args = []
        self.assertEqual(xd.inlets(pdo), [0] * 1)
        pdo.append_arg("%0.1f")
        self.assertEqual(xd.inlets(pdo), [0] * 1)
        pdo.append_arg("%%")
        self.assertEqual(xd.inlets(pdo), [0] * 1)
        pdo.append_arg("%s")
        self.assertEqual(xd.inlets(pdo), [0] * 2)
        pdo.append_arg("%02d")
        self.assertEqual(xd.inlets(pdo), [0] * 3)
        pdo.append_arg("%%")
        self.assertEqual(xd.inlets(pdo), [0] * 3)

    def test_outlets(self):
        xd = pd.XletCalculator()
        self.assertEqual(xd.inlets(12), [])
        pdo = pd.PdObject("osc~")
        self.assertEqual(xd.outlets(pdo), [pd.XLET_SOUND])
        pdo.name = "mtof"
        self.assertEqual(xd.outlets(pdo), [pd.XLET_MESSAGE])
        pdo.name = "writesf~"
        pdo.append_arg("1")
        self.assertEqual(xd.outlets(pdo), [])

        pdo.name = "sprintf"
        pdo._args = []
        self.assertEqual(xd.outlets(pdo), [0] * 0)
        pdo._args = ["test"]
        self.assertEqual(xd.outlets(pdo), [0] * 0)
        pdo._args = ["%%"]
        self.assertEqual(xd.outlets(pdo), [0] * 0)
        pdo._args = ["%02d"]
        self.assertEqual(xd.outlets(pdo), [0] * 1)

        pdo.name = "expr"
        pdo._args = ["$f1"]
        self.assertEqual(xd.outlets(pdo), [0] * 1)
        pdo.name = "expr"
        pdo._args = ["$f1;"]
        self.assertEqual(xd.outlets(pdo), [0] * 1)
        pdo._args = ["$f1; 2"]
        self.assertEqual(xd.outlets(pdo), [0] * 2)

    def test_xlets(self):
        xd = pd.XletCalculator()
        self.assertEqual(xd.inlets(make_pdo("sel")), [0] * 2)
        self.assertEqual(xd.inlets(make_pdo("sel .")), [0] * 2)
        self.assertEqual(xd.inlets(make_pdo("sel . .")), [0])
        self.assertEqual(xd.outlets(make_pdo("sel")), [0] * 2)
        self.assertEqual(xd.outlets(make_pdo("sel .")), [0] * 2)
        self.assertEqual(xd.outlets(make_pdo("sel . .")), [0] * 3)

        self.assertEqual(xd.inlets(make_pdo("send")), [0] * 2)
        self.assertEqual(xd.inlets(make_pdo("send .")), [0])
        self.assertEqual(xd.outlets(make_pdo("send")), [])

        self.assertEqual(xd.inlets(make_pdo("pack")), [0] * 2)
        self.assertEqual(xd.inlets(make_pdo("pack .")), [0])
        self.assertEqual(xd.inlets(make_pdo("pack . .")), [0] * 2)
        self.assertEqual(xd.inlets(make_pdo("pack . . .")), [0] * 3)
        self.assertEqual(xd.outlets(make_pdo("pack")), [0])

        self.assertEqual(xd.inlets(make_pdo("unpack")), [0])
        self.assertEqual(xd.outlets(make_pdo("unpack")), [0] * 2)
        self.assertEqual(xd.outlets(make_pdo("unpack .")), [0])
        self.assertEqual(xd.outlets(make_pdo("unpack . .")), [0] * 2)
        self.assertEqual(xd.outlets(make_pdo("unpack . . .")), [0] * 3)

        self.assertEqual(xd.inlets(make_pdo("t")), [0])
        self.assertEqual(xd.outlets(make_pdo("t")), [0] * 2)
        self.assertEqual(xd.outlets(make_pdo("t b")), [0])
        self.assertEqual(xd.outlets(make_pdo("t b b")), [0] * 2)
        self.assertEqual(xd.outlets(make_pdo("t b b b")), [0] * 3)

        self.assertEqual(xd.inlets(make_pdo("outlet")), [0])
        self.assertEqual(xd.outlets(make_pdo("outlet")), [])

        self.assertEqual(xd.outlets(make_pdo("ctlin")), [0] * 3)
        self.assertEqual(xd.outlets(make_pdo("ctlin 1")), [0] * 2)
        self.assertEqual(xd.outlets(make_pdo("ctlin 1 2")), [0] * 1)
        self.assertEqual(xd.outlets(make_pdo("ctlin 1 2 3 4 5")), [0] * 1)

        self.assertEqual(xd.inlets(make_pdo("mux~")), [1, 1])
        self.assertEqual(xd.outlets(make_pdo("mux~")), [1])
