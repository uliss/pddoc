#!/usr/bin/env python
# coding=utf-8
import argparse
import logging
import os
from pddoc.parser import parse_xml
from pddoc.pd import factory

from pddoc.htmldocvisitor import HtmlDocVisitor
from pddoc.docobject import DocObject
#   Copyright (C) 2015 by Serge Poltavski                                 #
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
    arg_parser = argparse.ArgumentParser(description='PureData pddoc C++ source generator')
    arg_parser.add_argument('name', metavar='PDDOC', help="Documentation file in PDDOC format")

    args = vars(arg_parser.parse_args())
    in_file = args['name']

    if not os.path.exists(in_file):
        logging.error("File not exists: \"%s\"", in_file)
        exit(1)

    xml = parse_xml(in_file)
    if not xml:
        exit(1)

    factory.add_import('ceammc')

    pddoc = xml.getroot()
    v = pddoc.xpath("//object/meta/description")
    if v is not None:
        print("obj.setDescription(\"{}\");".format(v[0].text))

    authors = pddoc.xpath("//object/meta/authors/author")
    if authors is not None:
        for a in authors:
            print("obj.addAuthor(\"{}\");".format(a.text))

    keywords = pddoc.xpath("//object/meta/keywords")
    if keywords is not None:
        kw = list(map(lambda x: f"\"{x}\"", keywords[0].text.split(" ")))
        print("obj.setKeywords({{{}}});".format(", ".join(kw)))

    category = pddoc.xpath("//object/meta/category")
    if category is not None:
        print("obj.setCategory(\"{}\");".format(category[0].text))

    since = pddoc.xpath("//object/meta/since")
    if since is not None:
        cat = since[0].text.split(".")[:2]
        print("obj.setSinceVersion({}, {});".format(cat[0], cat[1]))


if __name__ == '__main__':
    main()
