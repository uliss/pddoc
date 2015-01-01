#!/usr/bin/env python
# coding=utf-8

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

from unittest import TestCase, expectedFailure
from pddoc.docobject import *
from pddoc.htmldocvisitor import *

__author__ = 'Serge Poltavski'


class TestDocObject(TestCase):
    pass

    def test_float_export(self):
        dobj = DocObject()

        xml = ET.parse("float.pddoc")
        pddoc = xml.getroot()
        for child in pddoc:
            if child.tag == "object":
                dobj.from_xml(child)

                v = HtmlDocVisitor()
                dobj.traverse(v)
                v.generate_images()

                s = v.render()
                f = open("out/test.html", "w")
                f.write(s)
                f.close()
                break
