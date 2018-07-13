#!/usr/bin/env python
# coding=utf-8

# Copyright (C) 2014 by Serge Poltavski                                   #
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

from os import path
from .canvas import *
from .message import *
from .comment import *
from .coregui import *
from .array import *
from .factory import *


class Parser:
    lines_re = re.compile("^(#(.*?)[^\\\])\r?\n?;\r?\n", re.MULTILINE | re.DOTALL)
    split_re = re.compile(" |\r\n?|\n", re.MULTILINE)

    def __init__(self):
        self.canvas = None
        self.canvas_stack = []
        self._array = None
        self._fname = None

    def parse_declare(self, atoms):
        pass  # TODO
        # print atoms

    def parse_canvas(self, atoms):
        # get positions
        values = []
        for i in range(3, -1, -1):
            if len(atoms) > i:
                values.insert(0, int(atoms[i]))
            else:
                values.insert(0, 0)

        x, y, w, h = values

        # get canvas name
        kwargs = {}
        if len(atoms) >= 4:
            kwargs['name'] = atoms[4]

        c = Canvas(x, y, w, h, **kwargs)

        # root canvas
        if self.canvas is None:
            c.type = Canvas.TYPE_WINDOW
            c._font_size = int(atoms[4])
            self.canvas = c
        else:
            c.type = Canvas.TYPE_SUBPATCH

        self.canvas_stack.append(c)

    def current_canvas(self):
        assert len(self.canvas_stack) > 0
        return self.canvas_stack[-1]

    def parse_frameset(self, atoms):
        if atoms[0] == "canvas":
            atoms.pop(0)
            self.parse_canvas(atoms)
        else:
            logging.warning("unknown frameset type: {0:s}".format(atoms[0]))

    def parse_messages(self, atoms):
        x = atoms[0]
        y = atoms[1]
        atoms.pop(0)
        atoms.pop(0)

        msg = Message(x, y, atoms)
        self.current_canvas().append_object(msg)

    def parse_comments(self, atoms):
        x = atoms[0]
        y = atoms[1]
        comment = Comment(x, y, atoms[2:])
        self.current_canvas().append_object(comment)

    def parse_restore(self, atoms):
        # restore X, Y, TYPE, ARGS
        cnv_type = atoms[2]
        if cnv_type == "graph":
            # self.current_canvas().type = Canvas.TYPE_GRAPH
            # remove canvas from stack
            self.canvas_stack.pop()

            self._array.x = int(atoms[0])
            self._array.y = int(atoms[1])
            # put array instead
            self.current_canvas().append_object(self._array)
            self._array = None
        elif cnv_type == "pd":
            c = self.canvas_stack.pop()
            c.type = Canvas.TYPE_SUBPATCH
            c.x = int(atoms[0])
            c.y = int(atoms[1])
            c._args = atoms[3:]
            self.current_canvas().append_subpatch(c)
        else:
            logging.warning("unknown canvas type: {0:s}".format(cnv_type))
            assert False

    def parse_obj(self, atoms):
        x = atoms[0]
        y = atoms[1]

        obj = make(atoms[2:])
        obj.x = x
        obj.y = y

        self.current_canvas().append_object(obj)

    def parse_array(self, atoms):
        c = self.current_canvas()
        self._array = Array.from_atoms(atoms[1:])
        self._array._cnv_x = c.x
        self._array._cnv_y = c.y
        self._array._cnv_w = c.width
        self._array._cnv_h = c.height

    def parse_array_content(self, atoms):
        assert self._array
        self._array.set_data(atoms)

    def parse_connect(self, atoms):
        c = self.current_canvas()
        c.connect(atoms)

    def parse_coords(self, atoms):
        # syntax
        #X coords [x_from]? [y_to]? [x_to]? [y_from]? [width]? [heigth]? [graph_on_parent]?;\r\n

        if not self._array:
            if int(atoms[7]) > 0:
                self.current_canvas().set_graph_on_parent(True,
                                                          width=int(atoms[5]),
                                                          height=int(atoms[6]),
                                                          xoff=atoms[8],
                                                          yoff=atoms[9],
                                                          hide_args=(int(atoms[7]) == 2))
            return

        self._array.set_xrange(float(atoms[1]), float(atoms[3]))
        self._array.set_yrange(float(atoms[4]), float(atoms[2]))
        self._array.width = int(atoms[5])
        self._array.height = int(atoms[6])

    def parse_objects(self, atoms):
        name = atoms[0]
        if name == 'msg':
            self.parse_messages(atoms[1:])
        elif name == "obj":
            self.parse_obj(atoms[1:])
        elif name == "connect":
            self.parse_connect(atoms[1:])
        elif name == "text":
            self.parse_comments(atoms[1:])
        elif name == "restore":
            # end canvas definition
            self.parse_restore(atoms[1:])
        elif name in("floatatom", "symbolatom"):
            obj = make(atoms)
            self.current_canvas().append_object(obj)
        elif name == "array":
            self.parse_array(atoms)
        elif name == "coords":
            self.parse_coords(atoms)
        elif name == "declare":
            self.parse_declare(atoms)
        else:
            logging.warning("unknown atom: {0:s}, in file \"{1:s}\"".format(name, self._fname))

    def parse_atoms(self, atoms):
        if atoms[0] == '#X':
            self.parse_objects(atoms[1:])
        elif atoms[0] == '#N':
            self.parse_frameset(atoms[1:])
        elif atoms[0] == '#A':
            self.parse_array_content(atoms[2:])
        else:
            logging.info("unknown token: {0:s}".format(atoms[0]))

    def parse_imports(self, lines):
        for found in self.lines_re.finditer(lines):
            line = found.group(1)
            atoms = self.split_re.split(line)
            if atoms[0] == "#X" and atoms[1] == "obj" and atoms[4] == "import":
                add_import(atoms[5])

    def parse_line(self, line):
        self.parse_atoms(self.split_re.split(line))

    def parse(self, file_name):
        if not path.exists(file_name):
            logging.warning("File not exists: \"{0:s}\"".format(file_name))
            return False

        self._fname = file_name
        f = open(file_name, "r")
        lines = f.read()
        f.close()

        self.parse_imports(lines)

        for found in self.lines_re.finditer(lines):
            self.parse_line(found.group(1))

        return True
