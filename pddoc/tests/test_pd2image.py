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

import unittest
import subprocess
import os
import os.path

import nologging

BIN_PATH = os.path.join(os.path.dirname(__file__), "..", "bin", "pd2image.py")


class TestCairoPainter(unittest.TestCase):
    def clean(self):
        try:
            os.remove("image.png")
            os.remove("comments.pdf")
        except OSError:
            pass

    def setUp(self):
        self.clean()

    def tearDown(self):
        self.clean()

    def test_run_simple(self):
        nolog = nologging.NoLogging()
        rc = subprocess.call(["python", BIN_PATH, "not-exists"])
        self.assertNotEqual(rc, 0)

        rc = subprocess.call(["python", BIN_PATH, "comments.pd"])
        self.assertEqual(rc, 0)
        self.assertTrue(os.path.exists("image.png"))  # default output name

        rc = subprocess.call(["python", BIN_PATH, "--format", "pdf", "comments.pd", "comments.pdf"])
        self.assertEqual(rc, 0)
        self.assertTrue(os.path.exists("comments.pdf"))
