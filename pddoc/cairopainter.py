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

from __future__ import print_function

__author__ = 'Serge Poltavski'

import cairo
import textwrap
from math import pi
import logging

from .pdpainter import PdPainter
from .pd import XLET_GUI, XLET_SOUND, XLET_MESSAGE, Canvas


class CairoPainter(PdPainter):
    def __init__(self, width, height, output, fmt="png", **kwargs):
        PdPainter.__init__(self)

        from .pd.drawstyle import DrawStyle
        self.style = DrawStyle()

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
        self.output = output

        if fmt == 'png':
            self.ims = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.width, self.height)
        elif fmt == 'pdf':
            assert self.output
            self.ims = cairo.PDFSurface(self.output, self.width, self.height)
        elif fmt == 'svg':
            assert self.output
            self.ims = cairo.SVGSurface(self.output, self.width, self.height)
        else:
            msg = "unsupported format: \"{0:s}\"".format(fmt)
            logging.error(msg)
            raise RuntimeError(msg)

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

    def __del__(self):
        if self.format == 'png' and self.output:
            self.ims.write_to_png(self.output)

    def draw_rect(self, x, y, w, h, **kwargs):
        self.cr.save()

        if 'width' in kwargs:
            self.cr.set_line_width(kwargs['width'])

        if self.cr.get_line_width() % 2 == 1:
            x = round(x) + 0.5
            y = round(y) + 0.5

        self.cr.rectangle(x, y, w, h)

        if 'fill' in kwargs:
            self.set_src_color(kwargs['fill'])
            self.cr.fill_preserve()

        if 'color' in kwargs:
            self.set_src_color(kwargs['color'])

        self.cr.stroke()
        self.cr.restore()

    def set_src_color(self, rgb):
        if isinstance(rgb, float):
            self.cr.set_source_rgb(rgb, rgb, rgb)
        elif len(rgb) == 3:
            self.cr.set_source_rgb(rgb[0], rgb[1], rgb[2])

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
        ascent, descent, height, ax, ay = self.cr.font_extents()
        self.cr.save()
        self.set_src_color(self.style.obj_text_color)
        self.cr.move_to(x, y + ascent)
        self.cr.show_text(txt)
        self.cr.restore()

    def draw_xlets(self, xlets, x, y, obj_width):
        if not xlets:
            return

        inlet_space = 0
        if len(xlets) > 1:
            inlet_space = (obj_width - len(xlets) * self.style.xlet_width) / (len(xlets) - 1)

        for num in range(0, len(xlets)):
            inx = x + num * inlet_space
            if num != 0:
                inx += num * self.style.xlet_width

            xlet = xlets[num]

            if xlet in (XLET_MESSAGE, XLET_GUI):
                self.set_src_color(self.style.xlet_msg_color)
            else:
                self.set_src_color(self.style.xlet_snd_color)

            iny = y
            self.cr.set_line_width(self.style.obj_line_width)
            if self.style.obj_line_width % 2 == 1:
                inx = round(inx) + 0.5
                iny = round(iny) + 0.5

            self.cr.rectangle(inx, iny, self.style.xlet_width, self.xlet_height(xlet))
            self.cr.stroke_preserve()

            if xlet == XLET_SOUND:
                self.cr.fill()
                self.cr.stroke()
            else:
                self.cr.stroke()

            num += 1

    def draw_subpatch(self, subpatch):
        if subpatch.is_graph_on_parent():
            x = subpatch.x
            y = subpatch.y
            w = subpatch._gop['width']
            h = subpatch._gop['height']
            self.draw_rect(x, y, w, h, color=self.style.obj_border_color, width=1)
            m = self.cr.get_matrix()
            m.translate(x - subpatch._gop['xoff'], y - subpatch._gop['yoff'])
            self.cr.save()
            self.cr.set_matrix(m)
            for obj in subpatch.objects:
                if obj.draw_on_parent():
                    obj.draw(self)

            self.cr.restore()

            if not subpatch._gop['hide_args']:
                txt = "pd " + subpatch.args_to_string()
                self.draw_text(x + self.style.obj_pad_x,
                               y + self.style.font_size,
                               txt,
                               font_size=self.style.font_size)

            self.draw_xlets(subpatch.inlets(), x, y, w)
            self.draw_xlets(subpatch.outlets(), x, y + h - self.style.xlet_msg_height, w)
            return
        else:
            self.draw_object_txt(subpatch, "pd " + subpatch.args_to_string())

    def draw_gop(self, obj, gop_canvas):
        x, y, w, h = gop_canvas.gop_rect()
        self.cr.save()
        self.draw_box(obj.x, obj.y, w, h)
        self.cr.translate(obj.x - x, obj.y - y)
        gop_canvas.draw_gop(self)
        self.cr.restore()
        pass

    def text_size(self, txt, font_size=None):
        self.cr.save()
        self.cr.select_font_face(self.style.font_family)

        if font_size is not None:
            self.cr.set_font_size(int(font_size))
        else:
            self.cr.set_font_size(self.style.font_size)

        w = self.cr.text_extents(txt)[2]
        h = self.cr.font_extents()[2]
        self.cr.restore()
        return w, h

    def box_size(self, txt):
        w, h = self.text_size(txt)
        # box padding
        w += self.style.obj_pad_x * 3  # set by empirical way
        h += self.style.obj_pad_y * 2

        # objects have minimal width. otherwise such objects as [*] could be too narrow
        w = max(w, self.style.obj_min_width)
        return w, h

    def draw_hightlight(self, x, y, w, h):
        self.cr.save()
        pad = self.style.highlight_padding
        self.cr.rectangle(x + 0.5 - pad, y + 0.5 - pad, w + pad * 2, h + pad * 2)
        self.set_src_color(self.style.highlight_color)
        self.cr.fill()
        self.cr.restore()

    def draw_object(self, obj):
        self.draw_object_txt(obj, obj.to_string())

    def draw_object_txt(self, obj, txt):
        self.cr.save()
        self.cr.select_font_face(self.style.font_family)

        x = obj.x
        y = obj.y
        w, h = self.box_size(txt)

        obj.set_width(w)
        obj.set_height(h)

        if hasattr(obj, "highlight"):
            self.draw_hightlight(x, y, w, h)

        self.draw_box(x, y, w, h)
        self.draw_txt(x + self.style.obj_pad_x, y + self.style.obj_pad_y + 1, txt)
        self.draw_xlets(obj.inlets(), x, y, w)
        self.draw_xlets(obj.outlets(), x, y + h - self.style.xlet_msg_height, w)
        self.cr.restore()

    def draw_message_box(self, x, y, w, h):
        edge_w = 8
        edge_h = 10

        self.cr.save()
        self.set_src_color(self.style.obj_border_color)
        self.cr.set_line_width(self.style.obj_line_width)
        tx = x + 0.5
        ty = y + 0.5
        self.cr.move_to(tx, ty)
        self.cr.line_to(tx, ty + h)
        self.cr.line_to(tx + w, ty + h)
        self.cr.line_to(tx + w - edge_w / 2.0, ty + (h + edge_h) / 2.0)
        self.cr.line_to(tx + w - edge_w / 2.0, ty + (h - edge_h) / 2.0)
        self.cr.line_to(tx + w, ty)
        self.cr.line_to(tx, ty)
        self.cr.stroke_preserve()
        self.set_src_color(self.style.msg_fill_color)
        self.cr.fill()
        self.cr.stroke()
        self.cr.restore()

    def message_size(self, txt):
        w, h = self.box_size(txt)
        # increase width for message rightmost curved tail: [msg(
        w += self.style.obj_pad_y * 2
        return w, h

    def draw_message(self, message):
        txt = message.to_string()
        x = message.x
        y = message.y
        w, h = self.message_size(txt)

        message.set_height(h)
        message.set_width(w)

        self.draw_message_box(x, y, w, h)
        self.draw_txt(x + self.style.obj_pad_x, y + self.style.obj_pad_y + 1, txt)
        self.draw_xlets(message.inlets(), x, y, w)
        self.draw_xlets(message.outlets(), x, y + h - self.style.xlet_msg_height, w)

    def xlet_height(self, t):
        if t == XLET_GUI:
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
            xlet_space = (obj.width - len(outlets) * self.style.xlet_width) / float(len(outlets) - 1)

        x = obj.x + (xlet_space + self.style.xlet_width) * outlet_no + self.style.xlet_width / 2.0
        if isinstance(obj, Canvas):
            if obj.is_graph_on_parent():
                y = obj._gop['height'] + obj.y
            else:
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
            if dest_inl_type == XLET_SOUND and src_outl_type == XLET_SOUND:
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
        line_height = self.cr.font_extents()[2]
        lnum = 0
        for line in lines:
            line = ";\n".join(line.split(";")).split("\n")
            for subl in line:
                subl = subl.strip()
                self.draw_txt(comment.x, comment.y + lnum * line_height, subl)
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

    def draw_arc(self, x, y, radius, start_angle, end_angle, **kwargs):
        self.cr.save()
        if 'width' in kwargs:
            self.cr.set_line_width(float(kwargs['width']))

        self.cr.move_to(x, y)
        self.cr.arc(x, y, radius, start_angle, end_angle)

        if 'outline' in kwargs:
            self.set_src_color(kwargs['outline'])

        self.cr.stroke()
        self.cr.restore()

    def draw_circle(self, x, y, radius, **kwargs):
        self.cr.save()
        self.cr.set_line_width(self.style.obj_line_width)
        self.cr.arc(x, y, radius, 0, 2 * pi)
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
        if int(self.cr.get_line_width()) % 2 == 1:
            y0 = round(y0) + 0.5
            y1 = round(y1) + 0.5

        if self.cr.get_line_width() == 1:
            x0 = round(x0) + 0.5
            x1 = round(x1) + 0.5

        self.cr.move_to(x0, y0)
        self.cr.line_to(x1, y1)
        self.cr.stroke()
        self.cr.restore()

    def draw_graph(self, graph):
        print(graph)
