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

from __future__ import print_function
from ext_lexer import parse_string
import os
import re
import sys
import pprint
from mako.template import Template
from pddoc.txt import Parser
from pddoc.pd import Canvas, PdExporter, PdObject
from pddoc import CairoPainter
import argparse


def extract_doc_comment(data):
    res = list()
    is_doc = False

    for line in data:
        if re.match(r'\s*\/\*(\*|\!)', line):
            is_doc = True

        if re.match(r'\s*\*+\/', line):
            res.append(line)
            break

        if is_doc:
            res.append(line)

    return res


def extract_doc_example(data):
    res = list()
    is_example = False

    for line in data:
        if re.match(r'\s*\/\/\/\s*(@|\\)pddoc\s+', line):
            is_example = True

        if re.match(r'\s*\/\/\/\s*(@|\\)pddoc_end', line):
            res.append(line)
            break

        if is_example:
            res.append(line)

    return res


def graph_source(data):
    if len(data) < 2:
        return ''

    res = list()
    for line in data[1:-1]:
        res.append(re.sub(r'\s*\/{2,3}\s+', '', line))
    return ''.join(res)


def process_file(fname):
    if not os.path.exists(fname):
        print("file not exists: \"{0}\"".format(fname), file=sys.stderr)
        return None

    with open(fname, 'r') as myfile:
        res = {}
        data = myfile.readlines()

        doc = extract_doc_comment(data)
        if doc:
            res_doc = parse_string(''.join(doc))
            if res_doc:
                res['doc'] = res_doc

        example = extract_doc_example(data)
        if example:
            res['example'] = graph_source(example)

        return res


def generate_sphynx(data):
    main = data['doc'][0]
    info = data['doc'][1]
    res = '## {0}:{1}\n\n'.format(info['library'], info['name'])
    res += '{0}\n\n'.format(main)

    if 'args' in info:
        res += '### arguments\n\n'
        for i in info['args']:
            res += '# {0}\n'.format(i['args'])

    if 'inlet' in info:
        res += '### inlets\n\n'
        for i in info['inlet']:
            res += '# {0}\n'.format(i['info'])

    if 'outlet' in info:
        res += '\n### outlets\n\n'
        for i in info['outlet']:
            res += '# {0}\n'.format(i['info'])

    # res += '.. version: {0}\n'.format(data['version'])
    return res


def generate_pddoc(data, args):
    # template config
    tmpl_path = "{0:s}/../share/extract.pddoc".format(os.path.dirname(os.path.abspath(__file__)))
    pddoc_template = Template(filename=tmpl_path)
    doc = data['doc'][1]


    template_data = {}
    template_data['name'] = doc['name']
    template_data['description'] = doc.get('brief')
    template_data['license'] = doc.get('license', 'Unknown')
    template_data['library'] = doc.get('library', 'misc')
    template_data['version'] = doc.get('version', '0.0.0')
    template_data['category'] = doc.get('category', '')
    template_data['website'] = doc.get('website', '')
    template_data['authors'] = doc['author'].split(',')
    template_data['example'] = data.get('example')

    if 'inlet' in doc:
        PdObject.xlet_calculator.mem_db.add_object(doc['name'], [0], [0])

    ext_name = doc.get('name', 'unknown')
    xlet_db = "example_{0}.db".format(ext_name)

    # save xlet db
    with open(xlet_db, 'w') as db:
        str = doc['name'] + "\t"

        if doc['inlet']:
            for i in doc['inlet']:
                if i['type'] == 'control':
                    str += '.'
                elif i['type'] == 'sound':
                    str += '~'
                else:
                    print("unknown inlet type: {0}".format(i['type']))
        else:
            str += '-'

        str += '\t'

        if doc['outlet']:
            for i in doc['inlet']:
                if i['type'] == 'control':
                    str += '.'
                elif i['type'] == 'sound':
                    str += '~'
                else:
                    print("unknown outlet type: {0}".format(i['type']))
        else:
            str += '-'

        str += '\n'

        db.write(str)

    if 'see' in doc:
        template_data['see_also'] = doc['see'].split(',')

    # keywords = self._keywords,
    # css_file = self._css_file,
    # css = self._css,
    # aliases = self._aliases,
    # version = self._version,
    # inlets = self._inlets,
    # outlets = self._outlets,
    # arguments = self._arguments,
    # contacts = self._contacts,

    return pddoc_template.render(**template_data)


def main():
    arg_parser = argparse.ArgumentParser(description='PureData C/C++ comment extractor')
    arg_parser.add_argument('--xdens', metavar='xdens', default=1, type=float,
                            help="horizontal space between objects")
    arg_parser.add_argument('--ydens', metavar='ydens', default=1, type=float,
                            help="vertical space between objects")
    arg_parser.add_argument('input', metavar='SOURCE', help="C/C++ extension source file")
    args = vars(arg_parser.parse_args())

    res = process_file(args['input'])
    if not res:
        sys.exit(1)

    print(generate_pddoc(res, args))


if __name__ == '__main__':
    main()

