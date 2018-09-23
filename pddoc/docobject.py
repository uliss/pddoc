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
import re

from .idocobjectvisitor import IDocObjectVisitor


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

    def is_empty(self):
        return len(self._elements) == 0

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
                            "also", "category", "since")


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
        self._ref_view = "object"

    def from_xml(self, xmlobj):
        DocItem.from_xml(self, xmlobj)
        self._ref_view = xmlobj.get("view", "object")

    def is_link(self):
        return self._ref_view == "link"


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
    def __init__(self, *args):
        DocItem.__init__(self, args)
        self._ref_view = "object"

    def read_xml_data(self, xmlobj):
        DocItem.read_xml_data(self, xmlobj)
        self._ref_view = xmlobj.attrib.get("view", "object")

    def ref_view(self):
        return self._ref_view


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
        return tag_name in ("pdexample", "pdinclude", "pdascii")


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


class DocPdascii(DocItem):
    def __init__(self, *args):
        DocItem.__init__(self, args)
        self._x_pad = 0
        self._y_pad = 0
        self._x_space = 0
        self._y_space = 0

    def x_pad(self):
        return self._x_pad

    def y_pad(self):
        return self._y_pad

    def x_space(self):
        return self._x_space

    def y_space(self):
        return self._y_space

    def from_xml(self, xmlobj):
        self.read_xml_data(xmlobj)
        try:
            self._x_pad = xmlobj.attrib.get('x-pad', 20)
            self._y_pad = xmlobj.attrib.get('y-pad', 20)
            self._x_space = xmlobj.attrib.get('x-space', 1.2)
            self._y_space = xmlobj.attrib.get('y-space', 1.2)
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
        self._file = xmlobj.attrib.get("file", None)
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

    def is_valid_tag(self, tag_name):
        return tag_name == "alias"


class DocAlias(DocItem):
    def __init__(self, *args):
        DocItem.__init__(self, args)
        self._ref_view = "object"

    def from_xml(self, xmlobj):
        DocItem.from_xml(self, xmlobj)
        self._ref_view = xmlobj.get("view", "object")

    def is_link(self):
        return self._ref_view == "link"


class DocXlets(DocItem):
    def __init__(self, *args):
        DocItem.__init__(self, args)
        self._dynamic = False

    def pd_type_list(self):
        return list(map(lambda x: x.pd_type(), self.items()))

    def enumerate(self):
        # enumerate
        for n in range(len(self.items())):
            self.items()[n].enumerate(n + 1)

    def is_dynamic(self):
        return self._dynamic

    def from_xml(self, xmlobj):
        DocItem.from_xml(self, xmlobj)
        self._dynamic = xmlobj.attrib.get("dynamic", False)


class DocInlets(DocXlets):
    def __init__(self, *args):
        DocXlets.__init__(self, args)

    def is_valid_tag(self, tag_name):
        return tag_name == "inlet"


class DocTypeElement(DocItem):
    allowed_types = ("control", "audio", "gui")

    def __init__(self, *args):
        DocItem.__init__(self, args)
        self._type = "control"

    def is_valid_type(self, t):
        return t in self.allowed_types

    def type(self):
        return self._type

    def from_xml(self, xmlobj):
        self._type = xmlobj.get("type", "control")
        DocItem.from_xml(self, xmlobj)

    def pd_type(self):
        if self._type == "control":
            return 0
        elif self._type == "audio":
            return 1
        elif self._type == "gui":
            return 2
        else:
            return -1


class DocXlet(DocTypeElement):
    def __init__(self, *args):
        DocTypeElement.__init__(self, *args)
        self._number = ""

    def from_xml(self, xmlobj):
        DocTypeElement.from_xml(self, xmlobj)
        self._number = xmlobj.get("number", "")

    def enumerate(self, n):
        if self._number == "":
            self._number = n

    def number(self):
        return self._number


class DocInlet(DocXlet):
    def __init__(self, *args):
        DocXlet.__init__(self, args)

    def is_valid_tag(self, tag_name):
        return tag_name == "xinfo"


class DocXinfo(DocItem):
    def __init__(self, *args):
        DocItem.__init__(self, args)
        self._maxvalue = ""
        self._minvalue = ""
        self._on = ""

    def from_xml(self, xmlobj):
        self._maxvalue = xmlobj.attrib.get("maxvalue", "")
        self._minvalue = xmlobj.attrib.get("minvalue", "")
        self._on = xmlobj.attrib.get("on", "")
        DocItem.from_xml(self, xmlobj)

    def range(self):
        if not self._minvalue and not self._maxvalue:
            return ()

        return self.min(), self.max()

    def on(self):
        return self._on

    def min(self):
        return self._minvalue

    def max(self):
        return self._maxvalue


class DocOutlets(DocXlets):
    def __init__(self, *args):
        DocXlets.__init__(self, args)

    def is_valid_tag(self, tag_name):
        return tag_name == "outlet"


class DocOutlet(DocXlet):
    def __init__(self, *args):
        DocXlet.__init__(self, args)


