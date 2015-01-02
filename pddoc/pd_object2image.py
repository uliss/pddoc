#!/usr/bin/env python
# coding=utf-8

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

from cairopainter import *
from pdobject import *
from brectcalculator import *
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

def draw_object(object, fname, format, **kwargs):
    w, h = BRectCalculator().object_brect(object)[2:]
    pad = 1 # pixel
    w += pad
    h += pad

    painter = CairoPainter(int(w), int(h), fname, format, **kwargs)
    painter.draw_object(object)

def main():
    arg_parser = argparse.ArgumentParser(description='PureData patch to image converter')
    arg_parser.add_argument('--format', '-f', metavar='format', nargs=1, choices=("png", "pdf", "svg"),
                            help='output image format')
    arg_parser.add_argument('name', metavar='OBJECT_NAME', help="PureData object name, for ex.: osc~")
    arg_parser.add_argument('output', metavar='OUTNAME', nargs='?', default='',
                            help="Image output name, for ex.: float.png")

    args = vars(arg_parser.parse_args())

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
    draw_object(pdo, output, fmt)


if __name__ == '__main__':
    main()