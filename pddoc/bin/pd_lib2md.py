#!/usr/bin/env python
# coding=utf-8
from __future__ import print_function
import argparse
import os
import logging
from lxml import etree
from jinja2 import Environment, PackageLoader, select_autoescape


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

def main():
    arg_parser = argparse.ArgumentParser(description='Converts XML library to markdown page')
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

    xml = etree.parse(args['input'])
    xml.xinclude()
    root = xml.getroot()

    if args['output'] and os.path.exists(args['output']) and not args['force']:
        print("Error: file already exists: '{0}'. Use --force flag to overwrite.".format(args['output']))
        exit(2)

    f = None
    if args['output']:
        f = open(args['output'], "w")

    locale = args["locale"]
    # template config
    if "EN" in locale:
        tmpl_path = "md_library_en.tmpl.md"
    elif "RU" in locale:
        tmpl_path = "md_library_ru.tmpl.md"
    else:
        tmpl_path = "md_library_en.tmpl.md"

    info = {
        "name": root.get("name"),
        "version": root.xpath("//library/meta/version")[0].text,
        "descr": root.xpath("//library/meta/library-info/description")[0].text,
        "website": root.xpath("//library/meta/library-info/website")[0].text,
        "license": root.xpath("//library/meta/library-info/license")[0].text,
        "authors": root.xpath("//library/meta/authors/author")
    }

    data = []

    for c in root.findall("category"):
        category = {"name": c.get("name"), "info": "", "objects": []}
        cat_info = c.findall("category-info")
        if len(cat_info) > 0:
            category["info"] = cat_info[0].text

        data.append(category)
        # iterate category objects
        for obj in c.findall('entry'):
            item = {"name": obj.get("name"), "descr": obj.get("descr"), "aliases": []}
            category["objects"].append(item)

            if args['aliases']:
                for a in obj.xpath("pddoc/object/meta/aliases/alias"):
                    category["aliases"].append(a.text)

    # print(data)

    env = Environment(
        loader=PackageLoader('pddoc', 'share'),
        autoescape=select_autoescape(['md'])
    )

    template = env.get_template(tmpl_path)
    output_str = template.render(info=info, data=data)

    if f is None:
        print(output_str)
    else:
        f.write(output_str + "\n")
        f.close()


if __name__ == '__main__':
    main()
