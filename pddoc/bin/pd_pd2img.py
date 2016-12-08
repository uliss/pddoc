#!/usr/bin/env python
# coding=utf-8
import argparse
import os.path

from pddoc.cairopainter import *
from pddoc.pd import Parser
from format import detect_format

# Copyright (C) 2014 by Serge Poltavski                                 #
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


def main():
    arg_parser = argparse.ArgumentParser(description='Converts Pd patch to image')
    arg_parser.add_argument('--format', '-f', metavar='format', nargs=1, choices=("png", "pdf", "svg"),
                            help='output image format')
    arg_parser.add_argument('--width', metavar='px', nargs=1, help='image width in pixels')
    arg_parser.add_argument('--height', metavar='px', nargs=1, help='image height in pixels')
    arg_parser.add_argument('input', metavar='PATCH')
    arg_parser.add_argument('output', metavar='OUTNAME', nargs='?', default='image.png')

    args = vars(arg_parser.parse_args())

    pd_parser = Parser()

    finput = args['input']
    if not os.path.exists(finput):
        logging.error("File not exists: \"%s\"", finput)
        exit(1)

    pd_parser.parse(finput)

    width = pd_parser.canvas.width
    height = pd_parser.canvas.height

    if args['width'] is not None:
        width = int(args['width'][0])

    if args['height'] is not None:
        width = int(args['height'][0])

    fmt = detect_format(args)
    painter = CairoPainter(width, height, args['output'], fmt)
    pd_parser.canvas.draw(painter)


if __name__ == '__main__':
    main()
