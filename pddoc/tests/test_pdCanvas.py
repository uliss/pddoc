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

from pddoc.pdcanvas import *
from pddoc.pdobject import *
import copy
from nologging import NoLogging


class TestPdCanvas(TestCase):
    def test_init(self):
        cnv = PdCanvas(0, 0, 100, 50)
        self.assertEqual(len(cnv.objects), 0)
        self.assertEqual(len(cnv.graphs), 0)
        self.assertEqual(len(cnv.connections), 0)
        self.assertEqual(cnv.type, cnv.TYPE_NONE)

    def test_name(self):
        cnv = PdCanvas(0, 0, 100, 50)
        self.assertEqual(cnv.name, "")
        cnv.name = "new"
        self.assertEqual(cnv.name, "new")

    def test_append_graph(self):
        cnv = PdCanvas(0, 0, 100, 50)
        f1 = PdObject("float")
        cnv.append_object(f1)
        self.assertEqual(f1.id, 0)

        graph = PdCanvas(0, 0, 10, 10)
        self.assertEqual(len(cnv.graphs), 0)
        self.assertRaises(AssertionError, cnv.append_graph, None)
        self.assertRaises(AssertionError, cnv.append_graph, cnv)
        self.assertRaises(AssertionError, cnv.append_graph, graph)
        graph.type = PdCanvas.TYPE_GRAPH
        cnv.append_graph(graph)
        self.assertEqual(len(cnv.objects), 2)

        self.assertEqual(cnv.objects[1], graph)
        self.assertEqual(graph.id, 1)

    def test_gen_id(self):
        cnv = PdCanvas(0, 0, 100, 50)
        oid = cnv.gen_object_id()
        self.assertEqual(oid, 0)
        oid = cnv.gen_object_id()
        self.assertEqual(oid, 1)
        oid = cnv.gen_object_id()
        self.assertEqual(oid, 2)

    def test_append_object(self):
        nout = NoLogging()
        cnv = PdCanvas(0, 0, 100, 50)
        pdo = PdObject("float")
        self.assertTrue(cnv.append_object(pdo))
        self.assertEqual(len(cnv.objects), 1)
        self.assertFalse(cnv.append_object(pdo))
        pdo2 = copy.copy(pdo)
        self.assertTrue(cnv.append_object(pdo2))
        self.assertEqual(pdo2.id, 1)
        self.assertEqual(len(cnv.objects), 2)

    def test_find_object_by_id(self):
        cnv = PdCanvas(0, 0, 100, 50)
        pdo1 = PdObject("float")
        pdo2 = PdObject("float")
        self.assertTrue(cnv.append_object(pdo1))
        self.assertTrue(cnv.append_object(pdo2))
        self.assertEqual(cnv.find_object_by_id(0), pdo1)
        self.assertEqual(cnv.find_object_by_id(1), pdo2)
        self.assertEqual(cnv.find_object_by_id(2), None)

    def test_make_connection_key(self):
        self.assertEqual(PdCanvas.make_connection_key(1, 2, 3, 4), "1:2 => 3:4")

    def test_add_connection(self):
        nout = NoLogging()

        cnv = PdCanvas(0, 0, 100, 50)
        self.assertRaises(AssertionError, cnv.add_connection, 0, 0, 0, 0)
        self.assertFalse(cnv.add_connection(0, 0, 1, 0))
        pdo1 = PdObject("float")
        pdo2 = PdObject("float")
        cnv.append_object(pdo1)
        cnv.append_object(pdo2)
        self.assertTrue(cnv.add_connection(0, 0, 1, 0, True))
        self.assertEqual(len(cnv.connections), 1)
        self.assertFalse(cnv.add_connection(0, 1, 1, 0, True))
        self.assertFalse(cnv.add_connection(0, 0, 1, 2, True))
        cnv.connect([0, 0, 1, 1])

    def test_append_subpatch(self):
        cnv = PdCanvas(0, 0, 100, 50)
        f1 = PdObject("float")
        cnv.append_object(f1)
        self.assertEqual(f1.id, 0)
        self.assertEqual(len(cnv.objects), 1)

        sp = PdCanvas(0, 0, 10, 10)
        self.assertRaises(AssertionError, cnv.append_subpatch, sp)
        sp.type = cnv.TYPE_SUBPATCH
        self.assertTrue(cnv.append_subpatch(sp))
        self.assertEqual(sp.id, 1)
        self.assertEqual(len(cnv.objects), 2)

    def test_inlets(self):
        cnv = PdCanvas(0, 0, 100, 50)
        self.assertEqual(cnv.inlets(), [])

        pdo1 = PdObject("inlet", 100, 0)
        pdo2 = PdObject("inlet", 10, 0)
        pdo3 = PdObject("inlet~", 20, 0)

        for o in (pdo1, pdo2, pdo3):
            cnv.append_object(o)

        self.assertEqual(cnv.inlets(), [cnv.XLET_MESSAGE, cnv.XLET_SOUND, cnv.XLET_MESSAGE])
        pdo1.x = 0
        self.assertEqual(cnv.inlets(), [cnv.XLET_MESSAGE, cnv.XLET_MESSAGE, cnv.XLET_SOUND])

    def test_outlets(self):
        cnv = PdCanvas(0, 0, 100, 50)
        self.assertEqual(cnv.inlets(), [])

        pdo1 = PdObject("outlet", 100, 0)
        pdo2 = PdObject("outlet", 10, 0)
        pdo3 = PdObject("outlet~", 20, 0)

        for o in (pdo1, pdo2, pdo3):
            cnv.append_object(o)

        self.assertEqual(cnv.outlets(), [cnv.XLET_MESSAGE, cnv.XLET_SOUND, cnv.XLET_MESSAGE])
        pdo1.x = 0
        self.assertEqual(cnv.outlets(), [cnv.XLET_MESSAGE, cnv.XLET_MESSAGE, cnv.XLET_SOUND])

    def test_traverse(self):
        class T:
            def __init__(self):
                self.o = 0
                self.cb = 0
                self.ce = 0

            def visit_object(self, o):
                self.o += 1

            def visit_canvas_begin(self, c):
                self.cb += 1

            def visit_canvas_end(self, c):
                self.ce += 1

        t = T()
        cnv = PdCanvas(0, 0, 100, 50)
        pdo1 = PdObject("outlet", 100, 0)
        pdo2 = PdObject("outlet", 10, 0)
        for o in (pdo1, pdo2):
            cnv.append_object(o)

        cnv.traverse(t)
        self.assertEqual(t.o, 2)
        self.assertEqual(t.cb, 1)
        self.assertEqual(t.ce, 1)