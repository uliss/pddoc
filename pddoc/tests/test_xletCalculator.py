#!/usr/bin/env python
# coding=utf-8
from unittest import TestCase
import os.path as path
from pddoc.pd import XletCalculator, PdObject

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


class TestXletCalculator(TestCase):
    def test_add_db(self):
        db = XletCalculator()

        with self.assertRaises(IOError):
            db.add_db(path.join(path.dirname(__file__), 'unknown.db'))

        # before adding db
        self.assertEqual(0, len(db.outlets_by_name('pass.this')))
        self.assertEqual(0, len(db.inlets_by_name('pass.this')))
        self.assertEqual(0, len(db.outlets_by_name('unknown')))

        db.add_db(path.join(path.dirname(__file__), 'xlet_test.db'))
        self.assertEqual(1, len(db.inlets_by_name('pass.this')))
        self.assertEqual(1, len(db.outlets_by_name('pass.this')))
        self.assertEqual(0, len(db.outlets_by_name('unknown')))
