#!/usr/bin/env python

# Copyright (C) 2014 by Serge Poltavski                                 #
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


# -*- coding: utf-8 -*-

__author__ = 'Serge Poltavski'

import common
import xml.etree.ElementTree as ET


def make_class_name(tag_name):
    return "Doc%s" % (tag_name.capitalize())


def create_instance(tag_name, *args):
    class_name = make_class_name(tag_name)
    obj = globals()[class_name](args)
    return obj


class DocItem(object):
    def __init__(self):
        self._elements = []
        self._text = ""

    def text(self):
        return self._text

    def is_valid_tag(self, tag_name):
        return False

    def add_child(self, element):
        self._elements.append(element)

    def clear(self):
        self._elements = []

    def num_children(self):
        return len(self._elements)

    def traverse(self, visitor):
        mname = self.__class__.__name__[3:].lower()
        method = mname + "_begin"
        if hasattr(visitor, method):
            getattr(visitor, method)(self)

        self.traverse_children(visitor)

        method = mname + "_end"
        if hasattr(visitor, method):
            getattr(visitor, method)(self)

    def traverse_children(self, visitor):
        for e in self._elements:
            e.traverse(visitor)

    def from_xml(self, xmlobj):
        self._text = xmlobj.text

        for child in xmlobj:
            if not self.is_valid_tag(child.tag):
                common.warning("tag <%s> not allowed in <%s>" % (child.tag, xmlobj.tag))
                continue
                # break

            obj = create_instance(child.tag)
            obj.from_xml(child)
            self.add_child(obj)


class DocTitle(DocItem):
    def __init__(self, *args):
        super(self.__class__, self).__init__()


class DocMeta(DocItem):
    def __init__(self, *args):
        super(self.__class__, self).__init__()

    def is_valid_tag(self, tag_name):
        return tag_name in ("description", "authors", "contacts",
                            "license", "version", "website",
                            "aliases", "keywords", "library")


class DocDescription(DocItem):
    def __init__(self, *args):
        super(self.__class__, self).__init__()


class DocAuthors(DocItem):
    def __init__(self, *args):
        super(self.__class__, self).__init__()

    def is_valid_tag(self, tag_name):
        return tag_name in ("author")


class DocAuthor(DocItem):
    def __init__(self, *args):
        super(self.__class__, self).__init__()


class DocContacts(DocItem):
    def __init__(self, *args):
        super(self.__class__, self).__init__()


class DocLibrary(DocItem):
    def __init__(self, *args):
        super(self.__class__, self).__init__()


class DocVersion(DocItem):
    def __init__(self, *args):
        super(self.__class__, self).__init__()


class DocLicense(DocItem):
    def __init__(self, *args):
        super(self.__class__, self).__init__()
        self._url = ""

    def from_xml(self, xmlobj):
        self._url = xmlobj.attrib.get("url", "")
        super(self.__class__, self).from_xml(xmlobj)


class DocExample(DocItem):
    def __init__(self, *args):
        super(self.__class__, self).__init__()

    def is_valid_tag(self, tag_name):
        return tag_name in ("pdexample")


class DocPdmessage(DocItem):
    def __init__(self, *args):
        DocItem.__init__(self)
        self._id = ""
        self._comment = ""

    def from_xml(self, xmlobj):
        try:
            self._id = xmlobj.attrib["id"]
            self._msg = xmlobj.attrib["text"]
            self._common = xmlobj.attrib.get("comment", "")
            DocItem.from_xml(self, xmlobj)
        except KeyError, e:
            common.warning("required attribute not found: \"%s\" in <%s>" % (e.message, xmlobj.tag))


class DocPdobject(DocItem):
    def __init__(self, *args):
        DocItem.__init__(self)
        self._id = ""
        self._name = ""
        self._args = ""
        self._comment = ""

    def is_valid_tag(self, tag_name):
        return tag_name in ("pdinlet", "pdoutlet")

    def name(self):
        return self._name

    def from_xml(self, xmlobj):
        try:
            self._id = xmlobj.attrib["id"]
            self._name = xmlobj.attrib["name"]
            self._args = xmlobj.attrib.get("args", "")
            DocItem.from_xml(self, xmlobj)
        except KeyError, e:
            common.warning("required attribute not found: \"%s\" in <%s>" % (e.message, xmlobj.tag))


class DocPdinlet(DocItem):
    def __init__(self, *args):
        DocItem.__init__(self)


class DocPdoutlet(DocItem):
    def __init__(self, *args):
        DocItem.__init__(self)


class DocRow(DocItem):
    def __init__(self, *args):
        DocItem.__init__(self)

    def is_valid_tag(self, tag_name):
        return tag_name in ("col", "pdmessage", "pdobject")


class DocCol(DocItem):
    def __init__(self, *args):
        DocItem.__init__(self)

    def is_valid_tag(self, tag_name):
        return tag_name in ("row", "pdmessage", "pdobject")


class DocPdinclude(DocItem):
    def __init__(self, *args):
        DocItem.__init__(self)
        self._file = ""

    def from_xml(self, xmlobj):
        self._file = xmlobj.attrib["file"]
        DocItem.from_xml(self, xmlobj)

