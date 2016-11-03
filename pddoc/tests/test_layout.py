#!/usr/bin/env python
# coding=utf-8

# Copyright (C) 2014 by Serge Poltavski                                 #
#   serge.poltavski@gmail.com                                            #
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
from pddoc.layout import *


class TestLayout(unittest.TestCase):
    def test_parent(self):
        l = Layout(Layout.HORIZONTAL)
        self.assertEqual(l.parent(), None)
        l2 = Layout(Layout.VERTICAL)
        l2.set_parent(l)
        self.assertEqual(l2.parent(), l)

    def test_count(self):
        l = Layout(Layout.HORIZONTAL)
        i = LayoutItem()
        self.assertEqual(l.count(), 0)
        l.add_item(i)
        self.assertEqual(l.count(), 1)

    def test_add_item(self):
        l = Layout(Layout.HORIZONTAL)
        i = LayoutItem()
        l.add_item(i)
        self.assertEqual(l.item(0), i)
        i2 = LayoutItem()
        l.add_item(i2)
        self.assertEqual(l.item(0), i)
        self.assertEqual(l.item(1), i2)

        lv = Layout(Layout.VERTICAL)
        iv = LayoutItem()
        lv.add_item(iv)
        self.assertEqual(lv.item(0), iv)

    def test_add_vitem(self):
        lv = Layout(Layout.VERTICAL)
        i = LayoutItem(0, 0, 10, 10)
        lv.add_item(i)
        self.assertEqual(lv.item(0).brect(), (0, 0, 10, 10))
        lv.add_item(i)
        self.assertEqual(lv.item(0).brect(), (0, 0, 10, 10))
        self.assertEqual(lv.item(1).brect(), (0, 10, 10, 10))
        lv.add_item(i)
        lv.add_item(i)
        self.assertEqual(lv.item(3).brect(), (0, 30, 10, 10))
        self.assertEqual(lv.brect(), (0, 0, 10, 40))
        lv.add_item(LayoutItem(0, 0, 20, 20))
        self.assertEqual(lv.brect(), (0, 0, 20, 60))

        lh = Layout(Layout.HORIZONTAL)
        ih = LayoutItem(0, 0, 10, 10)
        lh.add_item(ih)
        self.assertEqual(lh.item(0).brect(), (0, 0, 10, 10))
        lh.add_item(ih)
        self.assertEqual(lh.item(0).brect(), (0, 0, 10, 10))
        self.assertEqual(lh.item(1).brect(), (10, 0, 10, 10))
        lh.add_item(ih)
        self.assertEqual(lh.item(2).brect(), (20, 0, 10, 10))

    def test_move_by(self):
        lv = Layout(Layout.VERTICAL)
        i = LayoutItem(0, 0, 10, 10)
        lv.add_item(i)
        lv.add_item(i)
        lv.move_by(10, 10)
        self.assertEqual(lv.item(0).brect(), (10, 10, 10, 10))
        self.assertEqual(lv.item(1).brect(), (10, 20, 10, 10))

    def test_move_by2(self):
        lv = Layout(Layout.VERTICAL)
        iv = LayoutItem(0, 0, 10, 10)
        lv.add_item(iv)

        lv2 = Layout(Layout.VERTICAL)
        iv2 = LayoutItem(0, 0, 10, 10)
        lv2.add_item(iv2)
        lv2.add_item(iv2)

        lv.add_layout(lv2)

        self.assertEqual(iv.brect(), (0, 0, 10, 10))
        self.assertEqual(lv.item(1).brect(), (0, 10, 10, 20))
        self.assertEqual(lv.item(1).item(0).brect(), (0, 10, 10, 10))
        self.assertEqual(lv.item(1).item(1).brect(), (0, 20, 10, 10))

    def test_brect(self):
        lv = Layout(Layout.VERTICAL)
        self.assertEqual(lv.brect(), (0, 0, 0, 0))

    def test_nested(self):
        lv = Layout(Layout.VERTICAL)
        lh = Layout(Layout.HORIZONTAL)
        lv.add_layout(lh)
        lv.add_layout(lh)

        self.assertNotEqual(lv.item(0), lv.item(1))

    def test_add_layout(self):
        lv = Layout(Layout.VERTICAL)
        iv = LayoutItem(0, 0, 100, 100)
        lv.add_item(iv)

        lh = Layout(Layout.HORIZONTAL)
        ih = LayoutItem(0, 0, 50, 50)
        lh.add_item(ih)
        lh.add_item(ih)
        lh.add_item(ih)
        self.assertEqual(lh.item(0).brect(), (0, 0, 50, 50))
        self.assertEqual(lh.item(1).brect(), (50, 0, 50, 50))
        self.assertEqual(lh.item(2).brect(), (100, 0, 50, 50))

        lv.add_layout(lh)
        self.assertEqual(lh.item(0).brect(), (0, 100, 50, 50))
        self.assertEqual(lh.item(1).brect(), (50, 100, 50, 50))
        self.assertEqual(lh.item(2).brect(), (100, 100, 50, 50))

    def test_add_vlayout(self):
        lh = Layout(Layout.HORIZONTAL)
        ih = LayoutItem(0, 0, 50, 50)
        lh.add_item(ih)
        lh.add_item(ih)
        lh.add_item(ih)
        self.assertEqual(lh.item(0).brect(), (0, 0, 50, 50))
        self.assertEqual(lh.item(1).brect(), (50, 0, 50, 50))
        self.assertEqual(lh.item(2).brect(), (100, 0, 50, 50))

        lv = Layout(Layout.VERTICAL)
        iv = LayoutItem(0, 0, 100, 100)
        lv.add_item(iv)

        lh.add_layout(lv)
        self.assertEqual(iv.brect(), (150, 0, 100, 100))

    def test_str(self):
        lh = Layout(Layout.HORIZONTAL)
        i = LayoutItem(0, 0, 10, 10)
        lh.add_item(i)
        lh.add_item(i)
        lh.add_item(i)

        s = str(lh)

        lv = Layout(Layout.HORIZONTAL)
        iv = LayoutItem(0, 0, 10, 10)
        lv.add_item(iv)

        s = str(lv)


class TestLayoutItem(unittest.TestCase):
    def test_str(self):
        li = LayoutItem(1, 2, 3, 4)
        s = str(li)
        self.assertEqual("(1,2,3x4)", s)
        self.assertEqual(1, li.left())
        self.assertEqual(1, li.x())
        self.assertEqual(2, li.top())
        self.assertEqual(3, li.width())
        self.assertEqual(4, li.height())
        self.assertEqual(4, li.right())
        self.assertEqual(6, li.bottom())

    def test_move_by(self):
        li = LayoutItem(10, 20, 30, 40)
        li.move_by(1, 2)
        self.assertEqual((11, 22, 30, 40), li.brect())


if __name__ == "__main__":
    unittest.main()

