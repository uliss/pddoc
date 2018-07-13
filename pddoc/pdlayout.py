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

from .pd import *
from .layout import *
from .docobject import DocPdobject, DocPdmessage
import logging


class PdLayout(object):
    def __init__(self):
        self._canvas = None
        self._cur_layout = []
        self._example_brect = ()
        self._pdobj_id_map = {}
        self._brect_calc = BRectCalculator()
        self._comment_xoffset = 2
        self._hlayout_space = 20
        self._vlayout_space = 25

    def canvas_brect(self):
        return 0, 0, self._canvas.width, self._canvas.height

    def layout_brect(self):
        return self._example_brect

    @property
    def canvas(self):
        return self._canvas

    @canvas.setter
    def canvas(self, cnv):
        assert isinstance(cnv, Canvas)
        self._canvas = cnv

    def update(self):
        for pdo in self._canvas.objects:
            if not hasattr(pdo, "layout"):
                continue

            litem = getattr(pdo, "layout")
            pdo.x = litem.x()
            pdo.y = litem.y()

    def calc_brect(self, obj):
        if isinstance(obj, Message):
            return self._brect_calc.message_brect(obj)
        elif isinstance(obj, PdObject):
            return self._brect_calc.object_brect(obj)
        elif isinstance(obj, Comment):
            return self._brect_calc.comment_brect(obj)
        else:
            assert False

    def row_begin(self):
        lh = Layout(Layout.HORIZONTAL, self._hlayout_space)
        self._cur_layout.append(lh)

    def row_end(self):
        lh = self._cur_layout.pop()
        # adds child layout to parent
        if self._cur_layout:
            self._cur_layout[-1].add_layout(lh)

        self._example_brect = lh.brect()

    def col_begin(self):
        lv = Layout(Layout.VERTICAL, self._vlayout_space)
        self._cur_layout.append(lv)

    def col_end(self):
        lv = self._cur_layout.pop()
        # adds child layout to parent
        if self._cur_layout:
            self._cur_layout[-1].add_layout(lv)

        self._example_brect = lv.brect()

    def comment2pd_comment(self, txt):
        pd_comment = Comment(0, 0, txt.split(" "))
        cbbox = self.calc_brect(pd_comment)
        comment_litem = LayoutItem(0, 0, cbbox[2], cbbox[3])
        setattr(pd_comment, "layout", comment_litem)
        return pd_comment

    def doc2msg(self, doc_msg):
        assert isinstance(doc_msg, DocPdmessage)
        pdm = Message(0, 0, [doc_msg.text()])
        obj_bbox = list(self.calc_brect(pdm))
        litem = LayoutItem(doc_msg.offset(), 0, obj_bbox[2], obj_bbox[3])
        setattr(pdm, "layout", litem)
        return pdm

    def doc2obj(self, doc_obj):
        assert isinstance(doc_obj, DocPdobject)
        args = list(filter(None, doc_obj.args()))
        pd_obj = factory.make_by_name(doc_obj.name(), args, **doc_obj.attrs())
        obj_bbox = list(self.calc_brect(pd_obj))
        litem = LayoutItem(doc_obj.offset(), 0, obj_bbox[2], obj_bbox[3])
        setattr(pd_obj, "layout", litem)

        if doc_obj.highlight():
            setattr(pd_obj, "highlight", True)

        return pd_obj

    def connect_begin(self, c):
        try:
            src_id = self._pdobj_id_map[c.src_id()]
            dest_id = self._pdobj_id_map[c.dest_id()]
            src_out = c._src_out
            dest_in = c._dest_in

            self._canvas.add_connection(src_id, src_out, dest_id, dest_in)
        except KeyError as e:
            logging.warning("connection not found: {0:s}:{1:s} => {2:s}:{3:s}".
                            format(c.src_id(), src_out, c.dest_id(), dest_in))

    def message_begin(self, msg_obj):
        pd_msg = self.doc2msg(msg_obj)
        self._canvas.append_object(pd_msg)

        # handle object comment
        if msg_obj.comment:
            pd_comment = self.comment2pd_comment(msg_obj.comment)
            self._canvas.append_object(pd_comment)

            hor_layout = Layout.horizontal(self._comment_xoffset)
            hor_layout.add_item(pd_msg.layout)
            hor_layout.add_item(pd_comment.layout)
            self._cur_layout[-1].add_layout(hor_layout)
        else:
            self._cur_layout[-1].add_item(pd_msg.layout)

        self.add_id_mapping(msg_obj, pd_msg)

    def object_begin(self, doc_obj):
        pd_obj = self.doc2obj(doc_obj)
        self._canvas.append_object(pd_obj)

        # handle object comment
        if doc_obj.comment:
            pd_comment = self.comment2pd_comment(doc_obj.comment)
            self._canvas.append_object(pd_comment)

            hor_layout = Layout.horizontal(self._comment_xoffset)
            hor_layout.add_item(pd_obj.layout)
            hor_layout.add_item(pd_comment.layout)
            self._cur_layout[-1].add_layout(hor_layout)
        else:
            self._cur_layout[-1].add_item(pd_obj.layout)

        self.add_id_mapping(doc_obj, pd_obj)

    def add_id_mapping(self, doc_obj, pd_obj):
        self._pdobj_id_map[doc_obj.id] = pd_obj.id

    def comment(self, doc_comment):
        comments = doc_comment.text().split("\n")

        vlayout = Layout.vertical()

        for c in comments:
            pd_c = self.comment2pd_comment(c)
            self._canvas.append_object(pd_c)
            vlayout.add_item(pd_c.layout)

        self._cur_layout[-1].add_layout(vlayout)
