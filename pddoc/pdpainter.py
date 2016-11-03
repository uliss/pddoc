#!/usr/bin/env python
# coding=utf-8

# Copyright (C) 2014 by Serge Poltavski                                  #
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

from __future__ import print_function

__author__ = 'Serge Poltavski'


class PdPainter(object):
    def draw_canvas(self, canvas):
        pass

    def draw_comment(self, comment):
        print("Draw comment: #", comment.text())

    def draw_message(self, message):
        print("Draw message [id:%i]: %s" % (message.id, message.to_string()))

    def draw_object(self, obj):
        print("Draw object: [id:%i] [%s]" % (obj.id, " ".join(obj.args)))

    def draw_core_gui(self, gui):
        print("Draw core GUI: [id:%i] [%s]" % (gui.id, gui.name))

    def draw_subpatch(self, subpatch):
        print("Draw subpatch: [pd {0:s}]".format(subpatch.name))

    def draw_graph(self, graph):
        print("Draw graph ")

    def draw_connections(self, canvas):
        print("Draw connections ")

    def draw_poly(self, vertexes, **kwargs):
        print("Draw poly:", vertexes)

    def draw_text(self, x, y, text, **kwargs):
        print("Draw text:", text)

    def draw_inlets(self, inlets, x, y, width):
        print("Draw inlets:", inlets)

    def draw_outlets(self, outlets, x, y, width):
        print("Draw outlets:", outlets)

    def draw_circle(self, x, y, width, **kwargs):
        print("Draw circle")

    def draw_arc(self, x, y, radius, start_angle, end_angle, **kwargs):
        print("Draw arc")

    def draw_line(self, x0, y0, x1, y1, **kwargs):
        print("Draw line")

    def draw_rect(self, x, y, w, h, **kwargs):
        print("Draw rect")
