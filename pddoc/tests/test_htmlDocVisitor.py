#!/usr/bin/env python

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


# -*- coding: utf-8 -*-
from unittest import TestCase

__author__ = 'Serge Poltavski'

from pddoc.htmldocvisitor import *
from pddoc.pdcanvas import *
import os


class TestHtmlDocVisitor(TestCase):
    def test_init(self):
        v = HtmlDocVisitor()

    def test_render(self):
        v = HtmlDocVisitor()
        self.assertTrue(v.render())

    def test_generate_object_image(self):
        PATH = "out/object_undefined~.png"
        v = HtmlDocVisitor()
        v.generate_object_image("undefined~")
        self.assertTrue(os.path.exists(PATH))
        os.remove(PATH)

    def test_generate_images(self):
        v = HtmlDocVisitor()
        v._title = "testobj"
        v._aliases.append("tobj")
        v.generate_images()
        self.assertTrue(os.path.exists("out/object_testobj.png"))
        self.assertTrue(os.path.exists("out/object_tobj.png"))
        os.remove("out/object_testobj.png")
        os.remove("out/object_tobj.png")

    def test_place_pd_objects(self):
        v = HtmlDocVisitor()
        pd_canvas = PdCanvas(0, 0, 100, 50, name="10")
        v._cur_canvas = pd_canvas
        pdo = PdObject("float")
        pd_canvas.append_object(pdo)
        self.assertEqual(pdo.x, 0)
        self.assertEqual(pdo.y, 0)
        self.assertEqual(pdo.width, 0)
        self.assertEqual(pdo.height, 0)

        li = LayoutItem(10, 20, 30, 40)
        setattr(pdo, "layout", li)

        v.place_pd_objects()
        self.assertEqual(pdo.x, 10)
        self.assertEqual(pdo.y, 20)
        self.assertEqual(pdo.width, 0)
        self.assertEqual(pdo.height, 0)

    def test_doc2obj(self):
        v = HtmlDocVisitor()
        do = DocPdobject()
        do._comment = "comment"
        do._id = "float"
        do._offset = 10
        do._name = "float"
        do._args = "3.1415926"
        pdo = v.doc_obj2pd_obj(do)

        self.assertEqual(pdo.x, 0)
        self.assertEqual(pdo.y, 0)
        self.assertEqual(pdo.width, 0)
        self.assertEqual(pdo.height, 0)

        self.assertTrue(hasattr(pdo, "layout"))
        self.assertEqual(pdo.layout.x(), 10)
        self.assertEqual(pdo.layout.y(), 0)
        self.assertEqual(pdo.layout.width(), 95.0)
        self.assertEqual(pdo.layout.height(), 17)