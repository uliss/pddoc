#!/usr/bin/env python
# coding=utf-8

#   Copyright (C) 2025 by Serge Poltavski                                 #
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

import language_tool_python
from lxml import etree


def check_description_tr(tool, lang: str, root, verbose: bool):
    descriptions = root.xpath(f"//*/description/tr[@lang='{lang}' and (not(@finished) or @finished!='false')]")
    for d in descriptions:
        src_text = ' '.join(d.text.split())
        correct = tool.correct(src_text)
        if correct != src_text:
            objname = d.getparent().getparent().getparent().get("name")
            logging.debug(f"[{objname}]")
            logging.warning(f"source: {src_text}\n"
                            f"update: {correct}\n")


def main():
    arg_parser = argparse.ArgumentParser(description='update translations in the object pddoc file')
    arg_parser.add_argument('name', metavar='PDDOC', help="pddoc file")
    arg_parser.add_argument('--lang', '-l', metavar='LANG', choices=("en", "ru",), default='en',
                            help='language (currently "en", "ru")')
    arg_parser.add_argument('--verbose', '-v', action='store_true', help='verbose output')
    arg_parser.add_argument('--in-place', '-i', action='store_true', help='format in place (overwrite source file)')

    args = vars(arg_parser.parse_args())
    in_file = args['name']
    lang = args['lang']
    verbose = args['verbose']

    xml = etree.parse(in_file)
    if not xml:
        exit(-1)

    xml.xinclude()
    root = xml.getroot()

    tool = language_tool_python.LanguageTool('en-US',
                                             config={'rulesFile': '.languagetool.cfg'})

    check_description_tr(tool, lang, root, verbose)

    tool.close()
    return 0


if __name__ == '__main__':
    main()
