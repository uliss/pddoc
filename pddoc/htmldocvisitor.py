#!/usr/bin/env python
# coding=utf-8

# Copyright (C) 2014 by Serge Poltavski                                 #
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

import os
import pdcanvas
import pddrawer
import pdobject
import cairopainter
import pdparser
from layout import *
from brectcalculator import *
from pdcomment import *
from pdmessage import *
from pdobject import *
from mako.template import Template
from mako.lookup import TemplateLookup
from docobject import *


class HtmlDocVisitor(object):
    def __init__(self):
        self._title = ""
        self._description = ""
        self._keywords = []
        self._website = ""
        self._version = ""
        self._aliases = []
        self._examples = {}
        self._inlets = {}
        self._outlets = {}
        self._arguments = []
        self._inlet_counter = 0
        self._cur_canvas = None
        self._image_counter = 0
        self._cur_layout = []
        self._example_brect = ()
        self._pdobj_id_map = {}
        self._css_theme = "../theme.css"
        self._img_output_dir = "./out"
        self._comment_xoffset = 2
        self._hlayout_space = 20
        self._vlayout_space = 25
        # template config
        tmpl_path = "{0:s}/html_object.tmpl".format(os.path.dirname(__file__))
        # self._tmpl_lookup = TemplateLookup(directories=[os.path.dirname(__file__)])
        self._html_template = Template(filename=tmpl_path)
        self._brect_calc = BRectCalculator()
        self._canvas_padding = 10

    def title_begin(self, t):
        self._title = t.text()

    def website_begin(self, w):
        self._website = w.text()

    def keywords_begin(self, k):
        self._keywords = k.keywords()

    def description_begin(self, d):
        self._description = d.text()

    def aliases_begin(self, a):
        self._aliases += a.aliases()

    def version_begin(self, v):
        self._version = v.text()

    def pdexample_begin(self, pd):
        if pd.file():
            parser = pdparser.PdParser()
            parser.parse(pd.file())
            self._cur_canvas = parser.canvas
        else:
            self._cur_canvas = pdcanvas.PdCanvas(0, 0, 10, 10, name="10")
            self._cur_canvas.type = pdcanvas.PdCanvas.TYPE_WINDOW

    def pdexample_end(self, pd):
        w, h = self.draw_area_size(pd)
        if not pd.file():
            self.place_pd_objects()

        self._image_counter += 1
        fname = "image_{0:02d}.png".format(self._image_counter)
        output_fname = "./out/" + fname

        painter = cairopainter.CairoPainter(w, h, output_fname,
                                            xoffset=self._canvas_padding,
                                            yoffset=self._canvas_padding)
        walker = pddrawer.PdDrawer()
        walker.draw(self._cur_canvas, painter)

        self._examples[self._image_counter] = fname

    def row_begin(self, row):
        lh = Layout(Layout.HORIZONTAL, self._hlayout_space)
        self._cur_layout.append(lh)

    def row_end(self, row):
        lh = self._cur_layout.pop()
        # adds child layout to parent
        if self._cur_layout:
            self._cur_layout[-1].add_layout(lh)

        self._example_brect = lh.brect()

    def col_begin(self, col):
        lv = Layout(Layout.VERTICAL, self._vlayout_space)
        self._cur_layout.append(lv)

    def col_end(self, col):
        lv = self._cur_layout.pop()
        # adds child layout to parent
        if self._cur_layout:
            self._cur_layout[-1].add_layout(lv)

        self._example_brect = lv.brect()

    def pdmessage_begin(self, msg_obj):
        cnv = self._cur_canvas
        pd_msg = self.doc_msg2pd_msg(msg_obj)
        cnv.append_object(pd_msg)

        # handle object comment
        if msg_obj.comment:
            pd_comment = self.comment2pd_comment(msg_obj.comment)
            cnv.append_object(pd_comment)

            hor_layout = Layout.horizontal(self._comment_xoffset)
            hor_layout.add_item(pd_msg.layout)
            hor_layout.add_item(pd_comment.layout)
            self._cur_layout[-1].add_layout(hor_layout)
        else:
            self._cur_layout[-1].add_item(pd_msg.layout)

        self.add_id_mapping(msg_obj, pd_msg)

    def calc_brect(self, obj):
        if isinstance(obj, PdMessage):
            return self._brect_calc.message_brect(obj)
        elif isinstance(obj, PdObject):
            return self._brect_calc.object_brect(obj)
        elif isinstance(obj, PdComment):
            return self._brect_calc.comment_brect(obj)
        else:
            assert False

    def doc_msg2pd_msg(self, doc_msg):
        assert isinstance(doc_msg, DocPdmessage)
        pdm = PdMessage(0, 0, [doc_msg.text()])
        obj_bbox = list(self.calc_brect(pdm))
        litem = LayoutItem(doc_msg.offset(), 0, obj_bbox[2], obj_bbox[3])
        setattr(pdm, "layout", litem)
        return pdm

    def doc_obj2pd_obj(self, doc_obj):
        assert isinstance(doc_obj, DocPdobject)
        args = filter(None, doc_obj.args())
        pd_obj = pdobject.PdObject(doc_obj.name(), 0, 0, 0, 0, args)
        obj_bbox = list(self.calc_brect(pd_obj))
        litem = LayoutItem(doc_obj.offset(), 0, obj_bbox[2], obj_bbox[3])
        setattr(pd_obj, "layout", litem)
        return pd_obj

    def comment2pd_comment(self, txt):
        pd_comment = PdComment(0, 0, txt.split(" "))
        cbbox = self.calc_brect(pd_comment)
        comment_litem = LayoutItem(0, 0, cbbox[2], cbbox[3])
        setattr(pd_comment, "layout", comment_litem)
        return pd_comment

    def pdobject_begin(self, doc_obj):
        cnv = self._cur_canvas
        pd_obj = self.doc_obj2pd_obj(doc_obj)
        cnv.append_object(pd_obj)

        # handle object comment
        if doc_obj.comment:
            pd_comment = self.comment2pd_comment(doc_obj.comment)
            cnv.append_object(pd_comment)

            hor_layout = Layout.horizontal(self._comment_xoffset)
            hor_layout.add_item(pd_obj.layout)
            hor_layout.add_item(pd_comment.layout)
            self._cur_layout[-1].add_layout(hor_layout)
        else:
            self._cur_layout[-1].add_item(pd_obj.layout)

        self.add_id_mapping(doc_obj, pd_obj)

    def add_id_mapping(self, doc_obj, pd_obj):
        self._pdobj_id_map[doc_obj.id] = pd_obj.id

    def draw_area_size(self, pd):
        assert isinstance(pd, DocPdexample)
        w = 0
        h = 0

        if pd.file() and pd.size() == "canvas":
            w = self._cur_canvas.width
            h = self._cur_canvas.height
        elif pd.size() == "auto":
            w = self._example_brect[2]
            h = self._example_brect[3]
        elif not pd.size():
            w = pd.width()
            h = pd.height()

            if not w:
                w = self._example_brect[2]
            if not h:
                h = self._example_brect[3]
        else:
            w = self._example_brect[2]
            h = self._example_brect[3]

        return int(w + 2 * self._canvas_padding), int(h + 2 * self._canvas_padding)

    def place_pd_objects(self):
        for pdo in self._cur_canvas.objects:
            litem = getattr(pdo, "layout")
            pdo.x = litem.x()
            pdo.y = litem.y()

    def pdconnect_begin(self, c):
        src_id = self._pdobj_id_map[c.src_id()]
        dest_id = self._pdobj_id_map[c.dest_id()]
        src_out = c._src_out
        dest_in = c._dest_in

        self._cur_canvas.add_connection(src_id, src_out, dest_id, dest_in)

    def inlets_begin(self, inlets):
        self._inlets = inlets.inlet_dict()

    def outlets_begin(self, outlets):
        self._outlets = outlets.outlet_dict()

    def arguments_begin(self, args):
        self._arguments = args.items()

    def generate_object_image(self, name):
        fname = "out/object_{0:s}.png".format(name)
        if os.path.exists(fname):
            return

        pdo = PdObject(name)
        brect = BRectCalculator().object_brect(pdo)
        pad = 1  # pixel
        painter = cairopainter.CairoPainter(int(brect[2]) + pad, int(brect[3]) + pad, fname, "png")
        painter.draw_object(pdo)

    def generate_images(self):
        if self._aliases:
            for a in [self._title] + self._aliases:
                self.generate_object_image(a)

    def render(self):
        return self._html_template.render(
            title=self._title,
            description=self._description,
            keywords=self._keywords,
            image_dir='.',
            css_theme=self._css_theme,
            aliases=[self._title] + self._aliases,
            version=self._version,
            examples=self._examples,
            inlets=self._inlets,
            outlets=self._outlets,
            arguments=self._arguments)