#!/usr/bin/env python
# coding=utf-8

# Copyright (C) 2014 by Serge Poltavski                                 #
# serge.poltavski@gmail.com                                             #
# #
# This program is free software; you can redistribute it and/or modify  #
# it under the terms of the GNU General Public License as published by  #
# the Free Software Foundation; either version 3 of the License, or     #
# (at your option) any later version.                                   #
# #
# This program is distributed in the hope that it will be useful,       #
# but WITHOUT ANY WARRANTY; without even the implied warranty of        #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         #
#   GNU General Public License for more details.                          #
#                                                                         #
#   You should have received a copy of the GNU General Public License     #
#   along with this program. If not, see <http://www.gnu.org/licenses/>   #

__author__ = 'Serge Poltavski'

import logging

from idocobjectvisitor import IDocObjectVisitor


def make_class_name(tag_name):
    return "Doc%s" % (tag_name.capitalize())


def create_instance(tag_name, *args):
    class_name = None
    try:
        class_name = make_class_name(tag_name)
        obj = globals()[class_name](args)
        return obj
    except KeyError:
        logging.error("Class not found: %s", class_name)
        exit(1)


class DocVisitorError(Exception):
    def __init__(self, message):
        self._msg = message

    def __str__(self):
        return "VisitorError: {0:s}".format(self._msg)


class DocItem(object):
    def __init__(self, *args):
        self._elements = []
        self._text = ""

        if len(args) > 1:
            self._text = args[0]

    def items(self):
        return self._elements

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
        assert isinstance(visitor, IDocObjectVisitor)

        try:
            mprefix = self.__class__.__name__[3:].lower()
            method = mprefix + "_begin"
            getattr(visitor, method)(self)
            # if hasattr(visitor, method):  # call element_begin() method
            #     getattr(visitor, method)(self)

            self.traverse_children(visitor)

            method = mprefix + "_end"
            # if hasattr(visitor, method):  # call element_end() method
            #     getattr(visitor, method)(self)
            getattr(visitor, method)(self)

        except DocVisitorError as e:
            logging.error(e)

    def traverse_children(self, visitor):
        for e in self._elements:
            e.traverse(visitor)

    def read_xml_data(self, xmlobj):
        self._text = xmlobj.text

    def from_xml(self, xmlobj):
        self.read_xml_data(xmlobj)

        for child in xmlobj:
            # skip XML comments
            if callable(child.tag):
                continue

            if not self.is_valid_tag(child.tag):
                logging.warning("tag <%s> not allowed in <%s>" % (child.tag, xmlobj.tag))
                continue
                # break

            obj = create_instance(child.tag)
            obj.from_xml(child)
            self.add_child(obj)


class DocTitle(DocItem):
    def __init__(self, *args):
        DocItem.__init__(self, args)


class DocMeta(DocItem):
    def __init__(self, *args):
        DocItem.__init__(self, args)

    def is_valid_tag(self, tag_name):
        return tag_name in ("description", "authors", "contacts",
                            "license", "version", "website",
                            "aliases", "keywords", "library",
                            "also", "category")


class DocDescription(DocItem):
    def __init__(self, *args):
        DocItem.__init__(self, args)


class DocAuthors(DocItem):
    def __init__(self, *args):
        DocItem.__init__(self, args)

    def is_valid_tag(self, tag_name):
        return tag_name in ("author",)


class DocAuthor(DocItem):
    def __init__(self, *args):
        DocItem.__init__(self, args)


class DocAlso(DocItem):
    def __init__(self, *args):
        DocItem.__init__(self, args)

    def is_valid_tag(self, tag_name):
        return tag_name == "see"


class DocSee(DocItem):
    def __init__(self, *args):
        DocItem.__init__(self, args)


class DocContacts(DocItem):
    def __init__(self, *args):
        DocItem.__init__(self, args)


class DocLibrary(DocItem):
    def __init__(self, *args):
        DocItem.__init__(self, args)


class DocVersion(DocItem):
    def __init__(self, *args):
        DocItem.__init__(self, args)


class DocCategory(DocItem):
    pass


