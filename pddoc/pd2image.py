#!/usr/bin/env python
# coding=utf-8

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

from pdparser import *
from cairopainter import *
import argparse
import os.path


def detect_format(args):
    if args['format'] is None:
        name, ext = os.path.splitext(args['output'].lower())
        if len(ext) > 2:
            ext = ext[1:]
        else:
            ext = None
    else:
        ext = args['format'][0].lower()

    if ext not in ('png', 'pdf', 'svg'):
        raise ValueError("output format not supported or can't be detected")

    return ext


def main():
    arg_parser = argparse.ArgumentParser(description='PureData patch to image converter')
    arg_parser.add_argument('--format', '-f', metavar='format', nargs=1, choices=("png", "pdf", "svg"),
                            help='output image format')
    arg_parser.add_argument('--width', metavar='px', nargs=1, help='image width in pixels')
    arg_parser.add_argument('--height', metavar='px', nargs=1, help='image height in pixels')
    arg_parser.add_argument('input', metavar='PATCH')
    arg_parser.add_argument('output', metavar='OUTNAME', nargs='?', default='image.png')

    args = vars(arg_parser.parse_args())

    pd_parser = PdParser()
    pd_parser.parse(args['input'])

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