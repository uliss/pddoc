#!/usr/bin/env python
# coding=utf-8
import argparse

from pddoc.cairopainter import *
from pddoc.pd import PdObject, BRectCalculator
from format import detect_format

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

import os


def add_xlet_db(path_list):
    for db_path in path_list:
        if not os.path.exists(db_path):
            logging.warning("xlet database file not found: '%s'. skipping...", db_path)
        else:
            PdObject.xlet_calculator.add_db(db_path)


def draw_object(obj, fname, fmt, **kwargs):
    w, h = BRectCalculator().object_brect(obj)[2:]

    pad = kwargs['pad'][0]
    w += pad * 2
    h += pad * 2

    painter = CairoPainter(int(w), int(h), fname, fmt, xoffset=pad, yoffset=pad)
    painter.draw_object(obj)


def main():
    arg_parser = argparse.ArgumentParser(description='PureData patch to image converter')
    arg_parser.add_argument('--format', '-f', metavar='format', nargs=1, choices=("png", "pdf", "svg"),
                            help='output image format')
    arg_parser.add_argument('--pad', '-p', metavar='padding', nargs=1, type=int, default=[1],
                            help="adds padding around object")
    arg_parser.add_argument('name', metavar='OBJECT_NAME', help="PureData object name, for ex.: osc~")
    arg_parser.add_argument('output', metavar='OUTNAME', nargs='?', default='',
                            help="Image output name, for ex.: float.png")
    arg_parser.add_argument('--xlet-db', '-x', metavar='PATH', action='append',
                            help='inlet/outlet database file path', default=[])

    args = vars(arg_parser.parse_args())

    add_xlet_db(args['xlet_db'])

    pdo = PdObject(args['name'])

    if not args['output']:
        if args['format']:
            output = "{0:s}.{1:s}".format(args['name'], args['format'][0].lower())
        else:
            output = args['name'] + ".png"
            args['output'] = output
    else:
        output = args['output']

    fmt = detect_format(args)
    draw_object(pdo, output, fmt, pad=args['pad'])


if __name__ == '__main__':
    main()
