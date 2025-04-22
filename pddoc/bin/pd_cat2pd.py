#!/usr/bin/env python
# coding=utf-8
import argparse
import logging
import os

from pddoc.categoryparser import CategoryParser


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
    arg_parser = argparse.ArgumentParser(description='Converts XML library to Pd category patches')
    arg_parser.add_argument('input', metavar='INPUT', help="Library description file in XML format")
    arg_parser.add_argument('--locale', '-l', metavar='NAME', choices=("EN", "RU"), default='EN',
                            help='locale (currently EN or RU)')
    args = vars(arg_parser.parse_args())

    if not os.path.exists(args['input']):
        logging.error('no such file: "%s"', args['input'])
        exit(-1)

    cp = CategoryParser(args['input'])
    cp.lang = args['locale'].lower()
    cp.process()


if __name__ == '__main__':
    main()
