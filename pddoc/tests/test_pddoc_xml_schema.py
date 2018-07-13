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

from unittest import TestCase, expectedFailure
from lxml import etree


class TestPddocXmlSchema(TestCase):
    schema_root = etree.parse('../share/pddoc.xsd').getroot()
    schema = etree.XMLSchema(schema_root)

    def test_init(self):
        parser = etree.XMLParser(schema=self.schema)
        with self.assertRaises(etree.XMLSyntaxError):
            etree.fromstring("<a>5</a>", parser)

    def test_float(self):
        parser = etree.XMLParser(schema=self.schema)
        etree.parse('float.pddoc', parser)
