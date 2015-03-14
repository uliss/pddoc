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

import argparse
import logging
from lxml import etree

from pddoc.htmldocvisitor import *


def get_parser():
    schema_root = etree.parse(os.path.join(os.path.dirname(__file__), '..', 'share', 'pddoc.xsd')).getroot()
    schema = etree.XMLSchema(schema_root)
    return etree.XMLParser(schema=schema)


def main():
    arg_parser = argparse.ArgumentParser(description='PureData pddoc to html converter')
    arg_parser.add_argument('name', metavar='PDDOC', help="Documentation file in PDDOC format")
    arg_parser.add_argument('output', metavar='OUTNAME', nargs='?', default='',
                            help="HTML output file name")

    args = vars(arg_parser.parse_args())
    input = args['name']
    output = args['output']

    if not os.path.exists(input):
        logging.error("File not exists: \"%s\"", input)
        exit(1)

    if not output:
        output = os.path.splitext(os.path.basename(input))[0] + ".html"

    dobj = DocObject()

    try:
        xml = ET.parse(input, get_parser())
    except etree.XMLSyntaxError, e:
        logging.error("XML syntax error:\n \"%s\"\n\twhile parsing file: \"%s\"", e, input)
        exit(1)

    pddoc = xml.getroot()
    for child in pddoc:
        if child.tag == "object":
            dobj.from_xml(child)
            v = HtmlDocVisitor()
            v.set_image_prefix(child.attrib["name"])
            dobj.traverse(v)
            v.generate_images()

            s = v.render()
            f = open(output, "w")
            f.write(s)
            f.close()
            break

if __name__ == '__main__':
    main()