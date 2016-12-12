#!/usr/bin/env python
# coding=utf-8

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
from __future__ import print_function
from unittest import TestCase
from pddoc.parser import fix_section_order
from lxml import etree


class TestFix_section_order(TestCase):
    def test_fix_section_order(self):
        input_xml = '''\
<object>
    <meta/>
    <inlets/>
    <methods/>
    <example/>
    <title/>
    <info/>
    <arguments/>
    <outlets/>
</object>
'''

        output_xml = '''\
<object>
    <title/>
    <meta/>
    <info/>
    <example/>
    <arguments/>
    <methods/>
    <inlets/>
    <outlets/>
</object>
'''
        xml = etree.fromstring(input_xml)
        self.assertTrue(xml is not None)
        fix_section_order(xml)
        self.assertEqual(etree.tostring(xml, pretty_print=True), output_xml)
