#!/usr/bin/env python
# coding=utf-8

#   Copyright (C) 2015 by Serge Poltavski                                 #
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

import os
import os.path
import subprocess
import unittest

BIN_PATH = os.path.join(os.path.dirname(__file__), "..", "bin", "pd_obj2img.py")


class TestCairoPainter(unittest.TestCase):
    def clean(self):
        try:
            os.remove("line.png")
            os.remove("line.pdf")
            os.remove("line2.pdf")
        except OSError:
            pass

    def setUp(self):
        self.clean()

    def tearDown(self):
        self.clean()

    def test_run_simple(self):
        self.assertFalse(os.path.exists("line.png"))
        rc = subprocess.call(["python3", BIN_PATH, "line"])
        self.assertEqual(rc, 0)
        self.assertTrue(os.path.exists("line.png"))

    def test_args(self):
        rc = subprocess.call(["python3", BIN_PATH, "--format", "pdf", "line"])
        self.assertEqual(rc, 0)
        self.assertTrue(os.path.exists("line.pdf"))

        rc = subprocess.call(["python3", BIN_PATH, "--format", "pdf", "line", "line2.pdf"])
        self.assertEqual(rc, 0)
        self.assertTrue(os.path.exists("line2.pdf"))
