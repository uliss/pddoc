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

import pddoc.pd as pd
from pdlayout import PdLayout
from idocobjectvisitor import IDocObjectVisitor


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
        self._inlet_counter = 0
        self._image_counter = 0
        self._image_prefix = ""
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

    def _pd_append_example(self, img_id, img_path, pd_path="", title=""):
        example_dict = {
            'id': img_id,
            'image': img_path,
            'title': title,
            'file': pd_path
        }

        self._examples.append(example_dict)

    def make_image_id_name(self):
        self._image_counter += 1
        cnt = self._image_counter
        path = "image_{0:02d}.png".format(self._image_counter)
        return cnt, path

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

    def pdconnect_begin(self, c):
        self._layout.connect_begin(c)

    def inlets_begin(self, inlets):
        self._inlets = inlets.inlet_dict()

    def outlets_begin(self, outlets):
        self._outlets = outlets.outlet_dict()

    def arguments_begin(self, args):
        self._arguments = args.items()