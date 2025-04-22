#!/usr/bin/env python
# coding=utf-8

# Copyright (C) 2014 by Serge Poltavski                                   #
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

from jinja2 import Environment, PackageLoader, select_autoescape

from .docobjectvisitor import DocObjectVisitor
from .pdpainter import PdPainter


class MarkdownVisitor(DocObjectVisitor):
    def __init__(self, locale="EN"):
        DocObjectVisitor.__init__(self)
        self._image_output_dir = MarkdownVisitor.image_output_dir
        self._image_extension = "png"
        self._image_output_dir = "img"
        self._example_img_dir = "examples/"
        self._example_pd_dir = "examples/"

        # template config
        if "EN" in locale:
            tmpl_path = "md_object.tmpl.md"
            self.lang = locale.lower()
        elif "RU" in locale:
            tmpl_path = "md_object_ru.tmpl.md"
            self.lang = locale.lower()
        else:
            tmpl_path = "md_object.tmpl.md"
            self.lang = 'en'

        def ws(txt):
            if isinstance(txt, str):
                return ' '.join(txt.replace('\n', ' ').split())
            else:
                return ' '

        def nnl(txt):
            return txt.replace('\n', ' ')

        self._env = Environment(
            loader=PackageLoader('pddoc', 'share'),
            autoescape=select_autoescape(['md'], default=True, default_for_string=True)
        )
        self._env.filters['nnl'] = nnl
        self._env.filters['ws'] = ws
        self._template = self._env.get_template(tmpl_path)

    @property
    def example_img_dir(self):
        return self._example_img_dir

    @example_img_dir.setter
    def example_img_dir(self, value: str):
        self._example_img_dir = value

    @property
    def example_pd_dir(self):
        return self._example_pd_dir

    @example_pd_dir.setter
    def example_pd_dir(self, value: str):
        self._example_pd_dir = value

    def alias_begin(self, tag):
        self._aliases.append("[%s]" % tag.text())

    def inlets_begin(self, inlets):
        self._inlets = inlets.items()

    def outlets_begin(self, outlets):
        self._outlets = outlets.items()

    def make_image_painter(self, w: int, h: int, fname: str):
        return PdPainter()

    def render(self):
        return self._template.render(
            title=self._title,
            description=self._description,
            keywords=self._keywords,
            pd_ascii=self._pdascii,
            aliases=self._aliases,
            license=self._license,
            version=self._version,
            examples=self._examples,
            info=self._info,
            inlets=self._inlets,
            outlets=self._outlets,
            arguments=self._arguments,
            properties=self._props,
            methods=self._methods,
            see_also=self._see_also,
            website=self._website,
            authors=self._authors,
            contacts=self._contacts,
            library=self._library,
            category=self._category,
            example_img_dir=self._example_img_dir,
            example_pd_dir=self._example_pd_dir,
            since=self._since)