class DocPdconnect(DocItem):
    def __init__(self, *args):
        DocItem.__init__(self)
        self._src_id = ""
        self._dest_id = ""
        self._src_out = None
        self._dest_in = None

    def from_xml(self, xmlobj):
        self._src_out = int(xmlobj.attrib["src_out"])
        self._dest_in = int(xmlobj.attrib["dest_in"])
        self._dest_id = xmlobj.attrib["dest"]
        self._src_id = xmlobj.attrib["src"]
        DocItem.from_xml(self, xmlobj)

class DocPdexample(DocItem):
    def __init__(self, *args):
        super(self.__class__, self).__init__()
        self._width = 0
        self._height = 0

    def is_valid_tag(self, tag_name):
        return tag_name in ("row", "col", "pdconnect", "pdinclude")

    def from_xml(self, xmlobj):
        self._width = int(xmlobj.attrib["width"])
        self._height = int(xmlobj.attrib["height"])
        DocItem.from_xml(self, xmlobj)

    def width(self):
        return int(self._width)

    def height(self):
        return int(self._height)


class DocWebsite(DocItem):
    def __init__(self, *args):
        super(self.__class__, self).__init__()


class DocKeywords(DocItem):
    def __init__(self, *args):
        super(self.__class__, self).__init__()
        self._keywords = []

    def from_xml(self, xmlobj):
        self._keywords = xmlobj.text.split(" ")
        super(self.__class__, self).from_xml(xmlobj)

    def keywords(self):
        return self._keywords


class DocAliases(DocItem):
    def __init__(self, *args):
        super(self.__class__, self).__init__()
        self._aliases = []

    def from_xml(self, xmlobj):
        for child in xmlobj:
            if child.tag == "alias":
                self._aliases.append(child.text)


class DocXlets(DocItem):
    def __init__(self, *args):
        DocItem.__init__(self)

    def xlet_dict(self):
        res = {}
        for inl in self._elements:
            n = inl._number
            if not res.has_key(n):
                res[n] = []

            res[n].append(inl)

        return res


class DocInlets(DocXlets):
    def __init__(self, *args):
        super(self.__class__, self).__init__()

    def is_valid_tag(self, tag_name):
        return tag_name == "inlet"

    def inlet_dict(self):
        return self.xlet_dict()


class DoxTypeElement(DocItem):
    allowed_types = ("bang", "float", "list", "symbol", "pointer", "any")

    def __init__(self, *args):
        DocItem.__init__(self)
        self._type = ""

    def is_valid_type(self, t):
        return t in self.allowed_types

    def type(self):
        return self._type

    def from_xml(self, xmlobj):
        self._type = xmlobj.attrib["type"]
        DocItem.from_xml(self, xmlobj)


class DocXlet(DoxTypeElement):
    def __init__(self, *args):
        DoxTypeElement.__init__(self, *args)
        self._maxvalue = ""
        self._minvalue = ""
        self._number = ""

    def from_xml(self, xmlobj):
        self._maxvalue = xmlobj.attrib.get("maxvalue", "")
        self._minvalue = xmlobj.attrib.get("minvalue", "")
        self._number = xmlobj.attrib["number"]
        DoxTypeElement.from_xml(self, xmlobj)

    def range(self):
        if not self._minvalue and not self._maxvalue:
            return ()

        return (float(self._minvalue), float(self._maxvalue))


class DocInlet(DocXlet):
    def __init__(self, *args):
        DocXlet.__init__(self, args)


class DocOutlets(DocXlets):
    def __init__(self, *args):
        DocXlets.__init__(self, args)

    def is_valid_tag(self, tag_name):
        return tag_name == "outlet"

    def outlet_dict(self):
        return self.xlet_dict()


class DocOutlet(DocXlet):
    def __init__(self, *args):
        DocXlet.__init__(self, args)


class DocArgument(DoxTypeElement):
    def __init__(self, *args):
        DoxTypeElement.__init__(self, args)


class DocArguments(DocItem):
    def __init__(self, *args):
        super(self.__class__, self).__init__()

    def is_valid_tag(self, tag_name):
        return tag_name == "argument"

    def argument_count(self):
        return len(self._elements)


class DocInfo(DocItem):
    def __init__(self, *args):
        super(self.__class__, self).__init__()


class DocObject(DocItem):
    def __init__(self):
        super(self.__class__, self).__init__()
        self._name = ""

    def is_valid_tag(self, tag_name):
        return tag_name in ("title", "meta", "inlets", "outlets", "arguments", "info", "example")

    def from_xml(self, xobj):
        self._name = xobj.attrib["name"]
        DocItem.from_xml(self, xobj)


if __name__ == '__main__':
    dobj = DocObject()

    import htmldocvisitor

    xml = ET.parse("tests/float.pddoc")
    pddoc = xml.getroot()
    for child in pddoc:
        if child.tag == "object":
            dobj.from_xml(child)

            v = htmldocvisitor.HtmlDocVisitor()
            dobj.traverse(v)

            s = str(v)
            f = open("test.html", "w")
            f.write(s)
            f.close()
            break


