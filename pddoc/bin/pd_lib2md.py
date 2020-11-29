#!/usr/bin/env python
# coding=utf-8
from __future__ import print_function
import argparse
import os
import logging
from lxml import etree
import re


#   Copyright (C) 2020 by Serge Poltavski                                 #
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

def print_entry(file, name, desc):
    # remove multiple spaces
    desc = " ".join(desc.split()).strip()
    output_str = f"[**{name}**]({name}.md)\t{desc}<br>"
    if file is None:
        print(output_str)
    else:
        file.write(output_str+"\n")

def print_category(file, name):
    if file is None:
        print(f"#### {name}")
    else:
        file.write(f"#### {name}<br>\n")

def main():
    arg_parser = argparse.ArgumentParser(description='Converts XML library to deken object list')
    arg_parser.add_argument('input', metavar='LIB_FILE', help="Library description file in XML format")
    arg_parser.add_argument('--aliases', '-a', action='store_true', help='output object aliases')
    arg_parser.add_argument('--force', '-f', action='store_true', help='force to overwrite existing file')
    arg_parser.add_argument('--output', '-o', metavar='OUTPUT', help="output file name")
    args = vars(arg_parser.parse_args())

    if not os.path.exists(args['input']):
        logging.error('no such file: "%s"', args['input'])
        exit(1)

    doc = etree.parse(args['input'])
    doc.xinclude()
    root = doc.getroot()

    if args['output'] and os.path.exists(args['output']) and not args['force']:
        print("Error: file already exists: '{0}'. Use --force flag to overwrite.".format(args['output']))
        exit(2)

    f = None
    if args['output']:
        f = open(args['output'], "w")

    for c in root.findall("category"):
        print_category(f, c.get("name"))
        for obj in c.findall('entry'):
            print_entry(f, obj.get("name"), obj.get("descr"))
            if args['aliases']:
                for a in obj.xpath("pddoc/object/meta/aliases/alias"):
                    print_entry(f, a.text, obj.get("descr"))

    if f:
        f.close()


if __name__ == '__main__':
    main()