class DocArgument(DocItem):
    UNIT_MAP = {
        'herz': 'Hz',
        'kiloherz': 'KHz',
        'millisecond': 'ms',
        'second': 'sec',
        'decibel': 'db',
        'bpm': 'bpm',
        'percent': '%',
        'sample': 'samp',
        'msec': 'ms',
        'sec': 'sec'
    }

    def __init__(self, *args):
        DocItem.__init__(self, args)
        self._number = ""
        self._type = ""
        self._units = ""
        self._name = ""
        self._minvalue = ""
        self._maxvalue = ""
        self._default = ""
        self._required = False
        self._enum = []

    def from_xml(self, xmlobj):
        self._name = xmlobj.attrib.get("name", "anonym")
        self._number = xmlobj.attrib.get("number", "")
        self._type = xmlobj.attrib.get("type", "")
        self._units = xmlobj.attrib.get("units", "")
        self._minvalue = xmlobj.attrib.get("minvalue", "")
        self._maxvalue = xmlobj.attrib.get("maxvalue", "")
        self._default = xmlobj.attrib.get("default", "")
        self._required = xmlobj.attrib.get("required", False) == "true"
        enum_str = xmlobj.attrib.get("enum", "").strip()
        if len(enum_str) > 1:
            self._enum = re.split("[ \n\t]+", enum_str)

        DocItem.from_xml(self, xmlobj)

    def type(self):
        return self._type

    def units(self):
        if not self._units:
            return ""

        return self.UNIT_MAP[self._units]

    def name(self):
        return self._name

    def required(self):
        return self._required is True

    def optional(self):
        return self._required is False

    def default(self):
        return self._default

    def number(self):
        return self._number

    def enumerate(self, n):
        if self._number == "":
            self._number = n

    def type_info(self):
        if self._type == "float":
            if self._units:
                return self.units()
            else:
                return "*float*"
        else:
            return self._type

    def main_info_prefix(self):
        res = ""
        if self._name:
            res += "{0}".format(self._name)
        if self._units:
            res += "({0})".format(self.units())

        if res:
            res += ": "
        return res

    def main_info(self):
        res = self.main_info_prefix()
        res += self.text()
        return res.strip()

    def range(self):
        if not self._minvalue and not self._maxvalue:
            return ()

        return self.min(), self.max()

    def min(self):
        return self._minvalue

    def max(self):
        return self._maxvalue

    def enum(self):
        return self._enum


class DocArguments(DocXlets):
    def __init__(self, *args):
        DocXlets.__init__(self, args)

    def is_valid_tag(self, tag_name):
        return tag_name == "argument"


class DocMethods(DocXlets):
    def __init__(self, *args):
        DocXlets.__init__(self, args)

    def is_valid_tag(self, tag_name):
        return tag_name == "method"


class DocMethod(DocItem):
    def __init__(self, *args):
        self._name = ""
        DocItem.__init__(self, args)

    def name(self):
        return self._name

    def is_valid_tag(self, tag_name):
        return tag_name == "param"

    def from_xml(self, xmlobj):
        self._name = xmlobj.attrib.get("name", "")
        DocItem.from_xml(self, xmlobj)


class DocParam(DocArgument):
    def param_name(self):
        if self._units:
            return self.units().upper()
        elif self._name:
            name = self.name()
            if self.default():
                name += '=' + self.default()

            if self.optional():
                name = "[{0}]".format(name)

            return name
        else:
            return "X"


class DocInfo(DocItem):
    def __init__(self, *args):
        DocItem.__init__(self, args)

    def is_valid_tag(self, tag_name):
        return tag_name in ("itemize", "par", "a")


class DocPar(DocItem):
    def __init__(self, *args):
        DocItem.__init__(self, args)


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
        self._type = "box"

    def is_valid_tag(self, tag_name):
        return tag_name in ("title", "meta", "inlets", "outlets",
                            "arguments", "properties", "info", "example", "methods")

    def from_xml(self, xobj):
        self._name = xobj.attrib["name"]
        self._type = xobj.attrib.get("type", "box")
        DocItem.from_xml(self, xobj)

    def name(self):
        return self._name

    def traverse(self, visitor):
        visitor.name = self._name
        DocItem.traverse(self, visitor)

    def is_box(self):
        return self._type == "box"

    def is_gui(self):
        return self._type == "gui"


class DocSince(DocItem):
    def __init__(self, *args):
        DocItem.__init__(self, args)


class DocProperties(DocItem):
    def __init__(self, *args):
        DocItem.__init__(self, args)

    def is_valid_tag(self, tag_name):
        return tag_name == "property"


class DocProperty(DocArgument):
    def __init__(self, *args):
        DocArgument.__init__(self, args)
        self._readonly = False

    def from_xml(self, xmlobj):
        DocArgument.from_xml(self, xmlobj)
        self._readonly = xmlobj.attrib.get("readonly", "false") == "true"
        self._default = xmlobj.attrib.get("default", "")

    def readonly(self):
        return self._readonly

    def is_flag(self):
        return self._type == "flag"

    def is_alias(self):
        return self._type == "alias"
