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
from pdlayout import *
import pdfactory


class HtmlDocVisitor(object):
    def __init__(self):
        self._title = ""
        self._description = ""
        self._keywords = []
        self._website = ""
        self._library = ""
        self._category = ""
        self._version = ""
        self._license = {}
        self._aliases = []
        self._see_also = []
        self._examples = []
        self._authors = []
        self._contacts = ""
        self._inlets = {}
        self._outlets = {}
        self._arguments = []
        self._inlet_counter = 0
        self._image_counter = 0
        self._css_theme = "../theme.css"
        self._img_output_dir = "./out"
        # template config
        tmpl_path = "{0:s}/html_object.tmpl".format(os.path.dirname(__file__))
        # self._tmpl_lookup = TemplateLookup(directories=[os.path.dirname(__file__)])
        self._html_template = Template(filename=tmpl_path)
        self._layout = PdLayout()
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

    def license_begin(self, l):
        self._license['url'] = l.url()
        self._license['name'] = l.name()

    def library_begin(self, lib):
        self._library = lib.text()

    def category_begin(self, cat):
        self._category = cat.text()

    def version_begin(self, v):
        self._version = v.text()

    def author_begin(self, author):
        self._authors.append(author.text())

    def contacts_begin(self, cnt):
        self._contacts = cnt.text()

    def see_begin(self, see):
        dict = {'name' : see.text()}
        dict['image'] = "object_{0:s}.png".format(see.text())
        dict['link'] = "{0:s}.html".format(see.text())
        self._see_also.append(dict)

    def make_image_id_name(self):
        self._image_counter += 1
        return self._image_counter, "image_{0:02d}.png".format(self._image_counter)

    def pdexample_begin(self, pd):
        if pd.file():
            parser = pdparser.PdParser()
            parser.parse(pd.file())
            self._layout.canvas = parser.canvas
        else:
            self._layout.canvas = pdcanvas.PdCanvas(0, 0, 10, 10, name="10")
            self._layout.canvas.type = pdcanvas.PdCanvas.TYPE_WINDOW

    def pdexample_end(self, pd):
        w, h = self.draw_area_size(pd)
        img_id, img_fname = self.make_image_id_name()

        example_dict = {'id' : img_id, 'image' : img_fname, 'title' : pd.title(), 'file' : pd.file() }

        if not pd.file():
            self._layout.update()

        self._examples.append(example_dict)

        output_fname = "./out/" + img_fname
        painter = cairopainter.CairoPainter(w, h, output_fname,
                                            xoffset=self._canvas_padding,
                                            yoffset=self._canvas_padding)
        walker = pddrawer.PdDrawer()
        walker.draw(self._layout.canvas, painter)

    def pdcomment_begin(self, comment):
        self._layout.comment(comment)

    def row_begin(self, row):
        self._layout.row_begin()

    def row_end(self, row):
        self._layout.row_end()

    def col_begin(self, col):
        self._layout.col_begin()

    def col_end(self, col):
        self._layout.col_end()

    def pdmessage_begin(self, msg_obj):
        self._layout.message_begin(msg_obj)

    def pdobject_begin(self, doc_obj):
        self._layout.object_begin(doc_obj)

    def draw_area_size(self, pd):
        assert isinstance(pd, DocPdexample)
        w = 0
        h = 0

        if pd.file() and pd.size() == "canvas":
            w, h = self._layout.canvas_brect()[2:]
        elif pd.size() == "auto":
            w, h = self._layout.layout_brect()[2:]
        elif not pd.size():
            w = pd.width()
            h = pd.height()

            if not w:
                w = self._layout.layout_brect()[2]
            if not h:
                h = self._layout.layout_brect()[3]
        else:
            w, h = self._layout.layout_brect()[2:]

        return int(w + 2 * self._canvas_padding), int(h + 2 * self._canvas_padding)

    def pdconnect_begin(self, c):
        self._layout.connect_begin(c)

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

        pdo = pdfactory.make_by_name(name)
        brect = BRectCalculator().object_brect(pdo)
        pad = 1  # pixel
        painter = cairopainter.CairoPainter(int(brect[2]) + pad, int(brect[3]) + pad, fname, "png")
        pdo.draw(painter)

    def generate_images(self):
        if self._aliases:
            for a in [self._title] + self._aliases:
                self.generate_object_image(a)

        if self._see_also:
            for sa in self._see_also:
                self.generate_object_image(sa['name'])

    def render(self):
        return self._html_template.render(
            title=self._title,
            description=self._description,
            keywords=self._keywords,
            image_dir='.',
            css_theme=self._css_theme,
            aliases=[self._title] + self._aliases,
            license=self._license,
            version=self._version,
            examples=self._examples,
            inlets=self._inlets,
            outlets=self._outlets,
            arguments=self._arguments,
            see_also=self._see_also,
            website=self._website,
            authors=self._authors,
            contacts=self._contacts,
            library=self._library,
            category=self._category)