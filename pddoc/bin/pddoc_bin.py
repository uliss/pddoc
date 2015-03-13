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

from pddoc.docobject import *
from pddoc.htmldocvisitor import *
from format import detect_format

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
        output = os.path.splitext(input)[0] + ".html"

    dobj = DocObject()
    xml = ET.parse(input)
    pddoc = xml.getroot()
    for child in pddoc:
        if child.tag == "object":
            dobj.from_xml(child)
            v = HtmlDocVisitor()
            dobj.traverse(v)
            v.generate_images()

            s = v.render()
            f = open(output, "w")
            f.write(s)
            f.close()
            break

if __name__ == '__main__':
    main()