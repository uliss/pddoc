#!/usr/bin/env python
# coding=utf-8
from __future__ import print_function

import argparse
import logging
import os
import re

from lxml import etree


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
    if file is None:
        print(f"{name}\t{desc}")
    else:
        file.write(f"{name}\t{desc}\n")


def clear_spaces(txt: str) -> str:
    return re.sub(r"\s+", " ", txt.replace("\n", " "))


def find_translation(node, path: str, lang: str, default: str) -> str:
    tr = node.find(f"{path}/tr[@lang='{lang}']")
    if tr is None or tr.get("finished", "true") == "false":
        tr = node.find(f"{path}/tr[@lang='en']")
        if tr is None:
            tr = node.find(f"{path}")

    if tr is not None:
        return clear_spaces(tr.text)
    else:
        return default


def main():
    arg_parser = argparse.ArgumentParser(description='Converts XML library to deken object list')
    arg_parser.add_argument('input', metavar='LIB_FILE', help="Library description file in XML format")
    arg_parser.add_argument('--aliases', '-a', action='store_true', help='output object aliases')
    arg_parser.add_argument('--force', '-f', action='store_true', help='force to overwrite existing file')
    arg_parser.add_argument('--output', '-o', metavar='OUTPUT', help="output file name")
    arg_parser.add_argument('--locale', '-l', metavar='NAME', choices=("EN", "RU"), default='EN',
                            help='locale (currently EN or RU)')
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
        for obj in c.findall('entry'):
            descr_en = find_translation(obj, "pddoc/object/meta/description", "en", "")
            descr_ru = find_translation(obj, "pddoc/object/meta/description", "ru", "")

            descr = descr_en
            if descr_ru != descr_en:
                descr += " / " + descr_ru

            print_entry(f, obj.get("name"), descr)
            if args['aliases']:
                for a in obj.xpath("pddoc/object/meta/aliases/alias"):
                    print_entry(f, a.text, descr)

    if f:
        f.close()


if __name__ == '__main__':
    main()
