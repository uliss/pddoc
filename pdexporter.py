#!/usr/bin/env python

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


# -*- coding: utf-8 -*-

__author__ = 'Serge Poltavski'

from pdcanvas import *
import textwrap

class PdExporter(object):
    def __init__(self):
        self.result = []

    def visit_canvas_begin(self, cnv):
        assert isinstance(cnv, PdCanvas)

        if cnv.type == PdCanvas.TYPE_WINDOW:
            line = "#N canvas {0:d} {1:d} {2:d} {3:d} {4:s};". \
                format(cnv.x, cnv.y, cnv.width, cnv.height, cnv.name)
            self.result.append(line)


    def visit_canvas_end(self, cnv):
        if len(cnv.connections):
            pass

        self.result.append("")

    def visit_comment(self, comment):
        line = "#X text {0:d} {1:d} {2:s};".format(comment.x, comment.y, " ".join(comment.args))
        for l in textwrap.wrap(line):
            self.result.append(l)

    def visit_object(self, obj):
        line = "#X obj {0:d} {1:d} {2:s}".format(obj.x, obj.y, obj.name)

        if len(obj.args):
            line += " " + " ".join(obj.args)

        line += ";"

        self.result.append(line)