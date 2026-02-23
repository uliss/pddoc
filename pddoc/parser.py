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
import re
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
                for tr in prop_xml.getroot():
                    tmpl = Template(tr.text)
                    obj_name = os.path.basename(path)[:-6]  # strip .pddoc extension
                    obj_name = obj_name.replace("~", "").replace(".", "_")
                    txt = tmpl.substitute(obj=obj_name)
                    tr.text = txt

            new_tag = prop_xml.getroot()
            ref.getparent().replace(ref, new_tag)

        for ref in xml.xpath('//pddoc/object/methods/*[local-name()="include"]'):
            # manual XInclude implementation with template substitution
            prop_xml = etree.parse(dirname + "/" + ref.attrib["href"])
            # if ref.attrib.get("subst", "true") != "false":
            #     for tr in prop_xml.getroot():
            #         tmpl = Template(tr.text)
            #         obj_name = os.path.basename(path)[:-6]  # strip .pddoc extension
            #         obj_name = obj_name.replace("~", "").replace(".", "_")
            #         txt = tmpl.substitute(obj=obj_name)
            #         tr.text = txt
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


def tag_index(name):
    return (
        "title", "meta", "info", "mouse", "arguments", "properties", "methods", "inlets", "outlets",
        "example").index(
        name)


class PddocFormatParser:
    def __init__(self, xml_file: str):
        parser = etree.XMLParser(resolve_entities=False,
                                 strip_cdata=False,
                                 remove_blank_text=False)
        self._xml = etree.parse(xml_file, parser)
        if not self._xml:
            return

        self._pddoc = self._xml.getroot()
        pddoc_version = self._pddoc.get("version", "1.0")
        obj = self._pddoc.getchildren()[0]

        self._pddoc = etree.Element(self._pddoc.tag,
                                    version=pddoc_version,
                                    nsmap={"xi": "http://www.w3.org/2001/XInclude"})
        self._pddoc.insert(0, obj)

    def is_ok(self):
        return self._pddoc is not None

    def strip_finished_tr(self):
        if self._pddoc is None:
            return

        # strip @lang finished=true
        for tr in self._pddoc.findall("**/description/tr[@finished='true']"):
            tr.attrib.pop("finished")

    def get_root(self):
        return self._pddoc.getchildren()[0]

    def sort_sections(self):
        if self._pddoc is None:
            return

        for r in self.get_root().iter("object"):
            r[:] = sorted(r, key=lambda x: tag_index(x.tag))

    def strip_blanks(self):
        if self._pddoc is None:
            return

        for elem in self.get_root().iter('*'):
            if elem.tag not in ("method", "property", "pdascii") and elem.text is not None:
                elem.text = elem.text.strip()

            if elem.tag == "pdascii":
                txt = elem.text.rstrip().lstrip("\n")
                elem.text = etree.CDATA("\n" + txt + "\n")

    def sort_and_comment_methods(self):
        if self._pddoc is None:
            return

        obj = self.get_root()
        # remove old method comments
        for comment in obj.xpath('//object/methods/comment()'):
            comment.getparent().remove(comment)

        # sort methods ny name
        for m in obj.iter("methods"):
            m[:] = sorted(m, key=lambda x: x.get("name", ""))

        # add new comments
        for m in obj.xpath('//object/methods/*'):
            name = m.get("name", "")
            # skip comments ending with '-'
            if name == "" or name.find("--") > 0 or name.endswith('-'):
                continue

            c = etree.Comment(' ' + m.attrib["name"] + ' ')
            m.addprevious(c)

    def sort_and_comment_properties(self):
        if self._pddoc is None:
            return

        obj = self.get_root()
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

    def to_string(self) -> str:
        if self._pddoc is None:
            return ""

        etree.indent(self._pddoc, space="  ", level=0)

        xml_str = etree.tostring(self._pddoc,
                                 pretty_print=True,
                                 encoding="UTF-8",
                                 xml_declaration=False,
                                 method="xml",
                                 doctype='<?xml version="1.0" encoding="utf-8"?>').decode()

        pattern = r"(<pdascii id=[^>]+>)(<!\[CDATA\[)"

        xml_str = xml_str \
            .replace("<pdascii><![CDATA[", "<pdascii>\n<![CDATA[") \
            .replace("]]></pdascii>",
                     "]]>\n      </pdascii>")

        xml_str = re.sub(pattern, r"\1\n<![CDATA[", xml_str)
        return xml_str

    def save_to(self, file) -> bool:
        if self._pddoc is None:
            return False

        with open(file, 'w') as f:
            f.write(self.to_string())
            return True
