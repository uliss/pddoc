#!/usr/bin/env python
# coding=utf-8
from __future__ import print_function
import argparse

from pddoc.docobject import DocObject
from pddoc.listobjectvisitor import ListObjectVisitor
from pddoc.parser import parse_xml

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

__author__ = 'Serge Poltavski'

def main():
    arg_parser = argparse.ArgumentParser(description='list PureData objects in pddoc')
    arg_parser.add_argument('name', metavar='PDDOC', help="Documentation file in PDDOC(XML) format")

    args = vars(arg_parser.parse_args())
    in_file = args['name']

    xml = parse_xml(in_file)

    if not xml:
        exit(1)

    pddoc = xml.getroot()
    for child_tag in pddoc:
        if child_tag.tag == "object":
            dobj = DocObject()
            dobj.from_xml(child_tag)
            dobj.traverse(ListObjectVisitor())


if __name__ == '__main__':
    main()
