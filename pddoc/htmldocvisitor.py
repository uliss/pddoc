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

import pdcanvas
import pddrawer
import pdobject
import pdmessage
import cairopainter
import pdparser
from layout import *
from brectcalculator import *
from pdcomment import *
import os
from pdobject import *
from mako.template import Template
from mako.lookup import TemplateLookup


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
        self._include = None
        self._css_theme = "../theme.css"
        self._img_output_dir = "./out"
        self._comment_xoffset = 2
        self._hlayout_space = 20
        self._vlayout_space = 25
        # template config
        tmpl_path = "{0:s}/html_object.tmpl".format(os.path.dirname(__file__))
        # self._tmpl_lookup = TemplateLookup(directories=[os.path.dirname(__file__)])
        self._html_template = Template(filename=tmpl_path)

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
        self._cur_canvas = pdcanvas.PdCanvas(0, 0, pd.width(), pd.height(), name="10")
        self._cur_canvas.type = pdcanvas.PdCanvas.TYPE_WINDOW

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

    def pdmessage_begin(self, obj):
        cnv = self._cur_canvas
        pdm = pdmessage.PdMessage(10, 10, [obj._msg])

        litem = LayoutItem(obj.offset(), 0, 50, 20)
        self._cur_layout[-1].add_item(litem)
        setattr(pdm, "layout", litem)
        cnv.append_object(pdm)
        self._pdobj_id_map[obj._id] = pdm._id

    def pdobject_begin(self, doc_obj):
        cnv = self._cur_canvas
        args = filter(None, doc_obj._args.split(" "))

        pd_obj = pdobject.PdObject(doc_obj.name(), 10, 10, -1, -1, args)
        pd_obj._id = doc_obj._id

        bc = BRectCalculator()
        obj_bbox = list(bc.object_brect(pd_obj))

        litem = LayoutItem(0, 0, obj_bbox[2], obj_bbox[3])
        cnv.append_object(pd_obj)

        # handle object comment
        if doc_obj.comment:
            # print doc_obj.comment
            cbbox = bc.comment_brect(doc_obj.comment)
            obj_bbox[2] += cbbox[2]
            comment_litem = LayoutItem(0, 0, cbbox[2], cbbox[3])

            pd_comment = PdComment(0, 0, doc_obj.comment.split(" "))
            setattr(pd_comment, "layout", comment_litem)
            cnv.append_object(pd_comment)

            hor_layout = Layout.horizontal(self._comment_xoffset)
            hor_layout.add_item(litem)
            hor_layout.add_item(comment_litem)
            self._cur_layout[-1].add_layout(hor_layout)
        else:
            self._cur_layout[-1].add_item(litem)

        setattr(pd_obj, "layout", litem)
        self.add_id_mapping(doc_obj, pd_obj)

    def add_id_mapping(self, doc_obj, pd_obj):
        self._pdobj_id_map[doc_obj._id] = pd_obj._id

    def pdobject_end(self, obj):
        pass

    def pdinclude_begin(self, inc):
        fname = inc._file
        parser = pdparser.PdParser()
        parser.parse(fname)

        self._cur_canvas = parser.canvas
        self._include = True

    def pdexample_end(self, pd):
        if self._include:
            if pd.width():
                img_width = pd.width()
            else:
                img_width = self._cur_canvas.height

            if pd.height():
                img_height = pd.height()
            else:
                img_height = self._cur_canvas.width
        else:
            for pdo in self._cur_canvas.objects:
                litem = getattr(pdo, "layout")
                pdo.x = litem.x()
                pdo.y = litem.y()

            img_width = int(self._example_brect[2])
            img_height = int(self._example_brect[3])

        self._image_counter += 1
        fname = "image_{0:02d}.png".format(self._image_counter)
        output_fname = "./out/" + fname

        pad = 10
        painter = cairopainter.CairoPainter(img_width + 2 * pad, img_height + 2 * pad,
                                            output_fname, xoffset=pad, yoffset=pad)
        walker = pddrawer.PdDrawer()
        walker.draw(self._cur_canvas, painter)

        self._examples[self._image_counter] = fname
        self._include = False

    def pdconnect_begin(self, c):
        src_id = self._pdobj_id_map[c._src_id]
        dest_id = self._pdobj_id_map[c._dest_id]
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