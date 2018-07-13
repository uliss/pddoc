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
from .pdlayout import PdLayout
from .idocobjectvisitor import IDocObjectVisitor
from .txt.parser import Parser
from .pd.canvas import Canvas
from .pd.pdexporter import PdExporter
from .pd.obj import PdObject


class DocObjectVisitor(IDocObjectVisitor):
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
        self._props = []
        self._inlet_counter = 0
        self._image_counter = 0
        self._image_prefix = ""
        self._image_extension = ""
        self._image_output_dir = ""
        self._search_dir = ""
        self._layout = PdLayout()
        self._canvas_padding = 10
        self._image_object_padding = 4
        self._pdascii = ""
        self._inlet_idx = 0
        self._outlet_idx = 0
        self._since = ""
        self._is_gui = False

    def object_begin(self, obj):
        self._is_gui = obj.is_gui()

    def alias_begin(self, a):
        element = {
            'name': a.text(),
            'image': self.image_pdobject_fname(a.text()),
            'is_link': a.is_link()
        }

        self._aliases.append(element)

    def add_alias(self, alias):
        element = {
            'name': alias,
            'image': self.image_pdobject_fname(alias),
            'is_link': False
        }
        self._aliases.append(element)

    def title_begin(self, t):
        self._title = t.text()

    def website_begin(self, w):
        self._website = w.text()

    def keywords_begin(self, k):
        self._keywords = k.keywords()

    def description_begin(self, d):
        self._description = d.text()

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

    def pdexample_begin(self, tag):
        self._layout.canvas = pd.Canvas(0, 0, 10, 10, name="10")
        self._layout.canvas.type = pd.Canvas.TYPE_WINDOW

    def pdexample_end(self, tag):
        img_id, img_path = self.make_image_id_name()
        # append data to template renderer
        self._pd_append_example(img_id, img_path, None, tag.title())
        # update layout - place all objects
        self._layout.update()
        # draw image
        w, h = self._pd_layout_size(tag)
        self._pd_draw(w, h, img_path)

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

    def row_begin(self, row):
        self._layout.row_begin()

    def row_end(self, row):
        self._layout.row_end()

    def col_begin(self, col):
        self._layout.col_begin()

    def col_end(self, col):
        self._layout.col_end()

    def pdascii_begin(self, pdascii):
        self._pdascii = pdascii.text()

        p = Parser()
        p.X_PAD = pdascii.x_pad()
        p.Y_PAD = pdascii.y_pad()
        p.X_SPACE *= pdascii.x_space()
        p.Y_SPACE *= pdascii.y_space()
        if not p.parse(self._pdascii):
            logging.info("<pdascii> parse failed: {0}".format(self._pdascii))

        cnv = Canvas(0, 0, 300, 500)
        cnv.type = Canvas.TYPE_WINDOW
        p.export(cnv)

        # save as pd
        br_calc = cnv.brect_calc()
        cnv.traverse(br_calc)
        bbox = br_calc.brect()
        wd = bbox[2] + Parser.X_PAD * 2
        ht = bbox[3] + Parser.Y_PAD * 2
        cnv.height = ht
        cnv.width = wd
        pd_exporter = PdExporter()
        cnv.traverse(pd_exporter)

        pd_name_template = "{0}-example.pd".format(self.name)
        pd_exporter.save(pd_name_template)

        return cnv

    def pdmessage_begin(self, msg_obj):
        self._layout.message_begin(msg_obj)

    def pdobject_begin(self, doc_obj):
        self._layout.object_begin(doc_obj)

    def pdconnect_begin(self, c):
        self._layout.connect_begin(c)

    def arguments_begin(self, args):
        self._arguments = args.items()

    def properties_begin(self, props):
        self._props = props.items()

    def since_begin(self, s):
        self._since = s.text()

    def see_begin(self, see):
        element = {
            'name': see.text(),
            'image': self.image_pdobject_fname(see.text()),
            'is_link': see.is_link()
        }

        self._see_also.append(element)

    def set_image_prefix(self, prefix):
        self._image_prefix = re.sub('[^a-zA-Z0-9~]', '', prefix)

    def image_prefix(self):
        if self._image_prefix:
            return self._image_prefix + "_"
        else:
            return ""

    def image_output_dir(self):
        return self._image_output_dir

    def set_image_output_dir(self, path):
        self._image_output_dir = path

    def search_dir(self):
        return self._search_dir

    def set_search_dir(self, path):
        self._search_dir = path

    def image_pdobject_fname(self, name):
        return os.path.join(self._image_output_dir,
                            "object_{0:s}.{1:s}".format(name, self._image_extension))

    def create_image_output_dir(self):
        try:
            if not os.path.exists(self._image_output_dir):
                os.makedirs(self._image_output_dir)

            if not os.path.isdir(self._image_output_dir):
                raise RuntimeError("not a directory: %s".format(self._image_output_dir))
        except Exception as e:
            raise RuntimeError(e.message)

    def make_image_id_name(self):
        self._image_counter += 1
        cnt = self._image_counter
        path = os.path.join(self._image_output_dir,
                            "{1:s}image_{0:02d}.{2:s}".format(self._image_counter,
                                                              self.image_prefix(),
                                                              self._image_extension))
        return cnt, path

    def make_image_painter(self, w, h, fname):
        return None

    def _pd_draw(self, w, h, fname):
        self.create_image_output_dir()

        painter = self.make_image_painter(w, h, fname)
        self._layout.canvas.draw(painter)
        logging.info("image [{0:d}x{1:d}] saved to: \"{2:s}\"".format(w, h, fname))

    def _pd_layout_size(self, tag):
        w = tag.width()
        h = tag.height()
        if not w:
            w = self._layout.layout_brect()[2]
        if not h:
            h = self._layout.layout_brect()[3]

        return int(w + 2 * self._canvas_padding), int(h + 2 * self._canvas_padding)

    def _pd_append_example(self, img_id, img_path, pd_path="", title=""):
        example_dict = {
            'id': img_id,
            'image': img_path,
            'title': title,
            'file': pd_path
        }

        self._examples.append(example_dict)

    def generate_object_image(self, name):
        fname = self.image_pdobject_fname(name)
        if os.path.exists(fname):
            logging.warning("image exists: \"%s\"", fname)

        pdo = pd.make_by_name(name)
        x, y, w, h = pd.BRectCalculator().object_brect(pdo)
        w = int(w + self._image_object_padding * 2)
        h = int(h + self._image_object_padding * 2)
        old_pad = self._canvas_padding
        self._canvas_padding = self._image_object_padding
        painter = self.make_image_painter(w, h, fname)
        self._canvas_padding = old_pad
        pdo.draw(painter)

    def generate_images(self):
        try:
            self.create_image_output_dir()

            if self._aliases:
                for a in self._aliases:
                    self.generate_object_image(a['name'])

            if self._see_also:
                for sa in self._see_also:
                    self.generate_object_image(sa['name'])
        except Exception as e:
            logging.error("Error while generating images: %s", e)
