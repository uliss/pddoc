# /usr/bin/env python

# Copyright (C) 2014 by Serge Poltavski                                 #
# serge.poltavski@gmail.com                                             #
# #
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


# -*- coding: utf-8 -*-

__author__ = 'Serge Poltavski'

from pdpainter import *
import cairo


class CairoPainter(PdPainter):
    st_bg_color = (1, 1, 1)
    st_text_color = (0, 0, 0)
    st_object_border_color = (0.2, 0.2, 0.2)
    st_object_fill_color = (0.95, 0.95, 0.95)
    st_font = "terminus"
    st_font_size = 12
    st_font_slant = cairo.FONT_SLANT_NORMAL
    st_font_weight = cairo.FONT_WEIGHT_NORMAL
    st_line_width = 1
    st_line_join = cairo.LINE_JOIN_ROUND

    st_object_xpad = 2.5
    st_object_ypad = 2.5
    st_object_height = 16
    st_object_min_width = 20

    st_xlet_width = 8
    st_xlet_height = 2
    st_xlet_color = (0, 0, 0)

    def __init__(self, width, height, output, format="png"):
        super(CairoPainter, self).__init__()

        assert width > 0
        assert height > 0

        self.width = width
        self.height = height

        assert format
        format = format.lower()
        self.format = format

        assert output
        self.output = output

        if format == 'png':
            self.ims = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.width, self.height)
        elif format == 'pdf':
            assert self.output
            self.ims = cairo.PDFSurface(self.output, self.width, self.height)
        elif format == 'svg':
            assert self.output
            self.ims = cairo.SVGSurface(self.output, self.width, self.height)

        self.cr = cairo.Context(self.ims)

        self.set_src_color(self.st_bg_color)
        self.cr.rectangle(0, 0, self.width, self.height)
        self.cr.fill()

        self.cr.select_font_face(self.st_font, self.st_font_slant, self.st_font_weight)
        self.cr.set_font_size(self.st_font_size)
        self.cr.set_line_width(self.st_line_width)
        self.cr.set_line_join(self.st_line_join)

    def set_src_color(self, rgb):
        self.cr.set_source_rgb(rgb[0], rgb[1], rgb[2])

    def __del__(self):
        if self.format == 'png':
            self.ims.write_to_png(self.output)

    def draw_box(self, x, y, w, h):
        self.set_src_color(self.st_object_border_color)
        self.cr.rectangle(x + 0.5, y + 0.5, max(w, self.st_object_min_width), h)
        self.cr.stroke_preserve()
        self.set_src_color(self.st_object_fill_color)
        self.cr.fill()

    def draw_txt(self, x, y, txt):
        (tx, ty, width, height, dx, dy) = self.cr.text_extents(txt)
        self.set_src_color(self.st_text_color)
        self.cr.move_to(x + self.st_object_xpad, y + height)
        self.cr.show_text(txt)

    def draw_xlets(self, xlets, x, y, obj_width):
        self.set_src_color(self.st_xlet_color)

        if not xlets:
            return

        inlet_space = 0
        if len(xlets) > 1:
            inlet_space = (obj_width - len(xlets) * self.st_xlet_width) / (len(xlets) - 1)

        for num in xrange(0, len(xlets)):
            inx = x + num * inlet_space
            if num != 0:
                inx += (num) * self.st_xlet_width
                # inx = int(inx) + 0.5

            iny = y
            self.cr.rectangle(inx + 0.5, iny + 0.5, self.st_xlet_width, self.st_xlet_height)
            self.cr.stroke_preserve()

            if xlets[num] == PdBaseObject.XLET_SOUND:
                self.cr.fill()
                self.cr.stroke()
            else:
                self.cr.stroke()

            num += 1


    def draw_subpatch(self, subpatch):
        txt = "pd " + subpatch.name
        (x, y, width, height, dx, dy) = self.cr.text_extents(txt)
        x = subpatch.x
        y = subpatch.y
        w = width + self.st_object_xpad * 2
        h = self.st_object_height

        self.draw_box(x, y, w, h)
        self.draw_txt(x, y, txt)

        self.draw_xlets(subpatch.inlets(), x, y, w)
        self.draw_xlets(subpatch.outlets(), x, y + h - self.st_xlet_height, w)

    def draw_object(self, object):
        txt = object.to_string()
        (x, y, width, height, dx, dy) = self.cr.text_extents(txt)
        x = object.x
        y = object.y
        w = width + self.st_object_xpad * 2
        h = self.st_object_height

        self.draw_box(x, y, w, h)
        self.draw_txt(x, y, txt)
        self.draw_xlets(object.inlets(), x, y, w)
        self.draw_xlets(object.outlets(), x, y + h - self.st_xlet_height, w)

    def draw_message(self, message):
        txt = message.to_string()
        (x, y, width, height, dx, dy) = self.cr.text_extents(txt)
        x = message.x
        y = message.y
        w = width + self.st_object_xpad * 4
        h = self.st_object_height



        # draw message box
        cr = self.cr
        self.set_src_color(self.st_object_border_color)
        edge_w = 8
        edge_h = 10

        cr.save()
        tx = x + 0.5
        ty = y + 0.5
        cr.move_to(tx, ty)
        cr.line_to(tx, ty + h)
        cr.line_to(tx + w, ty + h)
        cr.line_to(tx + w - edge_w / 2.0, ty + (h + edge_h) / 2.0)
        cr.line_to(tx + w - edge_w / 2.0, ty + (h - edge_h) / 2.0)
        cr.line_to(tx + w, ty)
        cr.line_to(tx, ty)
        cr.stroke_preserve()
        cr.set_source_rgb(0.95, 0.95, 0.95)
        cr.fill()
        cr.stroke()
        cr.restore()

        self.draw_txt(x, y, txt)
        self.draw_xlets(message.inlets(), x, y, w)
        self.draw_xlets(message.outlets(), x, y + h - self.st_xlet_height, w)


pass