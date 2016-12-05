#!/usr/bin/env python
# coding=utf-8

# Copyright (C) 2016 by Serge Poltavski                                 #
#   serge.poltavski@gmail.com                                            #
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

from docobjectvisitor import DocObjectVisitor
from pd.canvas import Canvas
from pd.pdexporter import PdExporter
from pd.gcanvas import GCanvas
from pd.coregui import Color
from pd.comment import Comment
from pd.parser import Parser
from pd.obj import PdObject
from pd.factory import make_by_name
import logging
import os


class PdDocVisitor(DocObjectVisitor):
    PD_HEADER_HEIGHT = 40
    PD_HEADER_FONT_SIZE = 20
    PD_HEADER_COLOR = Color(0, 255, 255)
    PD_HEADER_BG_COLOR = Color(100, 100, 100)
    PD_EXAMPLE_YOFFSET = 40

    def __init__(self):
        DocObjectVisitor.__init__(self)

        pd_parser = Parser()
        tmpl_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "share/doc_template.pd")
        if not os.path.exists(tmpl_path):
            logging.error("File not exists: \"%s\"", tmpl_path)

        self.current_yoff = 0
        pd_parser.parse(tmpl_path)

        self._cnv = pd_parser.canvas
        self._cnv.type = Canvas.TYPE_WINDOW
        self._width = self._cnv.width

    def meta_end(self, meta):
        self.add_header()
        self.current_yoff += self.PD_HEADER_HEIGHT + 30

    def pdascii_begin(self, t):
        cnv = super(self.__class__, self).pdascii_begin(t)

        for obj in cnv.objects:
            obj.y += self.current_yoff
            obj.x += self.PD_EXAMPLE_YOFFSET
            self._cnv.append_object(obj)

        for conn in cnv.connections.values():
            self._cnv.add_connection(conn[0].id, conn[1], conn[2].id, conn[3])

        self.current_yoff += cnv.height

    # def pdinclude_begin(self, t):
    #     db_path = os.path.splitext(t.file())[0] + '.db'
    #     PdObject.xlet_calculator.add_db(db_path)
    #
    #     pd_parser = Parser()
    #     pd_parser.parse(t.file())
    #     cnv = pd_parser.canvas
    #     for obj in cnv.objects:
    #         obj.y += self.current_yoff
    #         obj.x += self.PD_EXAMPLE_YOFFSET
    #         self._cnv.append_object(obj)
    #
    #     for conn in cnv.connections.values():
    #         self._cnv.add_connection(conn[0].id, conn[1], conn[2].id, conn[3])
    #
    #     self.current_yoff += cnv.height

    def example_end(self, tag):
        pass
        # self.add_delimiter(self.current_yoff)
        # self.current_yoff += 5

    def inlets_begin(self, inlets):
        super(self.__class__, self).inlets_begin(inlets)
        self.add_section(self.current_yoff, "inlets:")
        self.current_yoff += 20

    def outlets_begin(self, outlets):
        super(self.__class__, self).outlets_begin(outlets)
        self.add_section(self.current_yoff, "outlets:")
        self.current_yoff += 20

    def substitute(self, str):
        str = str.replace("@{LIBRARY}@", self._library)
        str = str.replace("@{CATEGORY}@", self._category)
        return str

    def render(self):
        pd_exporter = PdExporter()
        self._cnv.traverse(pd_exporter)
        return map(self.substitute, pd_exporter.result)
        # return self._html_template.render(
        #     title=self._title,
        #     description=self._description,
        #     keywords=self._keywords,
        #     css_file=self._css_file,
        #     css=self._css,
        #     aliases=self._aliases,
        #     license=self._license,
        #     version=self._version,
        #     examples=self._examples,
        #     inlets=self._inlets,
        #     outlets=self._outlets,
        #     arguments=self._arguments,
        #     see_also=self._see_also,
        #     website=self._website,
        #     authors=self._authors,
        #     contacts=self._contacts,
        #     library=self._library,
        #     category=self._category)

    def add_delimiter(self, y):
        delim = GCanvas(20, y, width=480, height=1, size=1)
        delim._bg_color = Color(200, 200, 200)
        self._cnv.append_object(delim)

    def add_text(self, x, y, txt, **kwargs):
        obj = GCanvas(x, y, **kwargs)
        obj._font_size = int(kwargs.get("font_size", 12))
        obj._label_xoff = int(kwargs.get("x_off", 0))
        obj.label = txt
        obj._label_color = kwargs.get("color", Color.black())
        obj._bg_color = kwargs.get("bgcolor", Color.white())
        self._cnv.append_object(obj)

    def add_section(self, y, txt):
        self.add_delimiter(y)

        lbl = GCanvas(20, y + 5, width=100, height=20, size=10, label=txt, font_size=14)
        lbl._label_color = Color(50, 50, 50)
        self._cnv.append_object(lbl)
        self.current_yoff += 16

    def add_header(self):
        lbl = GCanvas(1, 1, width=self._width - 3, height=self.PD_HEADER_HEIGHT, size=10,
                      label="{0}".format(self._title), font_size=self.PD_HEADER_FONT_SIZE,
                      label_yoff=18, label_xoff=10)
        lbl._label_color = self.PD_HEADER_COLOR
        lbl._bg_color = self.PD_HEADER_BG_COLOR

        self._cnv.append_object(lbl)

        example_obj = make_by_name(self._title)
        brect = example_obj.brect_calc().object_brect(example_obj)
        x = lbl.width - brect[2] - 20
        y = (lbl.height - brect[3]) / 2
        example_obj.x = x
        example_obj.y = y

        self._cnv.append_object(example_obj)


