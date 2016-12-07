#!/usr/bin/env python
# coding=utf-8
from __future__ import print_function
import argparse
import os
import logging
from pddoc.library import LibraryMaker

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


def check_file(fname):
    if os.path.exists(fname):
        return True
    else:
        logging.error("file not exists: '%s'", fname)
        return False

def main():
    arg_parser = argparse.ArgumentParser(description='PureData XML library tool')
    arg_parser.add_argument('--library', '-l', metavar='NAME', required=True, help="library name")
    arg_parser.add_argument('--output', '-o', metavar='OUTPUT', help="output xml file")
    arg_parser.add_argument('--version', '-v', metavar='version', default="0.0", help="set library version")
    arg_parser.add_argument('pddoc_files', metavar='FILE', nargs='+', help="pddoc files")

    args = vars(arg_parser.parse_args())
    files = filter(check_file, args['pddoc_files'])

    if not files:
        logging.error("no files exists...")
        exit(-1)

    lib = LibraryMaker(args['library'])
    lib.process_files(files)
    lib.sort()
    print(lib)


if __name__ == '__main__':
    main()
