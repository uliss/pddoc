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
from pd.coregui import Color
from pd.comment import Comment
from pd.factory import make_by_name
from pddoc.pdpage import PdPage
from pd.message import Message
from pd.obj import PdObject
from pd.parser import Parser
from pddoc.docobject import DocPar
import os


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
    PD_XLET_INDX_XPOS = 125
    PD_XLET_TYPE_XPOS = 150
    PD_XLET_INFO_XPOS = 230
    PD_ARG_NAME_COLOR = Color(230, 240, 240)

    def __init__(self):
        DocObjectVisitor.__init__(self)
        self.current_yoff = 0
        self._pp = PdPage("obj", self.PD_WINDOW_WIDTH, self.PD_WINDOW_HEIGHT)

    def meta_end(self, meta):
        self.add_header()
        self.current_yoff += self.PD_HEADER_HEIGHT
        self.current_yoff += 30

    def description_begin(self, d):
        super(self.__class__, self).description_begin(d)
        self._pp.add_description(self._description, self.PD_HEADER_HEIGHT + 10)

    def pdascii_begin(self, t):
        cnv = super(self.__class__, self).pdascii_begin(t)
        self.copy_canvas_objects(cnv)
        self.copy_canvas_connections(cnv)

        self.current_yoff += cnv.height
        self.current_yoff += self.PD_EXAMPLE_YOFFSET

    def copy_canvas_connections(self, cnv):
        for conn in cnv.connections.values():
            self._pp.canvas.add_connection(conn[0].id, conn[1], conn[2].id, conn[3])

    def copy_canvas_objects(self, cnv):
        for obj in cnv.objects:
            obj.y += self.current_yoff
            obj.x += self.PD_EXAMPLE_YOFFSET
            self._pp.append_object(obj)

    def pdinclude_begin(self, t):
        db_path = '{0}.db'.format(self._library)
        PdObject.xlet_calculator.add_db(db_path)

        pd_parser = Parser()
        pd_parser.parse(t.file())
        cnv = pd_parser.canvas
        self.copy_canvas_objects(cnv)
        self.copy_canvas_connections(cnv)
        self.current_yoff += cnv.height

    def methods_begin(self, m):
        self.add_section("methods:")

    def methods_end(self, m):
        self.current_yoff += 10

    def method_begin(self, m):
        msg_atoms = [m.name()]
        for i in m.items():
            msg_atoms.append(i.param_name())

        msg = Message(self.PD_XLET_INDX_XPOS, self.current_yoff, msg_atoms)
        msg.calc_brect()
        self._pp.append_object(msg)

        info = []
        for i in m.items():
            rng = self.format_range(i)
            txt = self._pp.add_txt("{1}. {0}".format(rng, i.text().strip()),
                                   self.PD_XLET_INFO_XPOS, self.current_yoff)
            info.append(txt)

        if len(info) < 1:
            info.append(self._pp.add_txt(m.text(), self.PD_XLET_INFO_XPOS, self.current_yoff))

        self._pp.place_in_col(info, self.current_yoff, 15)
        info.append(msg)
        br = self._pp.group_brect(info)
        self.current_yoff += br[3] + 10

    def inlets_begin(self, inlets):
        super(self.__class__, self).inlets_begin(inlets)
        self.add_section("inlets:")
        inlets.enumerate()

    def inlets_end(self, inlets):
        self.current_yoff += 10

    def inlet_begin(self, inlet):
        self._pp.add_txt("{0}.".format(inlet.number()), self.PD_XLET_INDX_XPOS, self.current_yoff)

    def xinfo_begin(self, xinfo):
        tlist = []
        if xinfo.on():
            t1 = self._pp.add_txt("*{0}*".format(xinfo.on()), self.PD_XLET_TYPE_XPOS, self.current_yoff)
            tlist.append(t1)

        rng = self.format_range(xinfo)
        t2 = self._pp.add_txt("{0}. {1}".format(xinfo.text(), rng), self.PD_XLET_INFO_XPOS, self.current_yoff)
        tlist.append(t2)

        _, _, _, h = self._pp.group_brect(tlist)
        self.current_yoff += h + 5

    def outlets_begin(self, outlets):
        super(self.__class__, self).outlets_begin(outlets)
        self.add_section("outlets:")
        outlets.enumerate()

    def outlets_end(self, outlets):
        self.current_yoff += 10

    def outlet_begin(self, outlet):
        y = self.current_yoff
        t1 = self._pp.add_txt("{0}.".format(outlet.number()), self.PD_XLET_INDX_XPOS, y)
        t2 = self._pp.add_txt(outlet.text(), self.PD_XLET_INFO_XPOS, y)

        _, _, _, h = self._pp.group_brect([t1, t2])
        self.current_yoff += h + 5

    def arguments_begin(self, args):
        super(self.__class__, self).arguments_begin(args)
        self.add_section("arguments:")
        args.enumerate()

    def arguments_end(self, outlets):
        self.current_yoff += 10

    def info_begin(self, info):
        lst = []
        for p in info.items():
            if isinstance(p, DocPar):
                t = self._pp.make_txt(p.text(), self.PD_XLET_INFO_XPOS, 0)
                lst.append(t)

        self._pp.place_in_col(lst, self.PD_HEADER_HEIGHT + 40, 10)
        brect = self._pp.group_brect(lst)
        bg = self._pp.make_background(brect[0] - 5, brect[1],
                                      self._pp.width - self.PD_XLET_INFO_XPOS - 15,
                                      brect[3] + 20, Color(250, 250, 250))
        self._pp.append_object(bg)
        self._pp.append_list(lst)
        self.current_yoff = brect[1] + brect[3]

    def argument_begin(self, arg):
        y = self.current_yoff
        super(self.__class__, self).argument_begin(arg)

        t1 = self._pp.add_txt("{0}.".format(arg.number()), self.PD_XLET_INDX_XPOS, y)
        t2 = self._pp.add_txt(arg.type(), self.PD_XLET_TYPE_XPOS, y)
        self.add_background_for_txt(arg.main_info_prefix(),
                                    self.PD_XLET_INFO_XPOS,
                                    y,
                                    self.PD_ARG_NAME_COLOR)

        rng = self.format_range(arg)
        t3 = self._pp.add_txt("{0}. {1}".format(arg.main_info(), rng), self.PD_XLET_INFO_XPOS, y)
        _, _, _, h = self._pp.group_brect([t1, t2, t3])
        self.current_yoff += h + 5

    def object_end(self, obj):
        LNK_Y = 45
        # index link
        idx_lnk = self._pp.make_link(0, LNK_Y, "../index-help.pd", "index")
        del1 = self._pp.make_txt("::", 0, LNK_Y)
        # library link
        lib_lnk = self._pp.make_link(0, LNK_Y,
                                     "{0}-help.pd".format(self._library),
                                     "{0}".format(self._library))
        del2 = self._pp.make_txt("::", 0, LNK_Y)
        # category link
        cat_lnk = self._pp.make_link(0, LNK_Y,
                                     "{0}.{1}-help.pd".format(self._library, self._category),
                                     "{0}".format(self._category))
        menu = [idx_lnk, del1, lib_lnk, del2, cat_lnk]
        self._pp.place_in_row(menu, 10, 7)
        self._pp.append_list(menu)
        self.add_footer()

    def render(self):
        return self._pp.to_string()

    @classmethod
    def format_range(cls, obj):
        r = obj.range()
        if len(r) == 2:
            if not r[0]:
                return "Max: {0}".format(r[1])
            if not r[1]:
                return "Min: {0}".format(r[0])

            return "Range: {0}...{1}".format(r[0], r[1])
        else:
            return ""

    def add_section(self, txt):
        hr = self._pp.make_styled_hrule(self.current_yoff)
        self._pp.append_object(hr)
        lbl = self._pp.make_section_label(self.current_yoff + 5, txt, font_size=14)
        self.current_yoff += 10
        self._pp.append_object(lbl)

    def add_header(self):
        lbl = self.add_header_label()
        self.add_header_example_object(lbl, self._title)

    def add_header_example_object(self, lbl, title):
        example_obj = make_by_name(title)
        example_obj.calc_brect()
        y = (lbl.height - example_obj.height) / 2
        self._pp.place_top_right(example_obj, 20, y)
        self._pp.append_object(example_obj)

    def add_header_label(self):
        return self._pp.add_header("{0}".format(self._title))

    def add_footer(self):
        ft = self._pp.make_footer(self.current_yoff + 20, height=self.PD_FOOTER_HEIGHT)
        y = ft.y
        self._pp.append_object(ft)
        self.add_footer_library(y)
        self.add_also(y + 15)
        self.add_footer_more_info(y)

    def add_footer_more_info(self, y):
        # more info
        pd = self._pp.make_subpatch('info', 10, y + 22, self.PD_INFO_WINDOW_WIDTH, self.PD_INFO_WINDOW_HEIGHT)

        def add_subpatch_text(x, y, txt):
            self._pp.add_subpatch_txt('info', txt, x, y)

        bg = self._pp.make_background(1, 1, 107, self.PD_INFO_WINDOW_HEIGHT - 3, self.PD_FOOTER_COLOR)
        self._pp.add_subpatch_obj('info', bg)
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

        if self._since:
            add_subpatch_text(xc1, yrows[row], "since:")
            add_subpatch_text(xc2, yrows[row], self._since)
            row += 1

        add_subpatch_text(xc1, yrows[row], "authors:")
        add_subpatch_text(xc2, yrows[row], ", ".join(self._authors))
        row += 1
        add_subpatch_text(xc1, yrows[row], "license:")
        if not self._license.get('url', ' '):
            add_subpatch_text(xc2, yrows[row], self._license['name'])
        else:
            lnk = self._pp.make_link(xc2, yrows[row], self._license['url'], self._license['name'])
            pd.append_object(lnk)
        row += 1
        if self._keywords:
            add_subpatch_text(xc1, yrows[row], "keywords:")
            add_subpatch_text(xc2, yrows[row], ", ".join(self._keywords))
            row += 1
        if self._website:
            add_subpatch_text(xc1, yrows[row], "website:")
            lnk = self._pp.make_link(xc2, yrows[row], self._website, self._website)
            pd.append_object(lnk)
            row += 1
        if self._contacts:
            add_subpatch_text(xc1, yrows[row], "contacts:")
            add_subpatch_text(xc2, yrows[row], self._contacts)
            row += 1

        ypos = self.PD_INFO_WINDOW_HEIGHT - 22
        delim = self._pp.make_hrule(xc2, ypos, width=270)
        pd.append_object(delim)
        add_subpatch_text(xc2, ypos, "generated by pddoc")
        self._pp.canvas.append_subpatch(pd)

    def add_footer_library(self, y):
        # library:
        self._pp.add_txt("library: {0} v{1}".format(self._library, self._version), 10, y + 3)

    def add_background_for_txt(self, txt, x, y, color, **kwargs):
        if len(txt) < 1:
            return

        padx = kwargs.get("padx", 5)
        pady = kwargs.get("pady", 5)

        c = Comment(x, y, txt.split(' '))
        c.calc_brect()
        bg = self._pp.make_background(x + 1, y + 1, c.width + padx, c.height + pady, color)
        self._pp.append_object(bg)

    def add_also(self, y):
        if len(self._see_also) < 1:
            return

        # see also:
        label = self._pp.make_txt("see also:", 0, 0)
        also_objects = [label]
        for see in self._see_also:
            also_objects.append(make_by_name(see['name']))

        self._pp.place_in_row(also_objects, 0, 10)
        _, _, w, h = self._pp.group_brect(also_objects)
        self._pp.move_to_y(also_objects, y)
        self._pp.move_to_x(also_objects, self._pp.width - w - 10)
        self._pp.append_list(also_objects)
