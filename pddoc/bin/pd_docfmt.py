#!/usr/bin/env python
# coding=utf-8
from __future__ import print_function

import argparse

#   Copyright (C) 2023 by Serge Poltavski                                 #
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

from pddoc.parser import PddocFormatParser


def main():
    arg_parser = argparse.ArgumentParser(description='format pddoc file')
    arg_parser.add_argument('--in-place', '-i', action='store_true', help='format in place (overwrite source file)')
    arg_parser.add_argument('name', metavar='PDDOC', help="Documentation file in PDDOC(XML) format")

    args = vars(arg_parser.parse_args())
    in_file = args['name']

    pddoc = PddocFormatParser(in_file)
    if not pddoc.is_ok():
        exit(1)

    pddoc.sort_sections()
    pddoc.strip_finished_tr()
    pddoc.strip_blanks()
    pddoc.sort_and_comment_methods()
    pddoc.sort_and_comment_properties()

    if args["in_place"]:
        pddoc.save_to(in_file)
    else:
        print(pddoc.to_string())


if __name__ == '__main__':
    main()
