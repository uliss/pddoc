#!/usr/bin/env python
# coding=utf-8
from __future__ import print_function

import argparse

from lxml import etree

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


def main():
    arg_parser = argparse.ArgumentParser(description='format pddoc file')
    arg_parser.add_argument('--in-place', '-i', action='store_true', help='format in place (overwrite source file)')
    arg_parser.add_argument('name', metavar='PDDOC', help="Documentation file in PDDOC(XML) format")

    args = vars(arg_parser.parse_args())
    in_file = args['name']

    # dirname = os.path.dirname(in_file)
    parser = etree.XMLParser(resolve_entities=False,
                             strip_cdata=False,
                             remove_blank_text=False)
    xml = etree.parse(in_file, parser)

    if not xml:
        exit(1)

    def tag_index(name):
        return (
            "title", "meta", "info", "mouse", "arguments", "properties", "methods", "inlets", "outlets",
            "example").index(
            name)

    pddoc = xml.getroot()
    obj = pddoc.getchildren()[0]
    for r in obj.iter("object"):
        r[:] = sorted(r, key=lambda x: tag_index(x.tag))

    # strip @lang finished=true
    for tr in pddoc.findall("**/description/tr[@finished='true']"):
        tr.attrib.pop("finished")

    # strip blanks
    for elem in obj.iter('*'):
        if elem.tag not in ("method", "property", "pdascii") and elem.text is not None:
            elem.text = elem.text.strip()

        if elem.tag == "pdascii":
            txt = elem.text.rstrip().lstrip("\n")
            elem.text = etree.CDATA("\n" + txt + "\n")

    # remove old method comments
    for comment in obj.xpath('//object/methods/comment()'):
        comment.getparent().remove(comment)

    # sort methods ny name
    for m in obj.iter("methods"):
        m[:] = sorted(m, key=lambda x: x.attrib["name"])

    # add new comments
    for m in obj.xpath('//object/methods/*'):
        if m.attrib["name"].find("--") > 0 or m.attrib["name"].endswith('-'):
            continue

        c = etree.Comment(' ' + m.attrib["name"] + ' ')
        m.addprevious(c)

    # remove old property comments
    for comment in obj.xpath('//object/properties/comment()'):
        comment.getparent().remove(comment)

    # sort properties by name
    for prop in obj.iter("properties"):
        prop[:] = sorted(prop, key=lambda x: x.get("name", ""))

    # add new property comments
    for m in obj.xpath('//object/properties/*'):
        name = m.attrib.get("name")
        if name is not None:
            c = etree.Comment(f" {name} ")
            m.addprevious(c)

    pddoc = etree.Element(pddoc.tag, version="1.0", nsmap={"xi": "http://www.w3.org/2001/XInclude"})
    pddoc.insert(0, obj)

    etree.indent(pddoc, space=" ", level=2)

    if args["in_place"]:
        etree.ElementTree(pddoc).write(in_file,
                                       pretty_print=True,
                                       encoding="UTF-8",
                                       xml_declaration=False,
                                       method="xml",
                                       doctype='<?xml version="1.0" encoding="utf-8"?>')
    else:
        print(etree.tostring(pddoc, pretty_print=True, encoding="UTF-8", xml_declaration=True, method="xml").decode())


if __name__ == '__main__':
    main()
