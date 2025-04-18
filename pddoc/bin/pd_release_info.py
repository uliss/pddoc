#!/usr/bin/env python
# coding=utf-8
from __future__ import print_function

import argparse
import logging
import os
import re
from datetime import datetime

from lxml import etree

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

from pddoc.pd.obj import PdObject
from pddoc.pdpage import PdPage

CLEAR_SPACES_RE = re.compile(r"\s+")

TR_MAP = {
    "New objects ({}):": {
        "ru": "Новые объекты ({}):"
    },
    "Date: {}": {
        "ru": "Дата: {}"
    },
    "CEAMMC release: v{}": {
        "ru": "CEAMMC версия: v{}"
    },
}


def clean_descr(txt: str) -> str:
    txt = txt.replace("\n", " ").replace("\r", "")
    return re.sub(CLEAR_SPACES_RE, " ", txt)


def tr(key: str, lang: str) -> str:
    if lang == "en":
        return key

    if key not in TR_MAP:
        return key

    key_tr = TR_MAP.get(key)
    return key_tr.get(lang, key)


def main():
    arg_parser = argparse.ArgumentParser(description='Create release info')
    arg_parser.add_argument('--release', '-r', metavar='release', default='0.0', help='release version')
    arg_parser.add_argument('--lang', '-l', metavar='lang', default='en', choices=['en', 'ru'], help='output language')
    arg_parser.add_argument('--force', '-f', action='store_true', help='force to overwrite existing file')
    arg_parser.add_argument('libname', metavar='XMLFILE', help="library xml file")
    arg_parser.add_argument('output', metavar='FNAME', help="Pd output name (without extension)")

    args = vars(arg_parser.parse_args())
    output_pd = args['output'] + ".pd"
    output_txt = args['output'] + ".txt"
    libname = args['libname']
    version = args['release']
    lang = args['lang']

    if not os.path.isfile(libname) or not os.path.exists(libname):
        print(f"Error: pddoc library is not found: '{libname}'")
        exit(1)

    if os.path.exists(output_pd) and not args['force']:
        print("Error: file already exists: '{0}'. Use --force flag to overwrite.".format(output_pd))
        exit(1)

    xml = etree.parse(libname)
    if not xml:
        exit(2)

    xml.xinclude()
    pddoc = xml.getroot()

    left_margin = 20
    page = PdPage("obj", 600, 600)
    title = PdObject("ui.label {} @size 450 50".format(tr("CEAMMC release: v{}", lang).format(version)), x=left_margin,
                     y=20)
    page.append_object(title)
    left_margin += 10
    yoff = 120
    left_margin += 10
    descr_x = left_margin + 190
    obj_count = 0

    txt_content = ""

    for meta in pddoc.findall(".//object/meta"):
        since = meta.find("since")
        if since is None:
            continue

        if since.text != version:
            continue

        obj = meta.getparent().get("name")

        tr_i18n = meta.find(f"./description/tr[@lang='{lang}']")
        if tr_i18n is None:
            tr_i18n = meta.find(f"./description/tr[@lang='en']")
            if tr_i18n is None:
                logging.error(f"{obj}: description tr not found, skipping")
                continue

        pd_obj = PdObject(obj, left_margin, yoff)
        page.append_object(pd_obj)

        obj_descr = clean_descr(tr_i18n.text)
        comment = page.add_txt(f"– {obj_descr}", descr_x, yoff, width=46)
        comment.calc_brect()
        yoff += comment.brect()[3] + 20
        obj_count += 1

        txt_content += f"[{obj}] – {obj_descr}\n"

    txt_content = tr("New objects ({}):", lang).format(obj_count) + "\n" + txt_content
    txt_content = tr("CEAMMC release: v{}", lang).format(version) + "\n" + txt_content

    page.add_txt(tr("New objects ({}):", lang).format(obj_count), left_margin, 80)
    date = datetime.today().strftime('%Y-%m-%d')
    page.add_txt(tr("Date: {}", lang).format(date), left_margin, yoff, width=46)

    with open(output_pd, 'w') as f:
        f.write(page.to_string())

    with open(output_txt, 'w') as f:
        f.write(txt_content)


if __name__ == '__main__':
    main()
