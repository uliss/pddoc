#!/usr/bin/env python
# coding=utf-8
from __future__ import print_function

import argparse
import logging
import os

from pddoc.libraryparser import LibraryParser


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


def main():
    arg_parser = argparse.ArgumentParser(description='Converts XML library to Pd patch')
    arg_parser.add_argument('input', metavar='INPUT', help="Library description file in XML format")
    arg_parser.add_argument('--locale', '-l', metavar='NAME', choices=("EN", "RU"), default='EN',
                            help='locale (currently EN or RU)')
    arg_parser.add_argument('--xlet-db-dir', metavar='PATH', action='append',
                            help='inlet/outlet database file directory', default=[])
    args = vars(arg_parser.parse_args())

    lang = args['locale'].lower()

    if not os.path.exists(args['input']):
        logging.error('no such file: "%s"', args['input'])
        exit(-1)

    lp = LibraryParser(args['input'])
    lp.lang = lang
    for db in args['xlet_db_dir']:
        lp.add_xlet_db_dir(db)

    lp.process()
    # lp.process_categories()
    with open(lp.lib_name() + "-help.pd", "w") as f:
        f.write(str(lp))


if __name__ == '__main__':
    main()
