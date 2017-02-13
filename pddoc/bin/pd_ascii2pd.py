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

__author__ = 'Serge Poltavski'

import argparse
import logging
import os

from pddoc.txt import Parser
from pddoc.pd import Canvas, PdExporter, PdObject
from pddoc import CairoPainter
import pddoc.pd.factory as factory


def main():
    fmt_list = ("png", "pdf", "svg", "pd")
    arg_parser = argparse.ArgumentParser(description='PureData ascii doc to Pd/PDF/SVG converter')
    arg_parser.add_argument('--auto', '-a', help='calculate output image size', action='store_true')
    arg_parser.add_argument('--format', '-f', metavar='FMT', nargs=1, choices=fmt_list,
                            help='output format ({0})'.format(",".join(fmt_list)), default=["pd"])
    arg_parser.add_argument('--width', '-wd', metavar='X', type=int, nargs=1,
                            help='image width in pixels', default=400)
    arg_parser.add_argument('--height', '-ht', metavar='X', type=int, nargs=1,
                            help='image height in pixels', default=300)
    arg_parser.add_argument('--xlet-db', metavar='PATH', action='append',
                            help='inlet/outlet database file path', default=[])
    arg_parser.add_argument('input', metavar='INPUT', help="Documentation file in pd ascii format")
    arg_parser.add_argument('output', metavar='OUTPUT', nargs='?', default='',
                            help="output file name")

    args = vars(arg_parser.parse_args())
    in_file = args['input']
    output = args['output']
    wd = args['width']
    ht = args['height']
    fmt = args['format'][0]

    if not os.path.exists(in_file):
        logging.error("File not exists: \"%s\"", in_file)
        exit(1)

    for db_path in args['xlet_db']:
        if not os.path.exists(db_path):
            logging.warning("xlet database file not found: '%s'. skipping...", db_path)
        else:
            PdObject.xlet_calculator.add_db(db_path)

    if not output:
        output = os.path.splitext(os.path.basename(in_file))[0] + "." + fmt

    factory.add_import('ceammc')

    p = Parser()
    p.parse_file(in_file)

    cnv = Canvas(0, 0, wd, ht)
    cnv.type = Canvas.TYPE_WINDOW
    p.export(cnv)

    if fmt in ('png', 'pdf', 'svg'):
        if args['auto']:
            br_calc = cnv.brect_calc()
            cnv.traverse(br_calc)
            bbox = br_calc.brect()
            wd = bbox[2] + Parser.X_PAD * 2
            ht = bbox[3] + Parser.Y_PAD * 2

        painter = CairoPainter(wd, ht, output, fmt)
        cnv.draw(painter)
    elif fmt == 'pd':
        pd_exporter = PdExporter()
        cnv.traverse(pd_exporter)
        pd_exporter.save(output)
    else:
        print("Unknown output format: {0:s}".format(fmt))

if __name__ == '__main__':
    main()
