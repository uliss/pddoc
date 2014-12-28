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

from pddoc.htmldocvisitor import Tag


class TestTag(TestCase):
    def test_init(self):
        t = Tag('meta')
        self.assertEqual(str(t), "<meta/>")
        t.set_attr('br')
        self.assertEqual(str(t), "<meta/>\n")
        t.set_attr('name', 'value')
        self.assertEqual(str(t), "<meta name=\"value\"/>\n")
        t.del_attr('br')
        self.assertEqual(str(t), "<meta name=\"value\"/>")
        t.del_attr('name')
        self.assertEqual(str(t), "<meta/>")