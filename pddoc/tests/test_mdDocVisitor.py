#!/usr/bin/env python

# Copyright (C) 2021 by Serge Poltavski                                   #
# serge.poltavski@gmail.com                                               #
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

from pddoc.markdownvisitor import *
from pddoc.pdlayout import *
from pddoc.docobject import *


class TestMdDocVisitor(TestCase):
    def test_init(self):
        v = MarkdownVisitor()

    def test_render(self):
        v = MarkdownVisitor()
        self.assertTrue(v.render())

    def test_place_pd_objects(self):
        v = PdLayout()
        pd_canvas = Canvas(0, 0, 100, 50, name="10")
        v._canvas = pd_canvas
        pdo = PdObject("float")
        pd_canvas.append_object(pdo)
        self.assertEqual(pdo.x, 0)
        self.assertEqual(pdo.y, 0)
        self.assertEqual(pdo.width, 0)
        self.assertEqual(pdo.height, 0)

        li = LayoutItem(10, 20, 30, 40)
        setattr(pdo, "layout", li)

        v.update()
        self.assertEqual(pdo.x, 10)
        self.assertEqual(pdo.y, 20)
        self.assertEqual(pdo.width, 0)
        self.assertEqual(pdo.height, 0)

    def test_doc2obj(self):
        v = PdLayout()
        do = DocPdobject()
        do._comment = "comment"
        do._id = "float"
        do._offset = 10
        do._name = "float"
        do._args = "3.1415926"
        pdo = v.doc2obj(do)

        self.assertEqual(pdo.x, 0)
        self.assertEqual(pdo.y, 0)
        self.assertEqual(pdo.width, 0)
        self.assertEqual(pdo.height, 0)

        self.assertTrue(hasattr(pdo, "layout"))
        self.assertEqual(pdo.layout.x(), 10)
        self.assertEqual(pdo.layout.y(), 0)
        self.assertEqual(pdo.layout.width(), 114)
        self.assertEqual(pdo.layout.height(), 18)

    def test_doc2msg(self):
        v = PdLayout()
        dmsg = DocPdmessage()
        dmsg._comment = "comment"
        dmsg._id = "float"
        dmsg._offset = 10
        dmsg._text = "message"
        pdm = v.doc2msg(dmsg)

        self.assertEqual(pdm.x, 0)
        self.assertEqual(pdm.y, 0)
        self.assertEqual(pdm.width, 0)
        self.assertEqual(pdm.height, 0)

        self.assertTrue(hasattr(pdm, "layout"))
        self.assertEqual(pdm.layout.x(), 10)
        self.assertEqual(pdm.layout.y(), 0)
        self.assertEqual(pdm.layout.width(), 61)
        self.assertEqual(pdm.layout.height(), 18)

    def test_comment2pd(self):
        v = PdLayout()
        pdc = v.comment2pd_comment("simple comment")
        self.assertTrue(isinstance(pdc, Comment))

        self.assertEqual(pdc.x, 0)
        self.assertEqual(pdc.y, 0)
        self.assertEqual(pdc.width, 0)
        self.assertEqual(pdc.height, 0)

        self.assertTrue(hasattr(pdc, "layout"))
        self.assertEqual(pdc.layout.x(), 0)
        self.assertEqual(pdc.layout.y(), 0)
        self.assertEqual(pdc.layout.width(), 105)
        self.assertEqual(pdc.layout.height(), 15)

        pdc = v.comment2pd_comment(" ".join(["long comment"] * 40))
        self.assertTrue(isinstance(pdc, Comment))
        self.assertEqual(pdc.x, 0)
        self.assertEqual(pdc.y, 0)
        self.assertEqual(pdc.width, 0)
        self.assertEqual(pdc.height, 0)
        self.assertTrue(hasattr(pdc, "layout"))
        self.assertEqual(pdc.layout.x(), 0)
        self.assertEqual(pdc.layout.y(), 0)
        self.assertEqual(pdc.layout.width(), 449)
        self.assertEqual(pdc.layout.height(), 136)
