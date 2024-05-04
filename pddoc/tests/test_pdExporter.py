#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

__author__ = 'Serge Poltavski'

import difflib
from unittest import TestCase, expectedFailure

from pddoc.pd.parser import *
from pddoc.pd.pdexporter import *


class TestPdExporter(TestCase):
    def setUp(self):
        self._exp = PdExporter()
        self._parser = Parser()
        c = Canvas(0, 0, 100, 100)
        self._parser.canvas = c
        self._parser.canvas_stack.append(c)

    def test_init(self):
        exp = PdExporter()
        c = Canvas(0, 0, 200, 100, font_size=10)
        c.type = Canvas.TYPE_WINDOW
        c.traverse(exp)

    def diff(self, fname1, fname2):
        file1 = open(fname1, 'r')
        file2 = open(fname2, 'r')
        diff = difflib.unified_diff(file1.readlines(), file2.readlines())
        lines = list(diff)
        ln = len(lines)
        # if ln:
        # print "".join(lines)

        return ln != 0

    def reexport(self, fname1, fname2):
        parser = Parser()
        self.assertTrue(parser.parse(fname1))
        exp = PdExporter()
        parser.canvas.traverse(exp)
        exp.save(fname2)

    def test_export_comments(self):
        fname1 = "comments.pd"
        fname2 = "out/export_comments.pd"
        self.reexport(fname1, fname2)
        self.assertFalse(self.diff(fname1, fname2))

    def test_export_comments2(self):
        comm = Comment(0, 0, ['a', 'b', 'c'])
        self._parser.canvas.append_object(comm)
        self._parser.canvas.traverse(self._exp)
        self.assertEqual("\n".join(self._exp.result), "#X text 0 0 a b c;")

    def test_export_comments3(self):
        comm = Comment(0, 0, ['Comment', 'with', 'symbols:', '$"!@#$%^&*()[]', '\\,', 'new line'])
        self.assertEqual(comm.text(), 'Comment with symbols: $"!@#$%^&*()[], new line')
        self._parser.canvas.append_object(comm)
        self._parser.canvas.traverse(self._exp)
        self.assertEqual("\n".join(self._exp.result), '#X text 0 0 Comment with symbols: $"!@#$%^&*()[] \\, new line;')

    def test_export_comments4(self):
        comm = Comment(0, 0, ['a', 'b', 'c'], width=45)
        self._parser.canvas.append_object(comm)
        self._parser.canvas.traverse(self._exp)
        self.assertEqual("\n".join(self._exp.result), "#X text 0 0 a b c, f 45;")

    def test_export_comments5(self):
        comm = Comment(0, 0, 'fill all array with specified value or pattern. Arguments are:'.split(' '))
        self._parser.canvas.append_object(comm)
        self._parser.canvas.traverse(self._exp)
        self.assertEqual("\n".join(self._exp.result), "#X text 0 0 fill all array with specified value or pattern. "
                                                      "Arguments\nare:;")

    def test_export_objects(self):
        fname1 = "objects.pd"
        fname2 = "out/export_objects.pd"
        self.reexport(fname1, fname2)
        self.assertFalse(self.diff(fname1, fname2))

    def test_export_connections(self):
        fname1 = "connections.pd"
        fname2 = "out/export_connections.pd"
        self.reexport(fname1, fname2)
        f1 = open(fname1, 'r')
        l1 = f1.readlines()
        l1.sort()
        f2 = open(fname2, 'r')
        l2 = f2.readlines()
        l2.sort()

        self.assertEqual(len(l2), len(l1))
        for n in range(0, len(l1)):
            self.assertEqual(l2[n], l1[n])

    @expectedFailure
    def test_export_subpatch(self):
        fname1 = "subpatch.pd"
        fname2 = "out/export_subpatch.pd"
        self.reexport(fname1, fname2)
        self.assertFalse(self.diff(fname1, fname2))

    @expectedFailure
    def test_export_core_gui(self):
        fname1 = "core_gui.pd"
        fname2 = "out/export_core_gui.pd"
        self.reexport(fname1, fname2)
        self.assertFalse(self.diff(fname1, fname2))

    def test_export_array(self):
        fname1 = "array.pd"
        fname2 = "out/export_array.pd"
        self.reexport(fname1, fname2)
        self.assertFalse(self.diff(fname1, fname2))

    @expectedFailure
    def test_export_many(self):
        fname1 = "simple.pd"
        fname2 = "out/export_simple.pd"
        self.reexport(fname1, fname2)
        self.assertFalse(self.diff(fname1, fname2))

    def parse_line(self, line):
        n = len(self._parser.canvas.objects)
        self._parser.parse_line(line)
        self.assertEqual(len(self._parser.canvas.objects), n + 1)
        return self._parser.canvas.objects[n]

    def test_visit_message(self):
        msg = self.parse_line('#X msg 10 20 1 \\, 2')
        msg.traverse(self._exp)
        res = self._exp.result
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0], '#X msg 10 20 1 \\, 2;')

    def test_export_array2(self):
        arr = Array('hist', 64, 0)
        self._parser.canvas.append_object(arr)
        self._parser.canvas.traverse(self._exp)
        self.assertEqual("\n".join(self._exp.result),
                         '#N canvas 0 22 450 300 (subpatch) 0;\n'
                         '#X array hist 64 float 1;\n'
                         '#X coords 0 1 64 -1 200 140 1;\n'
                         '#X restore 0 0 graph;')

    def test_export_array3(self):
        arr = Array('hist', 10, 0)
        arr.set_yrange(1.5, 3.5)
        self._parser.canvas.append_object(arr)
        self._parser.canvas.traverse(self._exp)
        self.assertEqual("\n".join(self._exp.result),
                         '#N canvas 0 22 450 300 (subpatch) 0;\n'
                         '#X array hist 10 float 1;\n'
                         '#X coords 0 3.5 10 1.5 200 140 1;\n'
                         '#X restore 0 0 graph;')

    def test_export_array4(self):
        arr = Array('hist', 4, 1)
        arr.set_yrange(-2, 2)
        arr.set_data([1, 2, 3, -1])
        self._parser.canvas.append_object(arr)
        self._parser.canvas.traverse(self._exp)
        self.assertEqual("\n".join(self._exp.result),
                         '#N canvas 0 22 450 300 (subpatch) 0;\n'
                         '#X array hist 4 float 1;\n'
                         '#A 0 1 2 3 -1;\n'
                         '#X coords 0 2 4 -2 200 140 1;\n'
                         '#X restore 0 0 graph;')

    def test_export_array5(self):
        arr = Array('hist', 4, 1)
        arr.set_yrange(-2, 2)
        arr.set_data([1, 2, 3, -1])
        arr.width = 125
        arr.height = 160
        self._parser.canvas.append_object(arr)
        self._parser.canvas.traverse(self._exp)
        self.assertEqual("\n".join(self._exp.result),
                         '#N canvas 0 22 450 300 (subpatch) 0;\n'
                         '#X array hist 4 float 1;\n'
                         '#A 0 1 2 3 -1;\n'
                         '#X coords 0 2 4 -2 125 160 1;\n'
                         '#X restore 0 0 graph;')
