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
import textwrap

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

    st_message_fill_color = (0.94)

    st_object_xpad = 2.5
    st_object_ypad = 1
    st_object_height = 17
    st_object_min_width = 22

    st_xlet_width = 7
    st_xlet_height = 2
    st_xlet_height_gui = 1
    st_xlet_msg_color = (0, 0, 0)
    st_xlet_snd_color = (0.3, 0.2, 0.4)

    st_gui_border_color = (0, 0, 0)

    st_connection_sndline_width = 2
    st_connection_sndline_color = (0.2, 0.2, 0.2)
    st_connection_sndline_color2 = (0.6, 0.6, 0)
    st_connection_line_color = (0, 0, 0)
    st_connection_line_width = 1
    st_connection_dash = [4, 8]

    st_comment_color = (0.5, 0.5, 0.5)


    def __init__(self, width, height, output, format="png"):
        PdPainter.__init__(self)

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
        if isinstance(rgb, float):
            self.cr.set_source_rgb(rgb, rgb, rgb)
        elif len(rgb) == 3:
            self.cr.set_source_rgb(rgb[0], rgb[1], rgb[2])


    def __del__(self):
        if self.format == 'png':
            self.ims.write_to_png(self.output)

    def draw_box(self, x, y, w, h):
        self.set_src_color(self.st_object_border_color)
        self.cr.rectangle(x + 0.5, y + 0.5, w, h)
        self.cr.stroke_preserve()
        self.set_src_color(self.st_object_fill_color)
        self.cr.fill()

    def draw_txt(self, x, y, txt):
        (tx, ty, width, height, dx, dy) = self.cr.text_extents(txt)
        self.set_src_color(self.st_text_color)
        self.cr.move_to(x + self.st_object_xpad, y + height + self.st_object_ypad)
        self.cr.show_text(txt)

    def draw_xlets(self, xlets, x, y, obj_width):
        if not xlets:
            return

        inlet_space = 0
        if len(xlets) > 1:
            inlet_space = (obj_width - len(xlets) * self.st_xlet_width) / (len(xlets) - 1)


        for num in xrange(0, len(xlets)):
            inx = x + num * inlet_space
            if num != 0:
                inx += (num) * self.st_xlet_width

            xlet = xlets[num]

            if xlet in (PdBaseObject.XLET_MESSAGE, PdBaseObject.XLET_GUI):
                self.set_src_color(self.st_xlet_msg_color)
            else:
                self.set_src_color(self.st_xlet_snd_color)

            iny = y
            self.cr.rectangle(inx + 0.5, iny + 0.5, self.st_xlet_width, self.xlet_height(xlet))
            self.cr.stroke_preserve()

            if xlet == PdBaseObject.XLET_SOUND:
                self.cr.fill()
                self.cr.stroke()
            else:
                self.cr.stroke()

            num += 1


    def draw_subpatch(self, subpatch):
        txt = "pd " + subpatch.name()
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
        w = max(width + self.st_object_xpad * 2, self.st_object_min_width)
        h = self.st_object_height
        object.width = w
        object.height = h

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
        message.height = h
        message.width = w

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
        self.set_src_color(self.st_message_fill_color)
        cr.fill()
        cr.stroke()
        cr.restore()

        self.draw_txt(x, y, txt)
        self.draw_xlets(message.inlets(), x, y, w)
        self.draw_xlets(message.outlets(), x, y + h - self.st_xlet_height, w)

    def draw_core_gui(self, gui):
        if gui.name() == "tgl":
            if not gui.props["bg_color"].is_black():
                self.set_src_color(gui.props["bg_color"].to_float())
            else:
                self.set_src_color((1, 1, 1))

            self.cr.rectangle(gui.x + 0.5, gui.y + 0.5, gui.width(), gui.height())
            self.cr.fill()
            self.set_src_color(self.st_gui_border_color)
            self.cr.rectangle(gui.x + 0.5, gui.y + 0.5, gui.width(), gui.height())
            self.cr.stroke()

            # print gui.inlets()
            self.draw_xlets(gui.inlets(), gui.x, gui.y, gui.width())
            self.draw_xlets(gui.outlets(), gui.x, gui.y + gui.height() - self.st_xlet_height_gui,
                            gui.props["size"])
            return

        if gui.name() == "cnv":
            self.cr.save()
            x = gui.x
            y = gui.y
            w = gui.width()
            h = gui.height()
            self.set_src_color(gui.props["bg_color"].to_float())
            self.cr.rectangle(x, y, w, h)
            self.cr.fill()

            fonts = ("Monaco Bold", "Helvetica", "Times")
            fontsize = gui.props["fontsize"]
            fontidx = int(gui.props["font"])
            self.cr.select_font_face(fonts[fontidx])
            self.cr.set_font_size(fontsize)
            self.set_src_color(gui.props["label_color"].to_float())
            txt = gui.props["label"]
            tx, ty, tw, th, tdx, tdy = self.cr.text_extents(txt)
            self.cr.move_to(x + gui.props["label_xoff"], y + gui.props["label_yoff"] + th)
            self.cr.show_text(txt)
            self.cr.restore()
            return



    def xlet_height(self, t):
        if t == PdBaseObject.XLET_GUI:
            return self.st_xlet_height_gui
        else:
            return self.st_xlet_height

    def inlet_connection_coords(self, obj, inlet_no):
        inlets = obj.inlets()

        xlet_space = 0;
        if len(inlets) > 1:
            xlet_space = (obj.width - len(inlets) * self.st_xlet_width) / float(len(inlets) - 1)

        x = obj.x + xlet_space * inlet_no + self.st_xlet_width / 2.0
        y = obj.y

        return (x, y)

    def outlet_connection_coords(self, obj, outlet_no):
        outlets = obj.outlets()

        xlet_space = 0;
        if len(outlets) > 1:
            xlet_space = (obj.width - len(outlets) * self.st_xlet_width) / float(len(outlets) - 1)

        x = obj.x + xlet_space * outlet_no + self.st_xlet_width / 2.0
        y = obj.y + obj.height
        return (x, y)

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

            self.cr.save()
            if dest_inl_type == PdBaseObject.XLET_SOUND and src_outl_type == PdBaseObject.XLET_SOUND:
                self.cr.set_line_width(self.st_connection_sndline_width)
                self.set_src_color(self.st_connection_sndline_color)
                # pixel correction
                if self.st_connection_sndline_width % 2 == 0:
                    sx += 0.5
                    dx += 0.5

                self.cr.move_to(sx, sy)
                self.cr.line_to(dx, dy)
                self.cr.stroke()
                self.cr.set_dash(self.st_connection_dash)
                self.set_src_color(self.st_connection_sndline_color2)
            else:
                self.cr.set_line_width(self.st_connection_line_width)
                self.set_src_color(self.st_connection_line_color)
                # pixel correction
                if self.st_connection_line_width % 2 == 0:
                    sx += 0.5
                    dx += 0.5

                sy += self.st_connection_line_width

            self.cr.move_to(sx, sy)
            self.cr.line_to(dx, dy)
            self.cr.stroke()
            self.cr.restore()

        pass

    def draw_comment(self, comment):
        txt = comment.text()
        lines = textwrap.wrap(txt, 59)

        self.set_src_color(self.st_comment_color)
        lnum = 0
        for line in lines:
            line = ";\n".join(line.split(";")).split("\n")
            for subl in line:
                subl = subl.strip()
                self.draw_txt(comment.x, comment.y + lnum * self.st_font_size, subl)
                lnum += 1

pass