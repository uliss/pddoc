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

import gettext

from pddoc.docobject import DocPar, DocA, DocWiki, DocArgument, DocArguments, DocProperties, DocOutlet, DocProperty, \
    DocMethod
from pddoc.pdpage import PdPage
from pddoc.pdpage import PdPageStyle
from .docobjectvisitor import DocObjectVisitor
from .pd.comment import Comment
from .pd.coregui import Color
from .pd.factory import make_by_name
from .pd.gcanvas import GCanvas
from .pd.message import Message
from .pd.obj import PdObject
from .pd.parser import Parser

gettext.install("pddoc")


def add_text_dot(txt) -> str:
    if txt is None:
        return ''
    txt = txt.strip()
    if len(txt) == 0:
        return txt

    if txt[-1] == '.':
        return txt
    else:
        return txt + '.'


def remove_text_dot(txt: str) -> str:
    txt = txt.strip()
    if len(txt) == 0:
        return txt

    if txt[-1] == '.':
        return txt[0:-1]
    else:
        return txt


def units_str(units) -> str:
    return ", ".join(map(lambda x: f"'{x}'", units))


class PdDocVisitor(DocObjectVisitor):
    current_yoff: int
    PD_WINDOW_WIDTH = 785
    PD_WINDOW_HEIGHT = 555
    PD_HEADER_HEIGHT = 40
    PD_HEADER_FONT_SIZE = 20
    PD_HEADER_COLOR = Color(0, 255, 255)
    PD_HEADER_BG_COLOR = Color(100, 100, 100)
    PD_FOOTER_HEIGHT = 48
    PD_FOOTER_COLOR = Color(180, 180, 180)
    PD_INFO_WINDOW_WIDTH = 400
    PD_INFO_WINDOW_HEIGHT = 290
    PD_XLET_INDX_XPOS = 110
    PD_XLET_TYPE_XPOS = 150
    PD_XLET_INFO_XPOS = 245
    PD_SECTION_YMARGIN = 40
    PD_PAR_INDENT = 10
    PD_ARG_NAME_COLOR = Color(240, 250, 250)

    def __init__(self):
        DocObjectVisitor.__init__(self)
        # object constants
        self.PD_EXAMPLE_X_OFFSET = 30
        self.DESCRIPTION_HEIGHT = 10

        self.current_yoff = 0
        self._pp = PdPage("obj", self.PD_WINDOW_WIDTH, self.PD_WINDOW_HEIGHT)

    def meta_end(self, meta):
        self.add_header()
        self.current_yoff += self.PD_HEADER_HEIGHT
        self.current_yoff += 30

    def abs_description_y_pos(self) -> int:
        return self.PD_HEADER_HEIGHT + 10

    def description_begin(self, d):
        super(self.__class__, self).description_begin(d)
        bbox = self._pp.add_description(self._description, self.abs_description_y_pos())
        self.DESCRIPTION_HEIGHT = bbox.height

    def pdascii_begin(self, t):
        cnv = super(self.__class__, self).pdascii_begin(t)
        # insert only first example
        if t.id() == 'main':
            self.copy_canvas_objects(cnv, self.PD_EXAMPLE_X_OFFSET, self.current_yoff)
            self.copy_canvas_connections(cnv)
            # update page y-offset
            self.current_yoff += cnv.height

    def copy_canvas_connections(self, cnv):
        for conn in cnv.connections.values():
            self._pp.canvas.add_connection(conn[0].id, conn[1], conn[2].id, conn[3])

    def copy_canvas_objects(self, cnv, xoff: int, yoff: int):
        for obj in cnv.objects:
            obj.x += xoff
            obj.y += yoff
            self._pp.append_object(obj)

    def pdinclude_begin(self, t):
        db_path = '{0}.db'.format(self._library)
        PdObject.xlet_calculator.add_db(db_path)

        pd_parser = Parser()
        pd_parser.parse(t.file())
        cnv = pd_parser.canvas
        self.copy_canvas_objects(cnv, self.PD_EXAMPLE_X_OFFSET, self.current_yoff)
        self.copy_canvas_connections(cnv)
        self.current_yoff += cnv.height

    def mouse_begin(self, m):
        self.add_section(_("mouse events:"), self.PD_SECTION_YMARGIN)
        m.sort_by(lambda e: e.edit_mode())

    def mouse_end(self, m):
        self.current_yoff += 10
        if m.is_empty():
            self.current_yoff += 10

    def event_begin(self, e):
        click_map = {
            'left-click': 'Left-click',
            'right-click': 'Right-click',
            'middle-click': 'Middle-click',
            'double-click': 'Double-click',
            'drag': 'Mouse-drag',
            'move': 'Mouse-move',
            'wheel': 'Mouse-wheel',
            'drop-file': 'Drop-file',
            'drop-text': 'Drop-text',
        }

        ct = e.type()
        k = e.keys()
        if k == "":
            tmpl = "{0}"
        else:
            tmpl = "{0} + {1}"

        items = []
        t1 = self._pp.add_txt(tmpl.format(click_map[ct], k), self.PD_XLET_INDX_XPOS, self.current_yoff)
        t2 = self._pp.add_txt(add_text_dot(e.text()), self.PD_XLET_INFO_XPOS + 40, self.current_yoff)

        items.append(t1)
        items.append(t2)

        __, __, __, h = self._pp.group_brect(items)

        if e.edit_mode():
            lbl = self._pp.add_txt(_("[Edit]"), 0, self.current_yoff)
            __, __, w, __ = self._pp.group_brect([lbl])
            lbl.x = (self.PD_XLET_INDX_XPOS - w - 10)

        self.current_yoff += h + 5

    def methods_begin(self, m):
        self.add_section(_("methods:"), self.PD_SECTION_YMARGIN)
        m.sort_by(lambda n: n.sort_name())

    def methods_end(self, m):
        self.current_yoff += 10
        if m.is_empty():
            self.current_yoff += 10

    def method_begin(self, m: DocMethod):
        msg_atoms = [m.name()]
        # for i in m.items():
        # msg_atoms.append(i.param_name())

        msg = Message(self.PD_XLET_INDX_XPOS, self.current_yoff, msg_atoms)
        msg.calc_brect()
        self._pp.append_object(msg)

        info_text = m.text().strip()
        info_text = add_text_dot(info_text)

        if len(m.items()) > 0:
            info_text += _(" Arguments are: ")

        x = self.PD_XLET_INFO_XPOS
        # fix x-offset for long method names
        if len(m.name()) > 18:
            x += (len(m.name()) - 18) * 10

        info = [self._pp.add_txt(info_text, x, self.current_yoff)]

        # add method arguments
        for i in m.items():
            param_name = i.param_name()
            arg_descr = param_name

            if i.text() is not None:
                arg_descr += ": " + i.text().strip()

            if i.type():
                arg_descr = _("{0} Type: {1}. ").format(add_text_dot(arg_descr), i.type())

            value_range = self.format_range(i)
            if len(value_range) > 0:
                # add dot after description
                arg_descr = add_text_dot(arg_descr)
                # add dot after the range
                arg_descr += " " + add_text_dot(value_range)

            if len(i.enum()) > 0:
                arg_descr = _("{0} Allowed values: {1}. ").format(add_text_dot(arg_descr), ', '.join(i.enum()))

            if i.units() and len(i.units()) > 0:
                arg_descr = _("{0} Units: {1}. ").format(add_text_dot(arg_descr), units_str(i.units()))

            # param name highlight with background canvas
            hl_text = self._pp.make_txt(param_name, 0, 0)
            hl_text.calc_brect()
            bg = self._pp.make_background(0, 0, hl_text.width + 8, hl_text.height + 8, color=self.PD_ARG_NAME_COLOR)
            self._pp.append_object(bg)

            # param description
            txt_obj = self._pp.add_txt(add_text_dot(arg_descr), self.PD_XLET_INFO_XPOS + 10, self.current_yoff)
            # bind background to object
            setattr(txt_obj, 'background_obj', bg)

            info.append(txt_obj)

        self._pp.place_in_col(info, self.current_yoff, 8)

        # set background positions
        for obj in info:
            if hasattr(obj, 'background_obj'):
                bg = getattr(obj, 'background_obj')
                bg.x = obj.x
                bg.y = obj.y

        info.append(msg)
        __, __, __, h = self._pp.group_brect(info)
        self.current_yoff += h + 10

    def inlets_begin(self, inlets):
        super(self.__class__, self).inlets_begin(inlets)
        self.add_section(_("inlets:"), 6)
        inlets.enumerate()

    def inlets_end(self, inlets):
        self.current_yoff += 10

        if inlets.is_empty():
            self.current_yoff += 10

    def inlet_begin(self, inlet):
        self._pp.add_txt("{0}.".format(inlet.number()), self.PD_XLET_INDX_XPOS, self.current_yoff)

    def xinfo_begin(self, xinfo):
        tlist = []
        if xinfo.on():
            t1 = self._pp.add_txt("*{0}*".format(xinfo.on()), self.PD_XLET_TYPE_XPOS, self.current_yoff)
            tlist.append(t1)

        txt = add_text_dot(xinfo.text())
        rng = self.format_range(xinfo)
        if rng != "":
            txt += " " + rng

        t2 = self._pp.add_txt(add_text_dot(txt), self.PD_XLET_INFO_XPOS, self.current_yoff)
        tlist.append(t2)

        __, __, __, h = self._pp.group_brect(tlist)
        self.current_yoff += h + 5

    def outlets_begin(self, outlets):
        super(self.__class__, self).outlets_begin(outlets)
        self.add_section(_("outlets:"), 6)
        outlets.enumerate()

    def outlets_end(self, outlets):
        self.current_yoff += 10

        if outlets.is_empty():
            self.current_yoff += 10

    def outlet_begin(self, outlet: DocOutlet):
        y = self.current_yoff
        t1 = self._pp.add_txt("{0}.".format(outlet.number()), self.PD_XLET_INDX_XPOS, y)
        t2 = self._pp.add_txt(add_text_dot(outlet.text()), self.PD_XLET_INFO_XPOS, y)

        __, __, __, h = self._pp.group_brect([t1, t2])
        self.current_yoff += h + 5

    def add_section_help(self, txt: str, url: str, y: int):
        a = self._pp.make_link(self.PD_WINDOW_WIDTH - 50, y, url, txt)
        a.set_bg_color(PdPageStyle.MAIN_BG_COLOR)
        self._pp.append_object(a)
        pass

    def arguments_begin(self, args: DocArguments):
        super(self.__class__, self).arguments_begin(args)
        lbl = self.add_section(_("arguments:"), self.PD_SECTION_YMARGIN)
        self.add_section_help("[?]", "ceammc.args-info.pd", lbl.top)
        args.enumerate()

    def arguments_end(self, args: DocArguments):
        self.current_yoff += 10
        if args.is_empty():
            self.current_yoff += 10

    def properties_begin(self, p: DocProperties):
        super(self.__class__, self).properties_begin(p)
        lbl = self.add_section(_("properties:"), self.PD_SECTION_YMARGIN)
        self.add_section_help("[?]", "ceammc.props-info.pd", lbl.top)
        # sort by names
        p.sort_by(lambda n: n.sort_name())

    def properties_end(self, p: DocProperties):
        self.current_yoff += 10
        if p.is_empty():
            self.current_yoff += 10

    def property_begin(self, m: DocProperty):
        props = list()

        # add message with property name
        prop_get_name = "{0}".format(m.name())
        if m.access() == "readonly":
            prop_get_name += '?'

        props.append(Message(self.PD_XLET_INDX_XPOS, self.current_yoff, [prop_get_name]))
        self._pp.append_list(props)

        # props description
        prop_descr = ""
        if not (m.is_alias() or m.is_flag()):
            if m.access() == "readwrite":
                if m.text().startswith("on/off"):
                    prop_descr += _("Turn ")
                else:
                    prop_descr += _("Get/Set ")
            elif m.access() == "initonly":
                prop_descr += _("(initonly) Get/Set ")
            else:
                prop_descr += _("(readonly) Get ")

        if m.is_alias():
            txt = m.text()
            prop_descr += txt[0].upper() + txt[1:]
        else:
            prop_descr += m.text()

        if m.type() and not (m.is_alias() or m.is_flag()):
            prop_descr = _("{0} Type: {1}. ").format(add_text_dot(prop_descr), m.type())

        if m.units() and len(m.units()) > 0:
            prop_descr = _("{0} Units: {1}. ").format(add_text_dot(prop_descr), units_str(m.units()))

        if m.default():
            prop_descr = _("{0} Default value: {1}. ").format(add_text_dot(prop_descr), m.default())

        if m.min() and m.max():
            prop_descr = _("{0} Range: {1}...{2}. ").format(add_text_dot(prop_descr), m.min(), m.max())
        elif m.min():
            prop_descr = _("{0} Min value: {1}. ").format(add_text_dot(prop_descr), m.min())
        elif m.max():
            prop_descr = _("{0} Max value: {1}. ").format(add_text_dot(prop_descr), m.max())

        if len(m.enum()) > 0:
            prop_descr = _("{0} Allowed values: {1}.").format(add_text_dot(prop_descr), ', '.join(m.enum()))

        info = list()
        info.append(self._pp.add_txt(add_text_dot(prop_descr), self.PD_XLET_INFO_XPOS, self.current_yoff))

        self._pp.place_in_col(info, self.current_yoff, 15)
        br = self._pp.group_brect(info + props)
        self.current_yoff += br[3] + 12

    def abs_info_y_pos(self) -> int:
        return self.abs_description_y_pos() + self.DESCRIPTION_HEIGHT + 10

    def info_background_width(self) -> int:
        return (self._pp.width - self.PD_XLET_INFO_XPOS) + 10

    def info_begin(self, info):
        lst = []
        XPOS = self.PD_XLET_INFO_XPOS - 30
        for p in info.items():
            if isinstance(p, DocPar):
                ind = p.indent * self.PD_PAR_INDENT
                t = self._pp.make_txt(p.text(), XPOS + ind, 0)
                lst.append(t)
            elif isinstance(p, DocA):
                a = self._pp.make_link(XPOS, 0, p.url, p.text())
                a.set_bg_color(PdPageStyle.MAIN_BG_COLOR)
                lst.append(a)
            elif isinstance(p, DocWiki):
                a = self._pp.make_link(XPOS, 0, p.url, p.text())
                a.set_bg_color(PdPageStyle.MAIN_BG_COLOR)
                lst.append(a)
                setattr(a, 'wiki_txt', True)

        brect = self._pp.place_in_col(lst, self.abs_info_y_pos(), 10)
        brect.width = self.info_background_width()
        brect.expand(10, 0, 5, 15)
        bg = self._pp.make_background(brect.x, brect.y, brect.width, brect.height,
                                      PdPageStyle.MAIN_BG_COLOR)
        self._pp.append_object(bg)

        # place "Wiki:" before wiki link
        for obj in lst:
            if hasattr(obj, 'wiki_txt'):
                # create "Wiki:" text
                wiki_txt = self._pp.make_txt("Wiki:", obj.x, obj.y)
                self._pp.append_object(wiki_txt)
                obj.x += wiki_txt.brect()[2] + 5
                obj.y += 2

        self._pp.append_list(lst)
        self.current_yoff = brect.bottom()

    def argument_begin(self, arg: DocArgument):
        y = self.current_yoff
        super(self.__class__, self).argument_begin(arg)

        t1 = self._pp.add_txt("{0}.".format(arg.number()), self.PD_XLET_INDX_XPOS, y)
        t2 = self._pp.add_txt(arg.type(), self.PD_XLET_TYPE_XPOS, y)
        self.add_background_for_txt(arg.main_info_prefix(),
                                    self.PD_XLET_INFO_XPOS,
                                    y,
                                    self.PD_ARG_NAME_COLOR)

        rng = self.format_range(arg)
        t3 = self._pp.add_txt("{0}. {1}".format(remove_text_dot(arg.main_info()), rng), self.PD_XLET_INFO_XPOS, y)
        __, __, __, h = self._pp.group_brect([t1, t2, t3])
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
                return _("Max value: {0}").format(r[1])
            if not r[1]:
                return _("Min value: {0}").format(r[0])

            return _("Range: {0}...{1}").format(r[0], r[1])
        else:
            return ""

    def add_section(self, txt: str, yoff: int) -> GCanvas:
        hr = self._pp.make_styled_hrule(self.current_yoff)
        self._pp.append_object(hr)
        lbl = self._pp.make_section_label(self.current_yoff + 5, txt, font_size=14)
        self.current_yoff += yoff
        self._pp.append_object(lbl)
        return lbl

    def add_header(self):
        lbl = self.add_header_label()
        self.add_header_example_object(lbl, self._title)

    def add_header_example_object(self, lbl: GCanvas, title: str):
        seq = []
        alias_objects = list(filter(lambda n: n["name"] != title and not n.get("deprecated", False), self._aliases))

        for a in alias_objects:
            if 'is_link' in a and a['is_link'] is True:
                seq.append(self._pp.make_header_alias_link(title, a['name']))
            else:
                seq.append(make_by_name(a['name']))

        # calc total aliases name length to prevent overflow
        total_alias_strlen = sum([len(a['name']) for a in alias_objects])

        # too many aliases - show them in subpatch
        if len(alias_objects) > 3 or total_alias_strlen > 32:
            pd = self._pp.make_subpatch('aliases', 0, 0, 250, 400)

            self._pp.place_in_col(seq, 40, 20)
            self._pp.move_to_x(seq, 30)

            for obj in seq:
                pd.append_object(obj)

            self._pp.canvas.append_subpatch(pd)

            # append main object name
            # UI object added as link
            if self._is_gui:
                mobj = self._pp.make_header_alias_link(title, title)
            else:
                mobj = make_by_name(title)

            __, __, w, h = self._pp.brect_obj(mobj)
            x = (lbl.width - w) - 20
            y = int(round((lbl.height - h) / 2))
            mobj.x = x
            mobj.y = y
            self._pp.append_object(mobj)

            __, __, w, __ = self._pp.brect_box("pd aliases")
            pd.x = (x - (w + 20))
            pd.y = y
        else:
            # append main object name
            # UI object added as link
            if self._is_gui:
                seq.append(self._pp.make_header_alias_link(title, title))
            else:
                seq.append(make_by_name(title))

            self._pp.place_in_row(seq, 0, 20)
            __, __, w, h = self._pp.group_brect(seq)
            y = (lbl.height - h) / 2
            x = (lbl.width - w) - 20
            self._pp.move_to_x(seq, x)
            self._pp.move_to_y(seq, y)
            self._pp.append_list(seq)

    def add_header_label(self):
        return self._pp.add_header("{0}".format(self._title))

    def add_footer(self):
        ft = self._pp.make_footer(self.current_yoff + 20, height=self.PD_FOOTER_HEIGHT)
        y = ft.y
        self._pp.append_object(ft)
        self.add_footer_library(y)
        self.add_also(y + 15)
        self.add_footer_more_info(y)

    def add_footer_more_info(self, y: int):
        # more info
        pd = self._pp.make_subpatch('info', 10, y + 22, self.PD_INFO_WINDOW_WIDTH, self.PD_INFO_WINDOW_HEIGHT)

        def add_subpatch_text(x, y0, txt):
            self._pp.add_subpatch_txt('info', txt, x, y0)

        bg = self._pp.make_background(1, 1, 107, self.PD_INFO_WINDOW_HEIGHT - 3, self.PD_FOOTER_COLOR)
        self._pp.add_subpatch_obj('info', bg)
        xc1 = 10
        xc2 = 120
        yrows = range(10, 300, 22)
        row = 0
        add_subpatch_text(xc1, yrows[row], _("library:"))
        add_subpatch_text(xc2, yrows[row], self._library)
        row += 1
        add_subpatch_text(xc1, yrows[row], _("version:"))
        add_subpatch_text(xc2, yrows[row], self._version)
        row += 1
        add_subpatch_text(xc1, yrows[row], _("object:"))
        add_subpatch_text(xc2, yrows[row], self._title)
        row += 1
        add_subpatch_text(xc1, yrows[row], _("category:"))
        add_subpatch_text(xc2, yrows[row], self._category)
        row += 1

        if self._since:
            add_subpatch_text(xc1, yrows[row], _("since:"))
            add_subpatch_text(xc2, yrows[row], self._since)
            row += 1

        add_subpatch_text(xc1, yrows[row], _("authors:"))
        add_subpatch_text(xc2, yrows[row], ", ".join(self._authors))
        row += 1
        add_subpatch_text(xc1, yrows[row], _("license:"))
        if not self._license.get('url', ' '):
            add_subpatch_text(xc2, yrows[row], self._license['name'])
        else:
            lnk = self._pp.make_link(xc2, yrows[row], self._license['url'], self._license['name'])
            pd.append_object(lnk)
        row += 1
        if self._keywords:
            add_subpatch_text(xc1, yrows[row], _("keywords:"))
            add_subpatch_text(xc2, yrows[row], ", ".join(self._keywords))
            row += 1
        if self._website:
            add_subpatch_text(xc1, yrows[row], "website:")
            lnk = self._pp.make_link(xc2, yrows[row], self._website, self._website)
            pd.append_object(lnk)
            row += 1
        if self._contacts:
            add_subpatch_text(xc1, yrows[row], _("contacts:"))
            add_subpatch_text(xc2, yrows[row], self._contacts)
            row += 1

        pd.append_object(PdObject("declare", x=xc2, y=yrows[row], args=["-lib", "ceammc"]))

        ypos = self.PD_INFO_WINDOW_HEIGHT - 22
        delim = self._pp.make_hrule(xc2, ypos, width=270)
        pd.append_object(delim)
        add_subpatch_text(xc2, ypos, _("generated by pddoc"))
        self._pp.canvas.append_subpatch(pd)

    def add_footer_library(self, y: int):
        # library:
        self._pp.add_txt(_("library: {0} v{1}").format(self._library, self._version), 10, y + 3)

    def add_background_for_txt(self, txt: str, x: int, y: int, color: Color, **kwargs):
        if len(txt) < 1:
            return

        padx: int = kwargs.get("padx", 5)
        pady: int = kwargs.get("pady", 5)

        c = Comment(x, y, txt.split(' '))
        c.calc_brect()
        bg = self._pp.make_background(x + 1, y + 1, c.width + padx, c.height + pady, color)
        self._pp.append_object(bg)

    def add_also(self, y: int):
        if len(self._see_also) < 1:
            return

        # see also:
        label = self._pp.make_txt(_("see also:"), 0, 0)
        also_objects = [label]
        for see in self._see_also:
            if 'is_link' in see and see['is_link'] == True:
                lnk = self._pp.make_link(0, 0,
                                         "{0}-help.pd".format(see['name']),
                                         "[{0}]".format(see['name']))
                lnk.set_bg_color(Color(200, 200, 200))
                also_objects.append(lnk)
            else:
                also_objects.append(make_by_name(see['name']))

        self._pp.place_in_row(also_objects, 0, 10)
        __, __, w, h = self._pp.group_brect(also_objects)
        self._pp.move_to_y(also_objects, y)
        self._pp.move_to_x(also_objects, (self._pp.width - w) - 40)
        self._pp.append_list(also_objects)
