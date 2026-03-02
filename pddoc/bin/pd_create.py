#!/usr/bin/env python
# coding=utf-8
#   Copyright (C) 2026 by Serge Poltavski                                 #
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
import os.path
import re

from lxml import etree


def append_to_pages(page_path: str, library: str, output_dir: str):
    pddoc_pages = f"{output_dir}/{library}_pages.xml"

    if not os.path.exists(pddoc_pages):
        with open(pddoc_pages, 'w') as f:
            logging.debug(f"creating file: '{pddoc_pages}' ...")
            f.write('<?xml version="1.0" encoding="utf-8"?>\n'
                    '<pddoc-pages version="1.0" xmlns:xi="http://www.w3.org/2001/XInclude">\n'
                    f'  <xi:include href="{page_path}" parse="xml" />\n'
                    '</pddoc-pages>\n')
    else:
        xml = etree.parse(pddoc_pages)
        root = xml.getroot()

        XINCLUDE_NS = "http://www.w3.org/2001/XInclude"
        include = etree.SubElement(root, f"{{{XINCLUDE_NS}}}include")
        include.set('href', page_path)
        include.set('parser', 'xml')

        etree.indent(root, space="  ", level=0)
        xml_str = etree.tostring(root,
                                 pretty_print=True,
                                 encoding="UTF-8",
                                 xml_declaration=False,
                                 method="xml",
                                 doctype='<?xml version="1.0" encoding="utf-8"?>').decode()

        with open(pddoc_pages, 'w') as f:
            logging.debug(f"update file: '{pddoc_pages}' ...")
            f.write(xml_str)


def create_page_template(page_path: str):
    with open(page_path, 'w') as f:
        f.write('''
<?xml version="1.0" encoding="utf-8"?>
<page output="ceammc.props-info.pd">
  <title>
    <tr lang="en">title</tr>
    <tr lang="ru">название</tr>
  </title>
  <sections>
    <h2>Basic usage</h2>
      <par indent="1">Some info</par>
      <a href="ceammc.args-info.pd">More info about argument processing in ceammc</a>
      <pdascii indent="10">
<![CDATA[
/*Pd example*/
]]>
    </pdascii>
  </sections>
</page> 
''')


def main():
    # logging.basicConfig(format='[%(levelname)] %(message)s')

    arg_parser = argparse.ArgumentParser(description='create pddoc file template')
    arg_parser.add_argument('--page', '-p', metavar='NAME', help='create page template')
    arg_parser.add_argument('--library', '-l', metavar='NAME', required=True, help='library name')
    arg_parser.add_argument('dir', metavar='DIR', help="output directory")

    args = vars(arg_parser.parse_args())

    output_dir = args["dir"]
    if not os.path.exists(output_dir):
        logging.error(f"output directory not exists: '{output_dir}'")
        exit(1)

    if args["page"]:
        page_name = ''.join(re.findall(r"[0-9a-z_A-Z]", args["page"]))
        if len(page_name) == 0:
            logging.error(f"invalid page name: {args['page']}")
            exit(2)

        page_name = f'{args["library"]}_page_{page_name}.xml'

        page_path = f"{output_dir}/{page_name}"
        if os.path.exists(page_path):
            logging.error(f"page already exists: {page_path}")
            exit(3)

        create_page_template(page_path)
        append_to_pages(page_name, library=args['library'], output_dir=output_dir)


if __name__ == '__main__':
    main()