class DocLicense(DocItem):
    def __init__(self, *args):
        DocItem.__init__(self, args)
        self._url = ""
        self._name = ""

    def read_xml_data(self, xmlobj):
        self._url = xmlobj.attrib.get("url", "")
        self._name = xmlobj.text

    def url(self):
        return self._url

    def name(self):
        return self._name


class DocExample(DocItem):
    def __init__(self, *args):
        DocItem.__init__(self, args)

    def is_valid_tag(self, tag_name):
        return tag_name in ("pdexample", "pdinclude")


class DocPdobject(DocItem):
    def __init__(self, *args):
        DocItem.__init__(self, args)
        self._id = ""
        self._name = ""
        self._args = ""
        self._comment = ""
        self._offset = 0
        self._highlight = False
        self._attrs = {}

    @property
    def id(self):
        return self._id

    def is_valid_tag(self, tag_name):
        return tag_name in ("pdinlet", "pdoutlet")

    def highlight(self):
        return self._highlight == "true"

    def name(self):
        return self._name

    def offset(self):
        return self._offset

    def from_xml(self, xmlobj):
        try:
            self._id = xmlobj.attrib["id"]
            self._name = xmlobj.attrib["name"]
            self._args = xmlobj.attrib.get("args", "")
            self._comment = xmlobj.attrib.get("comment", "")
            self._offset = int(xmlobj.attrib.get("offset", "0"))
            self._highlight = xmlobj.attrib.get("highlight", "")

            # save other attrs
            for k, v in xmlobj.attrib.items():
                if k not in ('id', 'name', 'args', 'comment', 'offset', 'highlight'):
                    self._attrs[k] = v

            DocItem.from_xml(self, xmlobj)
        except KeyError as e:
            logging.warning("required attribute not found: \"%s\" in <%s>" % (e.message, xmlobj.tag))

    @property
    def comment(self):
        return self._comment

    def args(self):
        return self._args.split(" ")

    def attrs(self):
        return self._attrs


class DocPdmessage(DocPdobject):
    def __init__(self, *args):
        DocPdobject.__init__(self, args)

    def is_valid_tag(self, name):
        return False

    def from_xml(self, xmlobj):
        try:
            self._id = xmlobj.attrib["id"]
            self._comment = xmlobj.attrib.get("comment", "")
            self._offset = int(xmlobj.attrib.get("offset", "0"))
            DocItem.from_xml(self, xmlobj)
            # after parent method
            self._text = xmlobj.attrib["text"]
        except KeyError as e:
            logging.warning("required attribute not found: \"%s\" in <%s>" % (e.message, xmlobj.tag))


class DocPdinlet(DocItem):
    def __init__(self, *args):
        DocItem.__init__(self, args)


class DocPdinclude(DocItem):
    def __init__(self, *args):
        DocItem.__init__(self, args)
        self._file = None
        self._size = "auto"

    def file(self):
        return self._file

    def size(self):
        return self._size

    def from_xml(self, xmlobj):
        try:
            self._file = xmlobj.attrib['file']
            self._size = xmlobj.attrib.get('size', 'auto')
            assert self._size in ("auto", "canvas")
        except KeyError as e:
            logging.warning("attribute \"%s\" not found in <%s>", e.args[0], xmlobj.tag)


class DocPdoutlet(DocItem):
    def __init__(self, *args):
        DocItem.__init__(self, args)


class DocRow(DocItem):
    def __init__(self, *args):
        DocItem.__init__(self, args)

    def is_valid_tag(self, tag_name):
        return tag_name in ("col", "pdmessage", "pdobject", "pdcomment")


class DocCol(DocItem):
    def __init__(self, *args):
        DocItem.__init__(self, args)

    def is_valid_tag(self, tag_name):
        return tag_name in ("row", "pdmessage", "pdobject", "pdcomment")


class DocPdconnect(DocItem):
    def __init__(self, *args):
        DocItem.__init__(self, args)
        self._src_id = ""
        self._dest_id = ""
        self._src_out = None
        self._dest_in = None

    def src_id(self):
        return self._src_id

    def dest_id(self):
        return self._dest_id

    def from_xml(self, xmlobj):
        self._src_out = int(xmlobj.attrib["src_out"])
        self._dest_in = int(xmlobj.attrib["dest_in"])
        self._dest_id = xmlobj.attrib["dest"]
        self._src_id = xmlobj.attrib["src"]
        DocItem.from_xml(self, xmlobj)


