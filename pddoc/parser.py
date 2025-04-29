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

import logging
import os
from string import Template

from lxml import etree


def get_schema():
    etree.register_namespace("xi", "http://www.w3.org/2001/XInclude")
    xml = etree.parse(os.path.join(os.path.dirname(__file__), 'share', 'pddoc.xsd'))
    return etree.XMLSchema(xml.getroot())


def get_parser():
    return etree.XMLParser(schema=get_schema(), strip_cdata=False)


def parse_xml(path):
    if not os.path.exists(path):
        logging.error("File not exists: \"%s\"", path)
        return None

    try:
        dirname = os.path.dirname(path)
        if len(dirname) == 0:
            dirname = os.getcwd()

        etree.register_namespace("xi", "http://www.w3.org/2001/XInclude")
        xml = etree.parse(path)
        for ref in xml.xpath('//pddoc/object/properties/*[local-name()="include"]'):
            # manual XInclude implementation with template substitution
            prop_xml = etree.parse(dirname + "/" + ref.attrib["href"])
            if ref.attrib.get("subst", "true") != "false":
                tmpl = Template(prop_xml.getroot().text)
                obj_name = os.path.basename(path)[:-6]  # strip .pddoc extension
                obj_name = obj_name.replace("~", "").replace(".", "_")
                txt = tmpl.substitute(obj=obj_name)
                prop_xml.getroot().text = txt

            new_tag = prop_xml.getroot()
            ref.getparent().replace(ref, new_tag)

        xml.xinclude()
        schema = get_schema()
        schema.assertValid(xml)
    except etree.XMLSyntaxError as e:
        logging.error("XML syntax error:\n \"%s\"\n\twhile parsing file: \"%s\"", e, path)
        return None

    pddoc = xml.getroot()
    for obj in pddoc.findall('object'):
        fix_section_order(obj)

    return xml


def fix_section_order(obj_tag):
    sorted_children = sorted(obj_tag, key=lambda n: ('title',
                                                     'meta', 'info', 'example',
                                                     'mouse', 'arguments', 'properties', 'methods',
                                                     'inlets', 'outlets').index(n.tag))
    for child in obj_tag:
        obj_tag.remove(child)

    for child in reversed(sorted_children):
        obj_tag.insert(0, child)
