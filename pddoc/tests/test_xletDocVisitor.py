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
from pddoc.xletdocvisitor import XletDocVisitor
from pddoc.parser import parse_xml
from pddoc.docobject import DocObject
from pddoc.pd.obj import PdObject
import os

CWD = os.path.dirname(__file__)


class TestXletDocVisitor(TestCase):
    def setUp(self):
        self._xml = parse_xml(os.path.join(CWD, "test_xlet_doc_visitor.pddoc"))
        self.assertTrue(self._xml is not None)
        self._doc_obj = DocObject()
        self._doc_obj.from_xml(self._xml.getroot()[0])
        self.XLET_DB = os.path.join(CWD, "test_xlet_doc_visitor-xlet_db.txt")

    def tearDown(self):
        if os.path.exists(self.XLET_DB):
            os.remove(self.XLET_DB)

    def traverse(self, v):
        self._doc_obj.traverse(v)

    def test_inlets_begin(self):
        v = XletDocVisitor()
        self.traverse(v)
        self.assertEqual(v.inlet_types(), [1, 0])
        self.assertTrue(os.path.exists(self.XLET_DB))
        with open(self.XLET_DB, "r") as f:
            txt = f.read().strip()
            self.assertEqual(txt, "test_xlet_doc_visitor\t\t~.\t\t~..")

        obj = PdObject("test_xlet_doc_visitor")
        self.assertEqual(obj.inlets(), [1, 0])
        self.assertEqual(obj.outlets(), [1, 0, 0])
        PdObject.remove_object_xlet_info("test_xlet_doc_visitor")

    def test_outlets_begin(self):
        v = XletDocVisitor(write_to_file=False, add_to_mem_db=False)
        self.traverse(v)
        self.assertEqual(v.outlet_types(), [1, 0, 0])
        self.assertFalse(os.path.exists(self.XLET_DB))

        obj = PdObject("test_xlet_doc_visitor")
        self.assertEqual(obj.inlets(), [])
        self.assertEqual(obj.outlets(), [])
