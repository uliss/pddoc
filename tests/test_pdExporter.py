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

    def test_export_comments(self):
        parser = PdParser()
        fname1 = "comments.pd"
        fname2 = "export_comments.pd"
        self.assertTrue(parser.parse(fname1))
        exp = PdExporter()

        parser.canvas.traverse(exp)
        content = "\n".join(exp.result)
        f = open(fname2, "w")
        f.write(content)
        f.close()

        file1 = open(fname1, 'r')
        file2 = open(fname2, 'r')

        diff = difflib.unified_diff(file1.readlines(), file2.readlines())
        lines = list(diff)
        ln = len(lines)
        if ln:
            print "".join(lines)

        self.assertEqual(ln, 0)

    def test_export_objects(self):
        parser = PdParser()
        fname1 = "objects.pd"
        fname2 = "export_objects.pd"
        self.assertTrue(parser.parse(fname1))
        exp = PdExporter()

        parser.canvas.traverse(exp)
        content = "\n".join(exp.result)
        f = open(fname2, "w")
        f.write(content)
        f.close()

        file1 = open(fname1, 'r')
        file2 = open(fname2, 'r')

        diff = difflib.unified_diff(file1.readlines(), file2.readlines())
        lines = list(diff)
        ln = len(lines)
        if ln:
            print "".join(lines)

        self.assertEqual(ln, 0)
