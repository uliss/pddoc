#!/usr/bin/env python
# coding=utf-8
import argparse
import logging
import os

from pddoc.parser import parse_xml
from pddoc.pd import factory, PdObject
from pddoc.markdownvisitor import MarkdownVisitor
from pddoc.docobject import DocObject
#   Copyright (C) 2023 by Serge Poltavski                                 #
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


def add_xlet_db(path_list):
    for db_path in path_list:
        if not os.path.exists(db_path):
            logging.warning("xlet database file not found: '%s'. skipping...", db_path)
        else:
            PdObject.xlet_calculator.add_db(db_path)


def main():
    arg_parser = argparse.ArgumentParser(description='PureData pddoc to Markdown converter')
    arg_parser.add_argument('name', metavar='PDDOC', help="Documentation file in PDDOC format")
    arg_parser.add_argument('output', metavar='OUTNAME', nargs='?', default='',
                            help="Markdown output file name")
    arg_parser.add_argument('--stdout', action='store_true', default=False, help='output to stdout')
    arg_parser.add_argument('--no-images', action='store_true', default=False, help='do not generate images')
    arg_parser.add_argument('--example-img', metavar='PATH', type=str, default='example/',
                            help="relative path to example folder with example image files")
    arg_parser.add_argument('--example-pd', metavar='PATH', type=str, default='',
                            help="relative path to example folder with example Pd files")
    arg_parser.add_argument('--xlet-db', metavar='PATH', action='append',
                            help='inlet/outlet database file paths', default=[])
    arg_parser.add_argument('--locale', '-l', metavar='locale', default='EN', help='locale (currently EN or RU)')
    
    args = vars(arg_parser.parse_args())
    in_file = args['name']
    output = args['output']
    stdout = args['stdout']

    if not os.path.exists(in_file):
        logging.error("File not exists: \"%s\"", in_file)
        exit(1)

    add_xlet_db(args['xlet_db'])

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

            v = MarkdownVisitor(args['locale'], no_images=args['no_images'])
            v.set_image_prefix(child_tag.attrib["name"])
            v.set_search_dir(os.path.dirname(in_file))
            v.example_img_dir = args['example_img']
            v.example_pd_dir = args['example_pd']

            # traverse doc
            dobj.traverse(v)

            # generate images
            if not args["no_images"]:
                v.generate_images()

            md_data = v.render()

            if stdout:
                print(md_data)
            else:
                with open(output, "w") as f:
                    f.write(md_data)
                    f.close()


if __name__ == '__main__':
    main()
