#!/usr/bin/env python
# coding=utf-8

# Copyright (C) 2014 by Serge Poltavski                                   #
# serge.poltavski@gmail.com                                               #
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

__author__ = 'Serge Poltavski'

from pdbaseobject import *
from pdpainter import *
import cairo
import textwrap
from pddrawstyle import *
from math import pi
from pdcanvas import PdCanvas


class CairoPainter(PdPainter):
    def __init__(self, width, height, output, fmt="png", **kwargs):
        PdPainter.__init__(self)
        self.style = PdDrawStyle()

        self.st_font_slant = cairo.FONT_SLANT_NORMAL
        self.st_font_weight = cairo.FONT_WEIGHT_NORMAL
        self.st_line_join = cairo.LINE_JOIN_ROUND

        assert width > 0
        assert height > 0

        self.width = width
        self.height = height

        assert fmt
        fmt = fmt.lower()
        self.format = fmt

        assert output
        self.output = output

        if fmt == 'png':
            self.ims = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.width, self.height)
        elif fmt == 'pdf':
            assert self.output
            self.ims = cairo.PDFSurface(self.output, self.width, self.height)
        elif fmt == 'svg':
            assert self.output
            self.ims = cairo.SVGSurface(self.output, self.width, self.height)

        self.cr = cairo.Context(self.ims)

        self.set_src_color(self.style.fill_color)
        self.cr.rectangle(0, 0, self.width, self.height)
        self.cr.fill()

        self.cr.select_font_face(self.style.font_family, self.st_font_slant, self.st_font_weight)
        self.cr.set_font_size(self.style.font_size)
        self.cr.set_line_join(self.st_line_join)

        matrix = cairo.Matrix()
        if 'xoffset' in kwargs:
            matrix.translate(kwargs['xoffset'], 0)
        if 'yoffset' in kwargs:
            matrix.translate(0, kwargs['yoffset'])

        self.cr.set_matrix(matrix)

    def draw_rect(self, x, y, w, h, **kwargs):
        self.cr.save()
        if 'color' in kwargs:
            self.set_src_color(kwargs['color'])

        if 'width' in kwargs:
            self.cr.set_line_width(kwargs['width'])

        self.cr.rectangle(x + 0.5, y + 0.5, w, h)

        if 'fill' in kwargs:
            self.set_src_color(kwargs['fill'])
            self.cr.fill_preserve()

        self.cr.stroke()
        self.cr.restore()

    def set_src_color(self, rgb):
        if isinstance(rgb, float):
            self.cr.set_source_rgb(rgb, rgb, rgb)
        elif len(rgb) == 3:
            self.cr.set_source_rgb(rgb[0], rgb[1], rgb[2])

    def __del__(self):
        if self.format == 'png':
            self.ims.write_to_png(self.output)

    def draw_box(self, x, y, w, h):
        self.cr.save()
        self.cr.set_line_width(self.style.obj_line_width)
        self.set_src_color(self.style.obj_border_color)
        self.cr.rectangle(x + 0.5, y + 0.5, w, h)
        self.cr.stroke_preserve()
        self.set_src_color(self.style.obj_fill_color)
        self.cr.fill()
        self.cr.restore()

    def draw_txt(self, x, y, txt):
        (tx, ty, width, height, dx, dy) = self.cr.text_extents(txt)
        self.set_src_color(self.style.obj_text_color)
        self.cr.move_to(x + self.style.obj_pad_x, y + height + self.style.obj_pad_y)
        self.cr.show_text(txt)

    def draw_xlets(self, xlets, x, y, obj_width):
        if not xlets:
            return

        inlet_space = 0
        if len(xlets) > 1:
            inlet_space = (obj_width - len(xlets) * self.style.xlet_width) / (len(xlets) - 1)

        for num in xrange(0, len(xlets)):
            inx = x + num * inlet_space
            if num != 0:
                inx += num * self.style.xlet_width

            xlet = xlets[num]

            if xlet in (PdBaseObject.XLET_MESSAGE, PdBaseObject.XLET_GUI):
                self.set_src_color(self.style.xlet_msg_color)
            else:
                self.set_src_color(self.style.xlet_snd_color)

            iny = y
            self.cr.set_line_width(self.style.obj_line_width)
            self.cr.rectangle(inx + 0.5, iny + 0.5, self.style.xlet_width, self.xlet_height(xlet))
            self.cr.stroke_preserve()

            if xlet == PdBaseObject.XLET_SOUND:
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
        w = width + self.style.obj_pad_x * 2
        h = self.style.obj_height

        self.draw_box(x, y, w, h)
        self.draw_txt(x, y, txt)

        self.draw_xlets(subpatch.inlets(), x, y, w)
        self.draw_xlets(subpatch.outlets(), x, y + h - self.style.xlet_msg_height, w)

    def draw_object(self, obj):
        txt = obj.to_string()
        (x, y, width, height, dx, dy) = self.cr.text_extents(txt)
        x = obj.x
        y = obj.y
        w = max(width + self.style.obj_pad_x * 2, self.style.obj_min_width)
        h = self.style.obj_height
        obj.set_width(w)
        obj.set_height(h)

        if hasattr(obj, "highlight"):
            pad = self.style.highlight_padding
            self.cr.rectangle(x + 0.5 - pad, y + 0.5 - pad, w + pad*2, h + pad*2)
            self.set_src_color(self.style.highlight_color)
            self.cr.fill()

        self.cr.set_line_width(self.style.obj_line_width)
        self.draw_box(x, y, w, h)
        self.draw_txt(x, y, txt)
        self.draw_xlets(obj.inlets(), x, y, w)
        self.draw_xlets(obj.outlets(), x, y + h - self.style.xlet_msg_height, w)

    def draw_message(self, message):
        txt = message.to_string()
        (x, y, width, height, dx, dy) = self.cr.text_extents(txt)
        x = message.x
        y = message.y
        w = width + self.style.obj_pad_x * 4
        h = self.style.obj_height
        message.set_height(h)
        message.set_width(w)

        # draw message box
        cr = self.cr
        self.set_src_color(self.style.obj_border_color)
        edge_w = 8
        edge_h = 10

        cr.save()
        cr.set_line_width(self.style.obj_line_width)
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
        self.set_src_color(self.style.msg_fill_color)
        cr.fill()
        cr.stroke()
        cr.restore()

        self.draw_txt(x, y, txt)
        self.draw_xlets(message.inlets(), x, y, w)
        self.draw_xlets(message.outlets(), x, y + h - self.style.xlet_msg_height, w)

    def xlet_height(self, t):
        if t == PdBaseObject.XLET_GUI:
            return self.style.xlet_gui_height
        else:
            return self.style.xlet_msg_height

    def inlet_connection_coords(self, obj, inlet_no):
        inlets = obj.inlets()

        xlet_space = 0
        if len(inlets) > 1:
            xlet_space = (obj.width - len(inlets) * self.style.xlet_width) / float(len(inlets) - 1)

        x = obj.x + (xlet_space + self.style.xlet_width) * inlet_no + self.style.xlet_width / 2.0
        y = obj.y

        return x, y

    def outlet_connection_coords(self, obj, outlet_no):
        outlets = obj.outlets()

        xlet_space = 0
        if len(outlets) > 1:
            xlet_space = (obj.width() - len(outlets) * self.style.xlet_width) / float(len(outlets) - 1)

        x = obj.x + (xlet_space + self.style.xlet_width) * outlet_no + self.style.xlet_width / 2.0
        if isinstance(obj, PdCanvas):
            y = obj.top + self.style.obj_height
        else:
            y = obj.bottom
        return x, y

    def draw_connections(self, canvas):
        for key, c in canvas.connections.items():
            src_obj = c[0]
            src_outl = c[1]
            if not src_obj.outlets():
                continue

            src_outl_type = src_obj.outlets()[src_outl]
            dest_obj = c[2]
            dest_inl = c[3]
            if not dest_obj.inlets():
                continue

            dest_inl_type = dest_obj.inlets()[dest_inl]

            sx, sy = self.outlet_connection_coords(src_obj, src_outl)
            dx, dy = self.inlet_connection_coords(dest_obj, dest_inl)

            # print sx, sy, "->", dx, dy

            self.cr.save()
            if dest_inl_type == PdBaseObject.XLET_SOUND and src_outl_type == PdBaseObject.XLET_SOUND:
                self.cr.set_line_width(self.style.conn_snd_width)
                self.set_src_color(self.style.conn_snd_color)
                # pixel correction
                if self.style.conn_snd_width % 2 == 0:
                    sx += 0.5
                    dx += 0.5

                self.cr.move_to(sx, sy)
                self.cr.line_to(dx, dy)
                self.cr.stroke()
                self.cr.set_dash(self.style.conn_snd_dash)
                self.set_src_color(self.style.conn_snd_color2)
            else:
                self.cr.set_line_width(self.style.conn_msg_width)
                self.set_src_color(self.style.conn_msg_color)
                # pixel correction
                if self.style.conn_msg_width % 2 == 1 and (sx - int(sx) == 0):
                    sx += 0.5
                    dx += 0.5

                sy += self.style.conn_msg_width

            self.cr.move_to(sx, sy)
            self.cr.line_to(dx, dy)
            self.cr.stroke()
            self.cr.restore()

        pass

    def draw_comment(self, comment):
        txt = comment.text()
        lines = textwrap.wrap(txt, 59)

        self.set_src_color(self.style.comment_color)
        lnum = 0
        for line in lines:
            line = ";\n".join(line.split(";")).split("\n")
            for subl in line:
                subl = subl.strip()
                self.draw_txt(comment.x, comment.y + lnum * self.style.font_size, subl)
                lnum += 1

    def draw_poly(self, vertexes, **kwargs):
        assert len(vertexes) > 1
        assert len(vertexes[0]) == 2
        self.cr.save()
        self.cr.set_line_width(self.style.obj_line_width)
        self.cr.move_to(vertexes[0][0] + 0.5, vertexes[0][1] + 0.5)
        for v in vertexes[1:]:
            self.cr.rel_line_to(v[0], v[1])

        self.cr.line_to(vertexes[0][0] + 0.5, vertexes[0][1] + 0.5)

        if 'fill' in kwargs:
            self.set_src_color(kwargs['fill'])
            self.cr.fill_preserve()

        if 'outline' in kwargs:
            self.set_src_color(kwargs['outline'])
            self.cr.stroke()

        self.cr.restore()

    def draw_text(self, x, y, text, **kwargs):
        self.cr.save()

        if 'color' in kwargs:
            self.set_src_color(kwargs['color'])
        else:
            self.set_src_color((0, 0, 0))

        if 'font_size' in kwargs:
            self.cr.set_font_size(kwargs['font_size'])

        if 'font' in kwargs:
            self.cr.select_font_face(kwargs['font'])

        self.cr.move_to(x, y)
        self.cr.show_text(text)
        self.cr.restore()

    def draw_inlets(self, inlets, x, y, width):
        self.draw_xlets(inlets, x, y, width)

    def draw_outlets(self, outlets, x, y, width):
        if not outlets:
            return

        yoffset = self.style.xlet_height(outlets[0])
        self.draw_xlets(outlets, x, y - yoffset, width)

    def draw_circle(self, x, y, radius, **kwargs):
        self.cr.save()
        self.cr.set_line_width(self.style.obj_line_width)
        self.cr.arc(x, y, radius, 0, 2*pi)
        if 'fill' in kwargs:
            self.set_src_color(kwargs['fill'])
            self.cr.fill_preserve()

        if 'outline' in kwargs:
            self.set_src_color(kwargs['outline'])
            self.cr.stroke()

        self.cr.restore()

    def draw_line(self, x0, y0, x1, y1, **kwargs):
        self.cr.save()
        self.cr.set_line_width(float(kwargs.get('width', 1)))
        if 'color' in kwargs:
            self.set_src_color(kwargs['color'])

        self.cr.set_line_cap(cairo.LINE_CAP_BUTT)
        self.cr.move_to(x0 + 0.5, y0 + 0.5)
        self.cr.line_to(x1 + 0.5, y1 + 0.5)
        self.cr.stroke()
        self.cr.restore()

    def draw_graph(self, graph):
        print graph