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
from pddoc.pd.pdfactory import find_external_object, make

__author__ = 'Serge Poltavski'


class TestFind_external_object(TestCase):
    def test_find_external_object(self):
        self.assertFalse(find_external_object("../name"))
        self.assertTrue(find_external_object("pddp/pddplink"))
        self.assertFalse(find_external_object("pddp/not-exists"))

    def test_make(self):
        self.assertTrue(make(["pddp/pddplink", "http://google.com"]))