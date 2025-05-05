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
    tr_tags = root.findall(f"{path}[@lang='en']")
    if len(tr_tags) == 0:  # no translation source found
        logging.warning(f"no translation source found for: {path} at '{file};")
        return

    for tag in tr_tags:
        src_txt = clear_spaces(tag.text)
        logging.debug(f"source: {src_txt}")

        tr = None
        for x in tag.getparent():
            if x.get("lang") == lang:
                tr = x
                break

        if tr is None:  # no translation found
            tr = copy.deepcopy(tag)
            tr.text = translate(src_txt, 'en', lang)
            tr.set("lang", lang)
            tr.set("finished", "false")
            tag.addnext(tr)
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


def check_translations(xml, lang: str, verbose: bool):
    xml.xinclude()
    root = xml.getroot()

    check_description_tr(lang, root, verbose)
    check_categories_tr(lang, root, verbose)


def check_categories_tr(lang, root, verbose):
    all_cats = root.xpath(f"//*/category[@name]")
    info_cats = root.xpath(f"//*/category-info")
    tr_cats = root.xpath(f"//*/category-info/tr[@lang='{lang}']")
    all_cats_set = set(map(lambda x: x.get("name"), all_cats))
    info_cats_set = set(map(lambda x: x.getparent().get("name"), info_cats))
    no_info_cats_set = all_cats_set - info_cats_set
    logging.info(f"info categories:        {len(info_cats):8}\n"
                 f"translated categories:  {len(tr_cats):8}\n"
                 f"total categories:       {len(all_cats):8}")
    if verbose and len(no_info_cats_set) > 0:
        logging.warning(
            f"categories without info ({len(no_info_cats_set)}):\n\t{'\n\t'.join(sorted(list(no_info_cats_set)))}")
    tr_cats_set = set(map(lambda x: x.getparent().getparent().get("name"), tr_cats))
    no_tr_cats_set = all_cats_set - tr_cats_set
    if verbose and len(no_tr_cats_set) > 0:
        logging.warning(
            f"categories without '{lang}' tr ({len(no_tr_cats_set)}):\n\t{'\n\t'.join(sorted(list(no_tr_cats_set)))}")


def check_description_tr(lang, root, verbose):
    num_obj = root.xpath(f"//*/object")
    num_tr = root.xpath(f"//*/description/tr[@lang='{lang}' and (not(@finished) or @finished!='false')]")
    unfinished = root.xpath(f"//*/description/tr[@lang='{lang}' and @finished='false']")
    logging.info(f"translated objects:      {len(num_tr): 8}\n"
                 f"unfinished translations: {len(unfinished): 8}\n"
                 f"total objects:           {len(num_obj): 8}\n"
                 f"progress:                {int(len(num_tr) / len(num_obj) * 100): 7}%")

    if verbose and len(unfinished) > 0:
        # object/meta/description/tr
        obj_lst = list(map(lambda x: "[" + x.getparent().getparent().getparent().get("name") + "]", unfinished))
        logging.warning(f"unfinished translations for '{lang}':\n\t{'\n\t'.join(obj_lst)}")

        all_obj = set(map(lambda x: x.getparent().getparent().get("name"), num_obj))
        all_tr = set(map(lambda x: x.getparent().getparent().getparent().get("name"), num_tr))
        non_tr = all_obj - all_tr
        logging.warning(f"non translated objects:")
        logging.info(f"\t{'\n\t-> '.join(sorted(non_tr))}")


def main():
    arg_parser = argparse.ArgumentParser(description='update translations in the object pddoc file')
    arg_parser.add_argument('name', metavar='PDDOC', help="pddoc file")
    arg_parser.add_argument('--lang', '-l', metavar='LANG', choices=("ru",), default='ru',
                            help='language (currently "ru")')
    arg_parser.add_argument('--translate', '-t', action='store_true', help='translate pddoc')
    arg_parser.add_argument('--update', '-u', action='store_true', help='update pddoc xml')
    arg_parser.add_argument('--check', '-c', action='store_true', help='checks translations')
    arg_parser.add_argument('--verbose', '-v', action='store_true', help='verbose output')
    arg_parser.add_argument('--in-place', '-i', action='store_true', help='format in place (overwrite source file)')

    args = vars(arg_parser.parse_args())
    in_file = args['name']
    lang = args['lang']
    verbose = args['verbose']

    xml = etree.parse(in_file)
    if not xml:
        exit(-1)

    if args['check']:
        return check_translations(xml, lang, verbose)

    # xml.xinclude()
    root = xml.getroot()

    if args['translate']:
        find_no_tr(in_file, "object/meta/description/tr", lang, root)
        find_no_tr(in_file, "object/arguments/argument/tr", lang, root)

    if args['update']:
        obj = root.find("object")
        if obj is not None:
            logging.debug(f"update object: [{obj.get('name')}]")
        # add property translations
        for arg in root.findall("object/properties/property"):
            if arg.find("tr") is None:
                tr = etree.Element('tr', lang='en')
                tr.text = clear_spaces(arg.text)
                arg.text = ""
                arg.append(tr)
                logging.info(f"adding translation for property '{arg.get('name')}'")
            else:
                logging.debug(f"skipping translated property: '{arg.get('name')}'")

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

    return 0


if __name__ == '__main__':
    main()
