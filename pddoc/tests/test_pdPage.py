#!/usr/bin/env python
# coding=utf-8

#   Copyright (C) 2016 by Serge Poltavski                                 #
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
from pddoc.pdpage import PdPage
from pddoc.pd.obj import PdObject


class TestPdPage(TestCase):
    def assertSeqProp(self, seq, func, pos):
        self.assertEqual(len(seq), len(pos))
        self.assertEqual(map(func, seq), pos)

    def assertXPos(self, seq, pos):
        self.assertSeqProp(seq, lambda x: x.x, pos)

    def assertYPos(self, seq, pos):
        self.assertSeqProp(seq, lambda x: x.y, pos)

    def assertWidth(self, seq, pos):
        self.assertSeqProp(seq, lambda x: x.width, pos)

    def assertHeight(self, seq, pos):
        self.assertSeqProp(seq, lambda x: x.height, pos)

    def obj(self, name="test", x=0, y=0, w=0, h=0):
        return PdObject(name, x, y, w, h)

    def objwh(self, w, h):
        return self.obj("test", 0, 0, w, h)

    def test_no_brect_recalc(self):
        o = PdObject("test", 10, 5, 0, 0)
        o.width = 150
        o.height = 60
        self.assertEqual(o.width, 150)
        self.assertEqual(o.height, 60)
        o.calc_brect()
        self.assertEqual(o.width, 150)
        self.assertEqual(o.height, 60)
        o.calc_brect(use_cached=False)
        self.assertEqual(o.width, 34)
        self.assertEqual(o.height, 17)

    def test_place_in_row(self):
        p = PdPage("sample")
        seq = [self.objwh(10, 5), self.objwh(12, 6), self.objwh(16, 7)]
        p.place_in_row(seq, 0, 0)
        self.assertWidth(seq, [10, 12, 16])
        self.assertHeight(seq, [5, 6, 7])
        self.assertYPos(seq, [0, 0, 0])
        self.assertXPos(seq, [0, 10, 22])

        p.place_in_row(seq, 10)
        self.assertXPos(seq, [10, 20, 32])

        p.place_in_row(seq, 10, 5)
        self.assertXPos(seq, [10, 25, 42])

    def test_place_in_col(self):
        p = PdPage("sample")
        seq = [self.objwh(5, 10), self.objwh(6, 12), self.objwh(7, 16)]
        p.place_in_col(seq, 0, 0)
        self.assertHeight(seq, [10, 12, 16])
        self.assertWidth(seq, [5, 6, 7])
        self.assertXPos(seq, [0, 0, 0])
        self.assertYPos(seq, [0, 10, 22])

        p.place_in_col(seq, 10)
        self.assertYPos(seq, [10, 20, 32])

        p.place_in_col(seq, 10, 5)
        self.assertYPos(seq, [10, 25, 42])

    def test_place_bottom_left(self):
        p = PdPage("sample", 600, 500)
        o = self.objwh(100, 20)
        p.place_bottom_left(o)
        self.assertEqual(o.x, 0)
        self.assertEqual(o.y, 480)

        p.place_bottom_left(o, 20)
        self.assertEqual(o.x, 20)
        self.assertEqual(o.y, 480)

        p.place_bottom_left(o, 20, 10)
        self.assertEqual(o.x, 20)
        self.assertEqual(o.y, 470)

    def test_place_bottom_right(self):
        p = PdPage("sample", 600, 500)
        o = self.objwh(100, 20)
        p.place_bottom_right(o)
        self.assertEqual(o.x, 500)
        self.assertEqual(o.y, 480)

        p.place_bottom_right(o, 10)
        self.assertEqual(o.x, 490)
        self.assertEqual(o.y, 480)

        p.place_bottom_right(o, 10, 15)
        self.assertEqual(o.x, 490)
        self.assertEqual(o.y, 465)

    def test_place_top_right(self):
        p = PdPage("sample", 600, 500)
        o = self.objwh(100, 20)
        p.place_top_right(o)
        self.assertEqual(o.x, 500)
        self.assertEqual(o.y, 0)

        p.place_top_right(o, 10)
        self.assertEqual(o.x, 490)
        self.assertEqual(o.y, 0)

        p.place_top_right(o, 10, 15)
        self.assertEqual(o.x, 490)
        self.assertEqual(o.y, 15)

    def test_place_right_side(self):
        p = PdPage("sample", 600, 500)
        o1 = self.obj(x=4, y=5, w=100, h=20)
        o2 = self.obj(x=2, y=100, w=100, h=20)
        p.place_right_side(o1, o2)
        self.assertEqual(o1.x, 4)
        self.assertEqual(o2.x, 104)
        self.assertEqual(o1.y, 5)
        self.assertEqual(o2.y, 100)

        p.place_right_side(o1, o2, 20)
        self.assertEqual(o1.x, 4)
        self.assertEqual(o2.x, 124)
        self.assertEqual(o1.y, 5)
        self.assertEqual(o2.y, 100)

    def test_group_brect(self):
        p = PdPage("sample", 600, 500)

        o1 = self.obj(x=4, y=5, w=100, h=20)
        o2 = self.obj(x=2, y=100, w=100, h=20)
        self.assertEqual(p.group_brect([o1, o2]), (2, 5, 102, 115))
