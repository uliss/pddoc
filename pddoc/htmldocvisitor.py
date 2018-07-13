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

from mako.template import Template

from .cairopainter import CairoPainter
from .docobjectvisitor import DocObjectVisitor


class HtmlDocVisitor(DocObjectVisitor):
    def __init__(self):
        DocObjectVisitor.__init__(self)
        self._image_output_dir = HtmlDocVisitor.image_output_dir
        self._image_extension = "png"
        self._image_output_dir = "img"

        self._css_file = ""
        self._css = ""
        # template config
        tmpl_path = "{0:s}/share/html_object.tmpl".format(os.path.dirname(__file__))
        self._html_template = Template(filename=tmpl_path)

    def css_file(self):
        return self._css_file

    def set_css_file(self, filename):
        self._css_file = filename

    def css(self):
        return self._css

    def set_css(self, content):
        self._css = content

    def make_image_painter(self, w, h, fname):
        return CairoPainter(w, h, fname, "png",
                                         xoffset=self._canvas_padding,
                                         yoffset=self._canvas_padding)

    def render(self):
        return self._html_template.render(
            title=self._title,
            description=self._description,
            keywords=self._keywords,
            css_file=self._css_file,
            css=self._css,
            aliases=self._aliases,
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