class DocPdcomment(DocItem):
    def __init__(self, *args):
        DocItem.__init__(self, args)


class DocPdexample(DocItem):
    def __init__(self, *args):
        DocItem.__init__(self, args)
        self._width = 0
        self._height = 0
        self._file = ""
        self._size = ""
        self._title = ""

    def is_valid_tag(self, tag_name):
        return tag_name in ("row", "col", "pdconnect")

    def from_xml(self, xmlobj):
        size = xmlobj.attrib.get("size", None)
        if size:
            if size in ("auto", "canvas"):
                self._size = size
            else:
                logging.warning("invalid size value: \"{0:s}\" in <{1:s}>".format(size, xmlobj.tag))

        self._width = int(xmlobj.attrib.get("width", 0))
        self._height = int(xmlobj.attrib.get("height", 0))
        self._title = xmlobj.attrib.get("title", "")
        DocItem.from_xml(self, xmlobj)

    def file(self):
        return self._file

    def width(self):
        return self._width

    def height(self):
        return self._height

    def size(self):
        return self._size

    def title(self):
        return self._title


class DocWebsite(DocItem):
    def __init__(self, *args):
        DocItem.__init__(self, args)


class DocKeywords(DocItem):
    def __init__(self, *args):
        DocItem.__init__(self, args)
        self._keywords = []

    def from_xml(self, xmlobj):
        self._keywords = xmlobj.text.split(" ")
        super(self.__class__, self).from_xml(xmlobj)

    def keywords(self):
        return self._keywords


class DocAliases(DocItem):
    def __init__(self, *args):
        DocItem.__init__(self, args)
        self._aliases = []

    def aliases(self):
        return self._aliases

    def from_xml(self, xmlobj):
        for child in xmlobj:
            if child.tag == "alias":
                self._aliases.append(child.text)


class DocXlets(DocItem):
    def __init__(self, *args):
        DocItem.__init__(self, args)

    def xlet_dict(self):
        res = {}
        for inl in self.items():
            n = inl.number()
            if n not in res:
                res[n] = []

            res[n].append(inl)

        return res


class DocInlets(DocXlets):
    def __init__(self, *args):
        DocXlets.__init__(self, args)

    def is_valid_tag(self, tag_name):
        return tag_name == "inlet"

    def inlet_dict(self):
        return self.xlet_dict()


class DoxTypeElement(DocItem):
    allowed_types = ("bang", "float", "list", "symbol", "pointer", "any")

    def __init__(self, *args):
        DocItem.__init__(self, args)
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

    def number(self):
        return int(self._number)

    def from_xml(self, xmlobj):
        self._maxvalue = xmlobj.attrib.get("maxvalue", "")
        self._minvalue = xmlobj.attrib.get("minvalue", "")
        self._number = xmlobj.attrib["number"]
        DoxTypeElement.from_xml(self, xmlobj)

    def range(self):
        if not self._minvalue and not self._maxvalue:
            return ()

        return float(self._minvalue), float(self._maxvalue)


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
        DocItem.__init__(self, args)

    def is_valid_tag(self, tag_name):
        return tag_name == "argument"

    def argument_count(self):
        return len(self._elements)


class DocInfo(DocItem):
    def __init__(self, *args):
        DocItem.__init__(self, args)

    def is_valid_tag(self, tag_name):
        return tag_name in ("itemize", "p", "a")


class DocA(DocItem):
    def __init__(self, *args):
        DocItem.__init__(self, args)
        self._url = None

    @property
    def url(self):
        return self._url

    def from_xml(self, xmlobj):
        self._url = xmlobj.attrib["href"]
        DocItem.from_xml(self, xmlobj)


class DocItemize(DocItem):
    def __init__(self, *args):
        DocItem.__init__(self, args)

    def is_valid_tag(self, tag_name):
        return tag_name in ("item",)


class DocObject(DocItem):
    def __init__(self, *args):
        DocItem.__init__(self, args)
        self._name = ""

    def is_valid_tag(self, tag_name):
        return tag_name in ("title", "meta", "inlets", "outlets", "arguments", "info", "example")

    def from_xml(self, xobj):
        self._name = xobj.attrib["name"]
        DocItem.from_xml(self, xobj)
