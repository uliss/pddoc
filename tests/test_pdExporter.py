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

from pdexporter import *
from pdcanvas import *
from pdparser import *
import difflib


class TestPdExporter(TestCase):
    def test_init(self):
        exp = PdExporter()
        c = PdCanvas(0, 0, 200, 100)
        c.type = PdCanvas.TYPE_WINDOW
        c.traverse(exp)

    def diff(self, fname1, fname2):
        file1 = open(fname1, 'r')
        file2 = open(fname2, 'r')
        diff = difflib.unified_diff(file1.readlines(), file2.readlines())
        lines = list(diff)
        ln = len(lines)
        if ln:
            print "".join(lines)

        return ln != 0

    def reexport(self, fname1, fname2):
        parser = PdParser()
        self.assertTrue(parser.parse(fname1))
        exp = PdExporter()
        parser.canvas.traverse(exp)
        exp.save(fname2)

    def test_export_comments(self):
        fname1 = "comments.pd"
        fname2 = "export_comments.pd"
        self.reexport(fname1, fname2)
        self.assertFalse(self.diff(fname1, fname2))

    def test_export_objects(self):
        fname1 = "objects.pd"
        fname2 = "export_objects.pd"
        self.reexport(fname1, fname2)
        self.assertFalse(self.diff(fname1, fname2))

    def test_export_connections(self):
        fname1 = "connections.pd"
        fname2 = "export_connections.pd"
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

    def test_export_core_gui(self):
        fname1 = "core_gui.pd"
        fname2 = "export_core_gui.pd"
        self.reexport(fname1, fname2)
        self.assertFalse(self.diff(fname1, fname2))

        # def test_export_many(self):
        # fname1 = "simple.pd"
        #     fname2 = "export_simple.pd"
        #     self.reexport(fname1, fname2)
        #     self.assertFalse(self.diff(fname1, fname2))
