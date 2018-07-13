#!/usr/bin/env python
# coding=utf-8
import textwrap

from .canvas import Canvas
from .abstractvisitor import AbstractVisitor

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


from .array import Array
import re


class PdExporter(AbstractVisitor):
    def __init__(self):
        self.result = []

    def visit_canvas_begin(self, cnv):
        assert isinstance(cnv, Canvas)

        if cnv.type == Canvas.TYPE_WINDOW:
            line = "#N canvas {0:d} {1:d} {2:d} {3:d} {4};". \
                format(cnv.x, cnv.y, cnv.width, cnv.height, cnv.font_size)
            self.result.append(line)
        elif cnv.type == Canvas.TYPE_SUBPATCH:
            line = "#N canvas {0:d} {1:d} {2:d} {3:d} {4:s} 0;". \
                format(cnv.x, cnv.y, cnv.width, cnv.height, cnv.name)
            self.result.append(line)
        elif cnv.type == Canvas.TYPE_GRAPH:
            gline = "#N canvas {0:d} {1:d} {2:d} {3:d} {4:s} 0;". \
                format(cnv.x, cnv.y, cnv.width, cnv.height, cnv.name)
            self.result.append(gline)
        else:
            pass

    def visit_graph(self, graph):
        pass

    def visit_subpatch(self, spatch):
        pass

    def visit_canvas_end(self, cnv):
        if cnv.type == Canvas.TYPE_WINDOW:
            self.result.append("")
        elif cnv.type == Canvas.TYPE_SUBPATCH:
            line = "#X restore {0:d} {1:d} pd {2:s};".format(cnv.x, cnv.y, cnv.name)
            self.result.append(line)
        pass

    def visit_connection(self, conn):
        line = "#X connect {0:d} {1:d} {2:d} {3:d};".format(conn[0].id, conn[1], conn[2].id, conn[3])
        self.result.append(line)

    def visit_comment(self, comment):
        txt = re.sub('\s+', ' ', " ".join(comment.args).strip())
        line = "#X text {0:d} {1:d} {2:s};".format(comment.x, comment.y, txt)
        for l in textwrap.wrap(line):
            self.result.append(l)

    def visit_object(self, obj):
        if isinstance(obj, Array):
            line = "#N canvas {0:d} {1:d} {2:d} {3:d} {4:s} {5:d};". \
                format(obj._cnv_x, obj._cnv_y, obj._cnv_w, obj._cnv_h, "(subpatch)", 0)
            self.result.append(line)

            line = "#X array {0:s} {1:d} float {2:d};".format(obj.name, obj.size(), obj.save_flag())
            self.result.append(line)

            line = "#A 0 " + " ".join(map(lambda x: "{0:g}".format(x), obj.data())) + ";"
            for l in textwrap.wrap(line, 70):
                self.result.append(l)

            # X coords [x_from]? [y_to]? [x_to]? [y_from]? [width]? [heigth]? [graph_on_parent]?;\r\n
            line = "#X coords {0:g} {1:g} {2:g} {3:g} {4:g} {5:d} {6:d};".format(
                obj.xrange()[0], obj.yrange()[1],
                obj.xrange()[0] + obj.size(), obj.yrange()[0],
                obj.width, obj.height, 1
            )
            self.result.append(line)

            # restore
            line = "#X restore {0:d} {1:d} graph;".format(obj.x, obj.y)
            self.result.append(line)
            return
        else:
            line = "#X obj {0:d} {1:d} {2:s}".format(obj.x, obj.y, obj.name)

        if len(obj.args):
            line += " " + " ".join(obj.args)

        line += ";"

        w = textwrap.TextWrapper()
        w.break_long_words = False
        w.break_on_hyphens = False
        w.width = 70

        for l in w.wrap(line):
            self.result.append(l)

        # handle declare
        if obj.name == "declare":
            self.result.insert(1, "#X declare {0:s};".format(" ".join(obj.args)))

    def visit_core_gui(self, gui):
        line = " ".join(map(str, gui.to_atoms())) + ";"
        for l in textwrap.wrap(line, 70):
            self.result.append(l)

    def visit_message(self, msg):
        txt = self.escape_tokens(msg.args_to_string())
        line = "#X msg {0:d} {1:d} {2:s};".format(msg.x, msg.y, txt)
        self.result.append(line)

    def save(self, fname):
        f = open(fname, 'w')
        f.write("\n".join(self.result))
        f.close()

    @classmethod
    def escape_tokens(cls, s):
        return s.replace(',', ' \\,').replace('$', '\\$')
