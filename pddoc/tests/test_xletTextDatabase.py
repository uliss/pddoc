#!/usr/bin/env python
# coding=utf-8

# Copyright (C) 2015 by Serge Poltavski                                 #
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


from pddoc.xlettextdatabase import XletTextDatabase
import pddoc
import os
from nologging import *

pddoc_path = os.path.dirname(pddoc.__file__)
pddoc_db = pddoc_path + '/externals/core/pd_objects.db'


class TestXletTextDatabase(TestCase):
    def test_load(self):
        nl = NoLogging()

        with self.assertRaises(IOError):
            XletTextDatabase('not-exists', None)

        db = XletTextDatabase(pddoc_db, "core")

    def test_parse(self):
        db = XletTextDatabase(None, None)
        db.parse('abs ~~~ -')
        self.assertTrue(db.has_object("abs"))

    def test_inlets(self):
        db = XletTextDatabase(pddoc_db, "core")
        self.assertEqual(db.inlets('none'), [])
        self.assertEqual(db.inlets('bang'), [0])
        self.assertEqual(db.inlets('b'), [0])
        self.assertEqual(db.inlets('float'), [0, 0])
        self.assertEqual(db.inlets('f'), [0, 0])
        self.assertEqual(db.inlets('int'), [0, 0])
        self.assertEqual(db.inlets('i'), [0, 0])
        self.assertEqual(db.inlets('symbol'), [0, 0])

    def test_outlets(self):
        db = XletTextDatabase(pddoc_db, "core")
        self.assertEqual(db.outlets('none'), [])
        self.assertEqual(db.outlets('bang'), [0])
        self.assertEqual(db.outlets('b'), [0])
        self.assertEqual(db.outlets('float'), [0])
        self.assertEqual(db.outlets('f'), [0])
        self.assertEqual(db.outlets('int'), [0])
        self.assertEqual(db.outlets('i'), [0])
        self.assertEqual(db.outlets('symbol'), [0])
