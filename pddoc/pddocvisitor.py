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
from pd.obj import PdObject
from pd.factory import make_by_name
import re
from pd.externals.pddp.pddplink import PddpLink


class PdDocVisitor(DocObjectVisitor):
    PD_WINDOW_WIDTH = 685
    PD_WINDOW_HEIGHT = 555
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
        self.current_yoff = 0
        self._cnv = self.make_main_canvas()

    def window_width(self):
        return self._cnv.width

    def window_height(self):
        return self._cnv.height

    def make_main_canvas(self):
        cnv = Canvas(0, 0, self.PD_WINDOW_WIDTH, self.PD_WINDOW_HEIGHT, font_size=12)
        cnv.type = Canvas.TYPE_WINDOW
        return cnv

    def meta_end(self, meta):
        self.add_header()

        self.current_yoff += self.PD_HEADER_HEIGHT
        self.current_yoff += 30

    def pdascii_begin(self, t):
        cnv = super(self.__class__, self).pdascii_begin(t)
        self.copy_canvas_objects(cnv)
        self.copy_canvas_connections(cnv)

        self.current_yoff += cnv.height
        self.current_yoff += self.PD_EXAMPLE_YOFFSET

    def copy_canvas_connections(self, cnv):
        for conn in cnv.connections.values():
            self._cnv.add_connection(conn[0].id, conn[1], conn[2].id, conn[3])

    def copy_canvas_objects(self, cnv):
        for obj in cnv.objects:
            obj.y += self.current_yoff
            obj.x += self.PD_EXAMPLE_YOFFSET
            self._cnv.append_object(obj)

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

    def inlets_begin(self, inlets):
        super(self.__class__, self).inlets_begin(inlets)
        self.add_section(self.current_yoff, "inlets:")
        inlets.enumerate()

    def inlets_end(self, inlets):
        self.current_yoff += 10

    def inlet_begin(self, inlet):
        self.add_text(120, self.current_yoff, "{0}.".format(inlet.number()))

    def xinfo_begin(self, xinfo):
        tlist = []
        t1 = self.add_text(150, self.current_yoff, "*{0}*".format(xinfo.on()))
        tlist.append(t1)
        t2 = self.add_text(230, self.current_yoff, xinfo.text())
        tlist.append(t2)
        val_range = xinfo.range()
        if val_range:
            t3 = self.add_text(150, self.current_yoff + 16, "({0}-{1})".format(val_range[0], val_range[1]))
            tlist.append(t3)

        ht = self.calc_objects_height(tlist)
        self.current_yoff += ht + 5

    def calc_objects_height(self, lst):
        # calc all bounding rects
        map(lambda x: x.calc_brect(), lst)
        # find highest element y-coord
        y_min = min(lst, key=lambda x: x.y).y
        # find lowest element bottom y
        return max(map(lambda x: x.height + x.y - y_min, lst))

    def outlets_begin(self, outlets):
        super(self.__class__, self).outlets_begin(outlets)
        self.add_section(self.current_yoff, "outlets:")
        outlets.enumerate()

    def outlets_end(self, outlets):
        self.current_yoff += 10

    def outlet_begin(self, outlet):
        self.add_text(120, self.current_yoff, "{0}.".format(outlet.number()))
        self.add_text(230, self.current_yoff, outlet.text())
        self.current_yoff += 20

    def arguments_begin(self, args):
        super(self.__class__, self).arguments_begin(args)
        self.add_section(self.current_yoff, "arguments:")

    def argument_begin(self, arg):
        super(self.__class__, self).argument_begin(arg)
        self.add_text(200, self.current_yoff, arg.text())
        self.current_yoff += 20

    def object_end(self, obj):
        LNK_X = 10
        LNK_Y = 45
        # library link
        l1 = self.add_link(LNK_X, LNK_Y, "{0}::".format(self._library), "{0}-help.pd".format(self._library))
        brect = PdObject.brect_calc().text_brect(l1.text())
        LNK_X += brect[2] + 10
        # category link
        self.add_link(LNK_X, LNK_Y, "{0}".format(self._category), "{0}.{1}-help.pd".format(self._library, self._category))
        self.add_footer()

    def render(self):
        pd_exporter = PdExporter()
        self._cnv.traverse(pd_exporter)
        return pd_exporter.result

    def make_txt(self, x, y, txt):
        txt = re.sub(' +', ' ', txt)
        txt = txt.replace('.', '\\.')
        txt = txt.replace(',', ' \\,')
        return Comment(x, y, txt.split(' '))

    def add_text(self, x, y, txt):
        obj = self.make_txt(x, y, txt)
        self._cnv.append_object(obj)
        return obj

    def make_link(self, x, y, name, url):
        return PddpLink(x, y, url, name)

    def add_link(self, x, y, name, url):
        obj = self.make_link(x, y, name, url)
        self._cnv.append_object(obj)
        return obj

    def make_delimeter(self, y, **kwargs):
        delim = GCanvas(kwargs.get('x', 20), y, width=kwargs.get('width', 640), height=1, size=1)
        delim._bg_color = Color(200, 200, 200)
        return delim

    def add_delimiter(self, y, **kwargs):
        obj = self.make_delimeter(y)
        self._cnv.append_object(obj)
        return obj

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
        lbl = self.add_header_label()
        self.add_header_example_object(lbl, self._title)

    def add_header_example_object(self, lbl, title):
        example_obj = make_by_name(title)
        example_obj.calc_brect()
        # horizontal align right
        example_obj.x = lbl.width - example_obj.width - 20
        # vertical align
        example_obj.y = (lbl.height - example_obj.height) / 2
        self._cnv.append_object(example_obj)

    def add_header_label(self):
        lbl = GCanvas(1, 1, width=self.window_width() - 3, height=self.PD_HEADER_HEIGHT, size=10,
                      label="{0}".format(self._title), font_size=self.PD_HEADER_FONT_SIZE,
                      label_yoff=18, label_xoff=10)
        lbl._label_color = self.PD_HEADER_COLOR
        lbl._bg_color = self.PD_HEADER_BG_COLOR
        self._cnv.append_object(lbl)
        return lbl

    def add_footer(self):
        y = self.window_height() - self.PD_FOOTER_HEIGHT - 2
        self.add_footer_bg(y)
        self.add_footer_library(y)
        self.add_also(y)
        self.add_footer_more_info(y)

    def add_footer_more_info(self, y):
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
        add_subpatch_text(xc1, yrows[row], "version:")
        add_subpatch_text(xc2, yrows[row], self._version)
        row += 1
        add_subpatch_text(xc1, yrows[row], "object:")
        add_subpatch_text(xc2, yrows[row], self._title)
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
            add_subpatch_text(xc2, yrows[row], ", ".join(self._keywords))
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
        ypos = self.PD_INFO_WINDOW_HEIGHT - 22
        delim = self.make_delimeter(ypos, width=270, x=xc2)
        pd.append_object(delim)
        add_subpatch_text(xc2, ypos, "generated by pddoc")
        self._cnv.append_subpatch(pd)

    def add_footer_library(self, y):
        # library:
        self.add_text(10, y + 3, "library: {0} v{1}".format(self._library, self._version))

    def add_footer_bg(self, y):
        bg = GCanvas(1, y, width=self.window_width() - 3, height=self.PD_FOOTER_HEIGHT)
        bg._bg_color = self.PD_FOOTER_COLOR
        self._cnv.append_object(bg)

    def add_also(self, y):
        # see also:
        also_objects = []
        for see in self._see_also:
            obj = PdObject(see['name'], 0, y + 20)
            obj.calc_brect()
            also_objects.append(obj)

        # width list
        also_wd = map(lambda x: x.width, also_objects)
        # width with padding
        total_wd = sum(also_wd) + 14 * (len(also_wd) - 1)
        x_init_pos = self.window_width() - total_wd - 20
        x_pos = x_init_pos
        for obj in also_objects:
            obj.x = x_pos
            x_pos += obj.width + 14
            self._cnv.append_object(obj)
        self.add_text(x_init_pos - 70, y + 22, "see also:")
