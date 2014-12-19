# /usr/bin/env python

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

from os import path
import re

import common
from pdcanvas  import *
from pdmessage import *
from pdcomment import *
from pdcoregui  import *


class PdParser:
    lines_re = re.compile("(#(.*?)[^\\\])\r{0,1}\n{0,1};\r{0,1}\n", re.MULTILINE | re.DOTALL)
    split_re = re.compile(" |\r\n?|\n", re.MULTILINE)

    def __init__(self):
        self.canvas = None
        self.canvas_stack = []

    def parse_canvas(self, atoms):
        # get positions
        values = []
        for i in xrange(3, -1, -1):
            if len(atoms) > i:
                values.insert(0, int(atoms[i]))
            else:
                values.insert(0, 0)

        x, y, w, h = values

        # get canvas name
        kwargs = {}
        if len(atoms) >= 4:
            kwargs['name'] = atoms[4]

        c = PdCanvas(x, y, w, h, **kwargs)

        # root canvas
        if self.canvas == None:
            c.type = PdCanvas.TYPE_WINDOW
            self.canvas = c

        self.canvas_stack.append(c)


    def current_canvas(self):
        assert len(self.canvas_stack) > 0
        return self.canvas_stack[-1]

    def parse_frameset(self, atoms):
        if atoms[0] == "canvas":
            atoms.pop(0)
            self.parse_canvas(atoms)
        else:
            common.warning("unknown frameset type:" % (atoms[0]))

    def parse_messages(self, atoms):
        x = atoms[0]
        y = atoms[1]
        atoms.pop(0)
        atoms.pop(0)

        msg = PdMessage(x, y, atoms)
        self.current_canvas().append_object(msg)


    def parse_comments(self, atoms):
        x = atoms[0]
        y = atoms[1]
        comment = PdComment(x, y, atoms[2:])
        self.current_canvas().append_object(comment)

    def parse_restore(self, atoms):
        cnv_type = atoms[2]
        if cnv_type == "graph":
            self.current_canvas().type = PdCanvas.TYPE_GRAPH
            c = self.canvas_stack.pop()
            self.canvas.append_graph(c)
        elif cnv_type == "pd":
            self.current_canvas().type = PdCanvas.TYPE_SUBPATCH
            c = self.canvas_stack.pop()
            c.x = int(atoms[0])
            c.y = int(atoms[1])

            if len(self.canvas_stack) > 1:
                self.current_canvas().append_subpatch(c)
            else:
                self.canvas.append_subpatch(c)
        else:
            common.warning("unknown canvas type: %s" % (cnv_type))

    def parse_obj(self, atoms):
        x = atoms[0]
        y = atoms[1]
        name = atoms[2]
        obj = None

        if name in ("bng", "cnv", "hradio", "hsl", "nbx", "tgl", "vradio", "vsl", "vu"):
            obj = PdCoreGui(x, y, atoms[2:])
        else:
            obj = PdObject(x, y, -1, -1, atoms[2:])

        self.current_canvas().append_object(obj)


    def parse_objects(self, atoms):
        name = atoms[0]
        if name == 'msg':
            atoms.pop(0)
            self.parse_messages(atoms)
        elif name == "obj":
            atoms.pop(0)
            self.parse_obj(atoms)
        elif name == "connect":
            pass
        elif name == "text":
            atoms.pop(0)
            self.parse_comments(atoms)
        elif name == "restore":
            # end canvas definition
            atoms.pop(0)
            self.parse_restore(atoms)
        else:
            pass


    def parse_atoms(self, atoms):
        if atoms[0] == '#X':
            atoms.pop(0)
            self.parse_objects(atoms)
        elif atoms[0] == '#N':
            atoms.pop(0)
            self.parse_frameset(atoms)
        else:
            pass

    def parse(self, file_name):
        self.file_name = file_name
        if not path.exists(file_name):
            common.warning("File not exists: \"%s\"" % (file_name))
            return False

        f = open(file_name, "r")
        lines = f.read()
        f.close()

        for found in self.lines_re.finditer(lines):
            line = found.group(1)
            atoms = self.split_re.split(line)
            self.parse_atoms(atoms)

pass


if __name__ == '__main__':
    pd_parser = PdParser()
    pd_parser.parse("tests/simple.pd")

    print pd_parser.canvas