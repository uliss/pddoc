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
    arg_parser.add_argument('--properties', '-p', action='store_true', help='list properties')
    arg_parser.add_argument('--objects', '-o', action='store_true', help='list objects')
    arg_parser.add_argument('--aliases', '-a', action='store_true', help='list object aliases')
    arg_parser.add_argument('--methods', '-m', action='store_true', help='list methods')
    arg_parser.add_argument('--keywords', '-k', action='store_true', help='list keywords')
    arg_parser.add_argument('name', metavar='PDDOC', help="Documentation file in PDDOC(XML) format")

    args = vars(arg_parser.parse_args())
    in_file = args['name']
    show_properties = args['properties']
    show_methods = args['methods']
    show_objects = args['objects']
    show_aliases = args['aliases']
    show_keywords = args['keywords']

    xml = parse_xml(in_file)

    if not xml:
        exit(1)

    pddoc = xml.getroot()
    for child_tag in pddoc:
        if child_tag.tag == "object":
            obj = DocObject()
            obj.from_xml(child_tag)
            visitor = ListObjectVisitor(show_objects=show_objects,
                                        show_aliases=show_aliases,
                                        show_methods=show_methods,
                                        show_properties=show_properties,
                                        show_keywords=show_keywords)
            obj.traverse(visitor)
            print(visitor)


if __name__ == '__main__':
    main()
