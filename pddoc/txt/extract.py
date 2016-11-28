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

from ext_lexer import parse_string
import os.path as path
import re
import sys
import pprint


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
    res = list()
    for line in data:
        res.append(re.sub(r'\s*\/{3}\s+', '', line))
    return ''.join(res)


def process_file(fname):
    if not path.exists(fname):
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


if __name__ == '__main__':
    if len(sys.argv) == 2:
        print "Extracting from: ", sys.argv[1]
        res = process_file(sys.argv[1])
        if res:
            pprint.pprint(res)
