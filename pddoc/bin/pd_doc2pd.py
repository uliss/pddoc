#!/usr/bin/env python
# coding=utf-8
from __future__ import print_function
import argparse
import os
import logging

from pddoc.docobject import DocObject
from pddoc.pddocvisitor import PdDocVisitor
from pddoc.xletdocvisitor import XletDocVisitor
from pddoc.parser import parse_xml
from pddoc.pd.obj import PdObject
from pddoc.pd import factory

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


def add_xlet_db(path_list):
    for db_path in path_list:
        if not os.path.exists(db_path):
            logging.warning("xlet database file not found: '%s'. skipping...", db_path)
        else:
            PdObject.xlet_calculator.add_db(db_path)


def main():
    arg_parser = argparse.ArgumentParser(description='PureData pddoc to pd patch converter')
    arg_parser.add_argument('--website', '-w', metavar='URL', help='library website URL')
    arg_parser.add_argument('--license', '-l', metavar='license', help='library license')
    arg_parser.add_argument('--version', '-v', metavar='version', default='0.0', help='library version')
    arg_parser.add_argument('--force', '-f', action='store_true', help='force to overwrite existing file')
    arg_parser.add_argument('--xlet-db', metavar='PATH', action='append',
                            help='inlet/outlet database file path', default=[])
    arg_parser.add_argument('name', metavar='PDDOC', help="Documentation file in PDDOC(XML) format")
    arg_parser.add_argument('output', metavar='OUTNAME', nargs='?', default='',
                            help="Pd output patch file name")

    args = vars(arg_parser.parse_args())
    in_file = args['name']
    output = args['output']

    if not output:
        output = os.path.splitext(os.path.basename(in_file))[0] + "-help.pd"

    if os.path.exists(output) and not args['force']:
        print("Error: file already exists: '{0}'. Use --force flag to overwrite.".format(output))
        exit(1)

    add_xlet_db(args['xlet_db'])

    xml = parse_xml(in_file)

    if not xml:
        exit(1)

    factory.add_import('ceammc')

    pddoc = xml.getroot()
    for child_tag in pddoc:
        if child_tag.tag == "object":
            dobj = DocObject()
            dobj.from_xml(child_tag)

            x = XletDocVisitor()
            dobj.traverse(x)

            v = PdDocVisitor()

            if 'version' in args:
                v._version = args['version']

            if 'license' in args:
                v._license['name'] = args['license']

            if 'website' in args:
                v._website = args['website']

            dobj.traverse(v)

            patch_data = v.render()
            if not patch_data:
                print("convertion error")
                exit(1)

            with open(output, 'w') as f:
                f.write(patch_data)


if __name__ == '__main__':
    main()
