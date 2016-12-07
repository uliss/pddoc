#!/usr/bin/env python
# coding=utf-8

# Copyright (C) 2016 by Serge Poltavski                                   #
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
import re


class PdDocVisitor(DocObjectVisitor):
    PD_HEADER_HEIGHT = 40
    PD_HEADER_FONT_SIZE = 20
    PD_HEADER_COLOR = Color(0, 255, 255)
    PD_HEADER_BG_COLOR = Color(100, 100, 100)
    PD_EXAMPLE_YOFFSET = 30
    PD_FOOTER_HEIGHT = 48
    PD_FOOTER_COLOR = Color(180, 180, 180)
    PD_INFO_WINDOW_WIDTH = 400
    PD_INFO_WINDOW_HEIGHT = 250

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
        self.current_yoff += self.PD_EXAMPLE_YOFFSET

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
        inlets.enumerate()

    def inlets_end(self, inlets):
        self.current_yoff += 10

    def inlet_begin(self, inlet):
        self.add_text(140, self.current_yoff, "{0}.".format(inlet.number()))

    def xinfo_begin(self, xinfo):
        self.add_text(160, self.current_yoff,
                      "if *{0}* - {1}".format(xinfo.on(), xinfo.text()))
        self.current_yoff += 20

    def outlets_begin(self, outlets):
        super(self.__class__, self).outlets_begin(outlets)
        self.add_section(self.current_yoff, "outlets:")
        outlets.enumerate()

    def outlets_end(self, outlets):
        self.current_yoff += 10

    def outlet_begin(self, outlet):
        self.add_text(140, self.current_yoff, "{0}.".format(outlet.number()))
        self.add_text(200, self.current_yoff, outlet.text())
        self.current_yoff += 20

    def substitute(self, str):
        str = str.replace("@{LIBRARY}@", self._library)
        str = str.replace("@{CATEGORY}@", self._category)
        return str

    def object_end(self, obj):
        self.add_footer()

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

    def make_txt(self, x, y, txt):
        txt = re.sub(' +', ' ', txt)
        txt = txt.replace('.', '\\.')
        return Comment(x, y, txt.split(' '))

    def add_text(self, x, y, txt):
        self._cnv.append_object(self.make_txt(x, y, txt))

    def make_link(self, x, y, name, url):
        return PdObject("pddplink", x, y, args=[url, "-text", name])

    def add_link(self, x, y, name, url):
        self._cnv.append_object(self.make_link(x, y, name, url))

    def make_delimeter(self, y, **kwargs):
        delim = GCanvas(kwargs.get('x', 20), y, width=kwargs.get('width', 580), height=1, size=1)
        delim._bg_color = Color(200, 200, 200)
        return delim

    def add_delimiter(self, y, **kwargs):
        self._cnv.append_object(self.make_delimeter(y))

    def add_label(self, x, y, txt, **kwargs):
        obj = GCanvas(x, y, **kwargs)
        obj._font_size = int(kwargs.get("font_size", 12))
        obj._label_xoff = int(kwargs.get("x_off", 0))
        obj.label = txt
        obj._label_color = kwargs.get("color", Color.black())
        obj._bg_color = kwargs.get("bgcolor", Color.white())
        self._cnv.append_object(obj)

    def add_section(self, y, txt):
        self.add_delimiter(y)

        lbl = GCanvas(20, y + 10, width=100, height=20, size=10, label=txt, font_size=14)
        lbl._label_color = Color(50, 50, 50)
        self._cnv.append_object(lbl)
        self.current_yoff += 10

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

    def add_footer(self):
        y = self._cnv.height - self.PD_FOOTER_HEIGHT - 2
        bg = GCanvas(1, y, width=self._width - 3, height=self.PD_FOOTER_HEIGHT)
        bg._bg_color = self.PD_FOOTER_COLOR
        self._cnv.append_object(bg)

        # library:
        self.add_text(10, y + 3, "library: {0} v{1}".format(self._library, self._version))

        # see also:
        also_objects = []
        for see in self._see_also:
            obj = PdObject(see['name'], 0, y + 20)
            obj.calc_brect()
            also_objects.append(obj)

        # width with padding
        also_wd = map(lambda x: x.width, also_objects)
        total_wd = sum(also_wd) + 14 * (len(also_wd) - 1)
        x_init_pos = self._width - total_wd - 20
        x_pos = x_init_pos

        for obj in also_objects:
            obj.x = x_pos
            x_pos += obj.width + 14
            self._cnv.append_object(obj)

        self.add_text(x_init_pos - 70, y + 22, "see also:")

        # more info
        pd = Canvas(10, y + 22, self.PD_INFO_WINDOW_WIDTH, self.PD_INFO_WINDOW_HEIGHT, name='info')
        pd.type = Canvas.TYPE_SUBPATCH

        def add_subpatch_text(x, y, txt):
            pd.append_object(self.make_txt(x, y, txt))

        bg1 = GCanvas(1, 1, width=110 - 3, height=self.PD_INFO_WINDOW_HEIGHT - 3)
        bg1._bg_color = self.PD_FOOTER_COLOR
        pd.append_object(bg1)

        xc1 = 10
        xc2 = 120
        yrows = range(10, 300, 22)
        row = 0
        add_subpatch_text(xc1, yrows[row], "library:")
        add_subpatch_text(xc2, yrows[row], self._library)
        row += 1
        add_subpatch_text(xc1, yrows[row], "title:")
        add_subpatch_text(xc2, yrows[row], self._title)
        row += 1
        add_subpatch_text(xc1, yrows[row], "version:")
        add_subpatch_text(xc2, yrows[row], self._version)
        row += 1
        add_subpatch_text(xc1, yrows[row], "category:")
        add_subpatch_text(xc2, yrows[row], self._category)
        row += 1
        add_subpatch_text(xc1, yrows[row], "authors:")
        add_subpatch_text(xc2, yrows[row], " \\, ".join(self._authors))
        row += 1

        add_subpatch_text(xc1, yrows[row], "license:")
        if not self._license.get('url', ' '):
            add_subpatch_text(xc2, yrows[row], self._license['name'])
        else:
            lnk = self.make_link(xc2, yrows[row], self._license['name'], self._license['url'])
            pd.append_object(lnk)
        row += 1

        if self._keywords:
            add_subpatch_text(xc1, yrows[row], "keywords:")
            add_subpatch_text(xc2, yrows[row], " \\, ".join(self._keywords))
            row += 1

        if self._website:
            add_subpatch_text(xc1, yrows[row], "website:")
            lnk = self.make_link(xc2, yrows[row], self._website, self._website)
            pd.append_object(lnk)
            row += 1

        if self._contacts:
            add_subpatch_text(xc1, yrows[row], "contacts:")
            add_subpatch_text(xc2, yrows[row], self._contacts)
            row += 1

        row += 1
        delim = self.make_delimeter(yrows[row], width=270, x=xc2)
        pd.append_object(delim)
        add_subpatch_text(xc2, yrows[row], "autogenerated by pddoc")
        row += 1

        self._cnv.append_subpatch(pd)
