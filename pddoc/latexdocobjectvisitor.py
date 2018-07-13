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

import os.path
from mako.template import Template

from .cairopainter import CairoPainter
from .docobjectvisitor import DocObjectVisitor


class LatexDocObjectVisitor(DocObjectVisitor):
    def __init__(self):
        DocObjectVisitor.__init__(self)
        self._image_extension = "pdf"
        self._image_output_dir = "pdf"
        self._includegraphics_scale = 0.7
        # template config
        tmpl_path = "{0:s}/share/latex_object_tmpl.tex".format(os.path.dirname(__file__))
        self._latex_template = Template(filename=tmpl_path)

    def make_image_painter(self, w, h, fname):
        return CairoPainter(w, h, fname, "pdf",
                                         xoffset=self._canvas_padding,
                                         yoffset=self._canvas_padding)

    def render(self):
        return self._latex_template.render(
            title=self._title,
            title_image=self.image_pdobject_fname(self._title),
            description=self._description,
            keywords=self._keywords,
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
            category=self._category,
            graphics_scale=self._includegraphics_scale)
