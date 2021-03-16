#!/usr/bin/env python
# coding=utf-8
import argparse
import shutil
import logging
import os
from pddoc.parser import parse_xml
from pddoc.pd import factory

from pddoc.markdownvisitor import MarkdownVisitor
from pddoc.docobject import DocObject
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


def main():
    arg_parser = argparse.ArgumentParser(description='PureData pddoc to Markdown converter')
    arg_parser.add_argument('name', metavar='PDDOC', help="Documentation file in PDDOC format")
    arg_parser.add_argument('output', metavar='OUTNAME', nargs='?', default='',
                            help="Markdown output file name")
    arg_parser.add_argument('--locale', '-l', metavar='locale', default='EN', help='locale (currently EN or RU)')
    
    args = vars(arg_parser.parse_args())
    in_file = args['name']
    output = args['output']

    if not os.path.exists(in_file):
        logging.error("File not exists: \"%s\"", in_file)
        exit(1)

    if not output:
        output = os.path.splitext(os.path.basename(in_file))[0] + ".md"

    xml = parse_xml(in_file)
    if not xml:
        exit(1)

    factory.add_import('ceammc')

    pddoc = xml.getroot()
    for child_tag in pddoc:
        if child_tag.tag == "object":
            dobj = DocObject()
            dobj.from_xml(child_tag)

            v = MarkdownVisitor(args['locale'])
            v.set_image_prefix(child_tag.attrib["name"])
            v.set_search_dir(os.path.dirname(in_file))

            # traverse doc
            dobj.traverse(v)

            # generate images
            v.generate_images()

            html_data = v.render()
            f = open(output, "w")
            f.write(html_data)
            f.close()


if __name__ == '__main__':
    main()
