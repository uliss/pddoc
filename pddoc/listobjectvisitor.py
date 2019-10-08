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

import re
import os
import logging

import pddoc.pd as pd
from .txt.parser import Parser
from .pd.canvas import Canvas
from .pd.pdexporter import PdExporter
from .idocobjectvisitor import IDocObjectVisitor


class ListObjectVisitor(IDocObjectVisitor):
    def __init__(self):
        IDocObjectVisitor.__init__(self)

    def object_begin(self, obj):
        self._is_gui = obj.is_gui()

    def alias_begin(self, a):
        print(a.text())

    def pdexample_begin(self, tag):
        self._layout.canvas = pd.Canvas(0, 0, 10, 10, name="10")
        self._layout.canvas.type = pd.Canvas.TYPE_WINDOW

    def pdcomment_begin(self, comment):
        self._layout.comment(comment)

    def pdinclude_begin(self, tag):
        # assert isinstance(tag, DocPdinclude)

        pd_file_path = os.path.join(self._search_dir, tag.file())

        if not os.path.exists(pd_file_path):
            logging.error("Error in tag <pdinclude>: file not exists: \"{0:s}\"".format(pd_file_path))
            return

        parser = pd.Parser()
        if not parser.parse(pd_file_path):
            logging.error("Error in tag <pdexample>: can't process file: {0:s}".format(pd_file_path))
            return

        self._layout.canvas = parser.canvas
        img_id, img_path = self.make_image_id_name()
        # append data to template renderer
        self._pd_append_example(img_id, img_path, pd_file_path, pd_file_path)

        # TODO auto layout
        w, h = self._layout.canvas_brect()[2:]
        self._pd_draw(w, h, img_path)

    def pdascii_begin(self, pdascii):
        self._pdascii = pdascii.text()

        p = Parser()
        p.X_PAD = pdascii.x_pad()
        p.Y_PAD = pdascii.y_pad()
        p.X_SPACE *= pdascii.x_space()
        p.Y_SPACE *= pdascii.y_space()
        if not p.parse(self._pdascii):
            logging.info("<pdascii> parse failed: {0}".format(self._pdascii))

        for n in filter(lambda x: x.is_object() and x.pd_object is not None and x.type == 'OBJECT', p.nodes):
            print(n.pd_object.name, " ".join(n.pd_object.args))

    def see_begin(self, see):
        print(see.text())