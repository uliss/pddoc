#!/usr/bin/env python
# coding=utf-8
from __future__ import print_function

import argparse
import logging
import os
import re

from jinja2 import Environment, PackageLoader, select_autoescape
from lxml import etree


#   Copyright (C) 2020 by Serge Poltavski                                 #
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

def clear_spaces(txt: str) -> str:
    return re.sub(r"\s+", " ", txt.replace("\n", " "))


def find_translation(node, path: str, lang: str, default: str) -> str:
    tr = node.find(f"{path}/tr[@lang='{lang}']")
    if tr is None:
        tr = node.find(f"{path}/tr[@lang='en']")
        if tr is None:
            tr = node.find(f"{path}")

    if tr is not None:
        return clear_spaces(tr.text)
    else:
        return default


def main():
    arg_parser = argparse.ArgumentParser(description='Converts XML library to markdown page')
    arg_parser.add_argument('input', metavar='LIB_FILE', help="Library description file in XML format")
    arg_parser.add_argument('--aliases', '-a', action='store_true', help='output object aliases')
    arg_parser.add_argument('--force', '-f', action='store_true', help='force to overwrite existing file')
    arg_parser.add_argument('--output', '-o', metavar='OUTPUT', help="output file name")
    arg_parser.add_argument('--locale', '-l', metavar='NAME', choices=("EN", "RU"), default='EN',
                            help='locale (currently EN or RU)')

    args = vars(arg_parser.parse_args())

    if not os.path.exists(args['input']):
        logging.error('no such file: "%s"', args['input'])
        exit(1)

    xml = etree.parse(args['input'])
    xml.xinclude()
    root = xml.getroot()

    if args['output'] and os.path.exists(args['output']) and not args['force']:
        print("Error: file already exists: '{0}'. Use --force flag to overwrite.".format(args['output']))
        exit(2)

    f = None
    if args['output']:
        f = open(args['output'], "w")

    locale = args["locale"]
    lang = 'en'
    # template config
    if "EN" in locale:
        tmpl_path = "md_library_en.tmpl.md"
        tmpl_keys = "md_keys_en.tmpl.md"
        tmpl_methods = "md_methods_en.tmpl.md"
        tmpl_props = "md_props_en.tmpl.md"
        lang = locale.lower()
    elif "RU" in locale:
        tmpl_path = "md_library_ru.tmpl.md"
        tmpl_keys = "md_keys_ru.tmpl.md"
        tmpl_methods = "md_methods_ru.tmpl.md"
        tmpl_props = "md_props_ru.tmpl.md"
        lang = locale.lower()
    else:
        tmpl_path = "md_library_en.tmpl.md"
        tmpl_keys = "md_keys_en.tmpl.md"
        tmpl_methods = "md_methods_en.tmpl.md"
        tmpl_props = "md_props_en.tmpl.md"

    descr = clear_spaces(root.xpath(f"//library/meta/library-info/description[@lang='{lang}']")[0].text)

    info = {
        "name": root.get("name"),
        "version": root.xpath("//library/meta/version")[0].text,
        "descr": descr,
        "website": root.xpath("//library/meta/library-info/website")[0].text,
        "license": root.xpath("//library/meta/library-info/license")[0].text,
        "authors": root.xpath("//library/meta/authors/author")
    }

    data = []
    lang = args['locale'].lower()

    for c in root.findall("category"):
        cat_info_txt = find_translation(c, "category-info", lang, "")

        category = {"name": c.get("name"), "info": cat_info_txt, "objects": []}

        data.append(category)
        # iterate category objects
        for obj in c.findall('entry'):
            descr = find_translation(obj, "pddoc/object/meta/description", lang, "")

            item = {"name": obj.get("name"), "descr": descr, "aliases": []}
            category["objects"].append(item)

            if args['aliases']:
                for a in obj.xpath("pddoc/object/meta/aliases/alias"):
                    item["aliases"].append("\\[%s\\]" % a.text)

    keywords = dict()
    for tag in root.findall(".//keywords"):
        obj = tag.getparent().getparent().findall(".//title")
        obj_name = None
        if len(obj) > 0:
            obj_name = obj[0].text

        for kw in tag.text.strip().split(" "):
            if len(kw) == 0:
                continue

            if kw in keywords:
                keywords[kw].add(obj_name)
            else:
                keywords[kw] = {obj_name}

    env = Environment(
        loader=PackageLoader('pddoc', 'share'),
        autoescape=select_autoescape(['md'])
    )

    template = env.get_template(tmpl_path)
    output_str = template.render(info=info, data=data, keywords=keywords)

    if f is None:
        print(output_str)
    else:
        f.write(output_str + "\n")
        f.close()

    # write keywords
    out_dir = os.path.dirname(args['output'])
    keywords_dir = os.path.join(out_dir, 'keywords')
    if not os.path.exists(keywords_dir):
        os.mkdir(keywords_dir)

    template = env.get_template(tmpl_keys)
    for k, w in keywords.items():
        output_str = template.render(info=info, key=k, obj=sorted(w))
        with open(f"{keywords_dir}/{k}.md", 'w') as f:
            f.write(output_str + "\n")
            f.close()

    # make methods page
    methods = dict()
    for tag in root.findall(".//methods"):
        if "name" not in tag.getparent().attrib:
            continue

        obj_name = tag.getparent().attrib["name"]

        for m in tag:
            if m.tag == "method":
                method_tokens: list[str] = []
                for tok in m.attrib["name"].split(' '):
                    if not tok.isupper():
                        method_tokens.append(tok)

                name = ' '.join(method_tokens)
                if name not in methods:
                    methods[name] = {obj_name}
                else:
                    methods[name].add(obj_name)

    with open(os.path.join(out_dir, "methods.md"), 'w') as f:
        template = env.get_template(tmpl_methods)
        f.write(template.render(info=info, data=methods) + "\n")
        f.close()

    # make properties page
    props = dict()
    for tag in root.findall(".//properties"):
        if "name" not in tag.getparent().attrib:
            continue

        obj_name = tag.getparent().attrib["name"]

        for p in tag:
            if p.tag == "property":
                name = p.attrib["name"]
                if name not in props:
                    props[name] = {obj_name}
                else:
                    props[name].add(obj_name)

    with open(os.path.join(out_dir, "properties.md"), 'w') as f:
        template = env.get_template(tmpl_props)
        f.write(template.render(info=info, data=props) + "\n")
        f.close()


if __name__ == '__main__':
    main()
