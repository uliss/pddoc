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
import copy
import logging
import re

import argostranslate.package
import argostranslate.translate
from lxml import etree


def clear_spaces(txt: str) -> str:
    return re.sub(r"\s+", " ", txt.replace("\n", " ")).strip()


def output_tr(file: str, line: int, tag: str, txt: str):
    # print(f"{file}:{line}:{tag}: '{txt}'")
    print(f"# xml tag: {tag}")
    print(f"#: {file}:{line}")
    print(f"#, fuzzy")

    txt = clear_spaces(txt)
    print(f"msgid \"{txt}\"")

    tr_txt = argostranslate.translate.translate(txt, "en", "ru")
    print(f"msgstr \"{tr_txt}\"\n")


def translate(txt: str, lang_from: str, lang_to: str):
    txt = argostranslate.translate.translate(txt, lang_from, lang_to)
    logging.debug(f"translation: {txt}")
    return txt


def find_no_tr(file: str, path: str, lang: str, root):
    src_tr = root.find(f"{path}[@lang='en']")
    if src_tr is None:  # no translation source found
        logging.warning(f"no translation source found for: {path} at '{file};")
        return

    src_txt = clear_spaces(src_tr.text)
    logging.debug(f"source: {src_txt}")

    tr = root.find(f"{path}[@lang='{lang}']")
    if tr is None:  # no translation found
        tr = copy.deepcopy(src_tr)
        tr.text = translate(src_txt, 'en', lang)
        tr.set("lang", lang)
        tr.set("finished", "false")
        src_tr.addnext(tr)
    elif tr.get("finished", "true") == "true":  # skip finished translation
        logging.info(f"skipping finished translation {path} at '{file}'")
        return
    else:
        tr_txt = translate(src_txt, 'en', lang)
        if tr.text != tr_txt:
            c = etree.Comment(f" old: {tr.text} ")
            tr.addprevious(c)
            tr.text = tr_txt
            tr.set("finished", "false")


def main():
    arg_parser = argparse.ArgumentParser(description='update translations in the object pddoc file')
    arg_parser.add_argument('name', metavar='PDDOC', help="pddoc file")
    arg_parser.add_argument('--lang', '-l', metavar='LANG', choices="ru", default='ru',
                            help='language (currently "ru")')
    arg_parser.add_argument('--in-place', '-i', action='store_true', help='format in place (overwrite source file)')

    args = vars(arg_parser.parse_args())
    in_file = args['name']
    lang = args['lang']

    xml = etree.parse(in_file)
    if not xml:
        exit(-1)

    # xml.xinclude()
    root = xml.getroot()

    find_no_tr(in_file, "object/meta/description/tr", lang, root)

    # for c in root.findall("pddoc/object/meta"):
    #     cat_tr(in_file, c)
    #     for obj in c.findall("entry"):
    #         name = obj.get("name")
    #         find_tr(f"{name}.pddoc", "pddoc/object/meta/description", obj)
    #
    #         find_no_tr(f"{name}.pddoc", "pddoc/object/info/par", obj)
    #         find_no_tr(f"{name}.pddoc", "pddoc/object/arguments/argument", obj)
    #         find_no_tr(f"{name}.pddoc", "pddoc/object/properties/property", obj)
    #         find_no_tr(f"{name}.pddoc", "pddoc/object/methods/method/param", obj)

    etree.indent(xml, space=" ", level=4)

    if args["in_place"]:
        etree.ElementTree(root).write(in_file,
                                      pretty_print=True,
                                      encoding="UTF-8",
                                      xml_declaration=False,
                                      method="xml",
                                      doctype='<?xml version="1.0" encoding="utf-8"?>')
    else:
        print(etree.tostring(xml, pretty_print=True, encoding="UTF-8", xml_declaration=True,
                             method="xml").decode())


if __name__ == '__main__':
    main()
