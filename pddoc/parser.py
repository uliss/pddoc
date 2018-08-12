#!/usr/bin/env python
# coding=utf-8

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

from lxml import etree
import os
import logging


def get_parser():
    etree.register_namespace("xi", "http://www.w3.org/2001/XInclude")
    schema_root = etree.parse(os.path.join(os.path.dirname(__file__), 'share', 'pddoc.xsd')).getroot()
    schema = etree.XMLSchema(schema_root)
    return etree.XMLParser(schema=schema)


def parse_xml(path):
    if not os.path.exists(path):
        logging.error("File not exists: \"%s\"", path)
        return None

    try:
        NSMAP = {'xi': "http://www.w3.org/2001/XInclude"}
        etree.register_namespace("xi", "http://www.w3.org/2001/XInclude")
        xml = etree.parse(path, get_parser())
        xml.xinclude()
    except etree.XMLSyntaxError as e:
        logging.error("XML syntax error:\n \"%s\"\n\twhile parsing file: \"%s\"", e, path)
        return None

    pddoc = xml.getroot()
    for obj in pddoc.findall('object'):
        fix_section_order(obj)

    return xml


def fix_section_order(obj_tag):
    sorted_children = sorted(obj_tag, key=lambda n: ('title',
                                                     'meta', 'info',
                                                     'example', 'arguments', 'properties', 'methods',
                                                     'inlets', 'outlets').index(n.tag))
    for child in obj_tag:
        obj_tag.remove(child)

    for child in reversed(sorted_children):
        obj_tag.insert(0, child)

