#!/usr/bin/env python
# coding=utf-8
from __future__ import print_function

import argparse
import logging
import os

from jinja2 import Environment, PackageLoader, select_autoescape
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


def main():
    template = None
    arg_parser = argparse.ArgumentParser(description='Converts XML library to set of category markdown pages')
    arg_parser.add_argument('input', metavar='LIB_FILE', help="Library description file in XML format")
    arg_parser.add_argument('--aliases', '-a', action='store_true', help='output object aliases')
    arg_parser.add_argument('--force', '-f', action='store_true', help='force to overwrite existing files')
    arg_parser.add_argument('--base-dir', metavar='PATH', help="base directory for output", default=".")
    arg_parser.add_argument('--prefix', metavar='STR', help="filename prefix", default="category_")
    arg_parser.add_argument('--locale', '-l', metavar='NAME', choices=("EN", "RU"), default='EN',
                            help='locale (currently EN or RU)')

    args = vars(arg_parser.parse_args())

    if not os.path.exists(args['input']):
        logging.error('no such file: "%s"', args['input'])
        exit(1)

    xml = etree.parse(args['input'])
    xml.xinclude()
    root = xml.getroot()

    locale = args["locale"]

    # template config
    if "EN" in locale:
        tmpl_path = "md_category_en.tmpl.md"
    elif "RU" in locale:
        tmpl_path = "md_category_ru.tmpl.md"
    else:
        tmpl_path = "md_category_en.tmpl.md"

    try:
        env = Environment(
            loader=PackageLoader('pddoc', 'share'),
            autoescape=select_autoescape(['md'])
        )

        template = env.get_template(tmpl_path)
    except Exception as e:
        logging.error(f"can't open {e}")
        exit(3)

    info = {
        "name": root.get("name"),
        "version": root.xpath("//library/meta/version")[0].text,
        "license": root.xpath("//library/meta/library-info/license")[0].text,
    }

    base_dir = args['base_dir']
    prefix = args["prefix"]

    for c in root.findall("category"):
        name = c.get("name")
        md_name = f"{base_dir}/{prefix}{name}.md"

        if os.path.exists(md_name) and not args["force"]:
            logging.error(f"Error: file already exists: '{md_name}'. Use --force flag to overwrite.")
            exit(2)

        category = {"name": name, "info": "", "objects": []}
        cat_info = c.findall("category-info")
        if len(cat_info) > 0:
            category["info"] = cat_info[0].text

        # iterate category objects
        for obj in c.findall('entry'):
            item = {"name": obj.get("name"), "descr": obj.get("descr"), "aliases": []}
            category["objects"].append(item)

            if args['aliases']:
                for a in obj.xpath("pddoc/object/meta/aliases/alias"):
                    item["aliases"].append("\\[%s\\]" % a.text)

        with open(md_name, "w") as f:
            output_str = template.render(info=info, cat=category)
            f.write(output_str + "\n")
            f.close()
            logging.info(f"write category to '{md_name}'")


if __name__ == '__main__':
    main()
