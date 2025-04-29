#!/usr/bin/env python
# coding=utf-8
import argparse
import logging
import os

#   Copyright (C) 2015 by Serge Poltavski                                 #
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

from pddoc.pd import factory
from pddoc.pd.obj import PdObject
from pddoc.pd.xletcalculator import XletCalculator

xcalc = XletCalculator(load_externals=False)


def add_xlet_db(path_list):
    for db_path in path_list:
        if not os.path.exists(db_path):
            logging.warning("xlet database file not found: '%s'. skipping...", db_path)
        else:
            xcalc.add_db(db_path, os.path.splitext(os.path.basename(db_path))[0])


def main():
    arg_parser = argparse.ArgumentParser(description='PureData object checker')
    arg_parser.add_argument('name', metavar='OBJECT_NAME', help="PureData object name, for ex.: osc~")
    arg_parser.add_argument('args', metavar='OBJECT_ARGS', nargs='*', help="PureData object arguments")
    arg_parser.add_argument('--search-paths', '-p', metavar='PATH', default=[], nargs='+', help="adds search paths")
    arg_parser.add_argument('--xlet-db', '-x', metavar='PATH', action='append',
                            help='inlet/outlet database file path', default=[])
    arg_parser.add_argument("--debug", action="store_true", help="enable debug mode")

    args = vars(arg_parser.parse_args())
    if args['debug']:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    add_xlet_db(args['xlet_db'])

    for path in args['search_paths']:
        xcalc.add_patch_search_path(path)

    obj = factory.make_by_name(args['name'], args['args'])
    if type(obj) != PdObject:
        print('core:', obj.name)
        return 0

    found = False
    db_name = ""

    for db in reversed(xcalc.databases):
        if db.has_object(obj.name):
            found = True
            db_name = db.extname
            break

    if found:
        print(db_name + ':', obj.name, obj.args_to_string())
        return 0
    else:
        logging.error(f"ERROR: [%s] not found", obj.name)
        return 1


if __name__ == '__main__':
    main()
