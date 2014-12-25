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

import pdcanvas
import pddrawer
import pdobject
import pdmessage
import cairopainter
import pdparser
from layout import *


class HtmlDocVisitor(object):
    def __init__(self, tmpl="default.tmpl"):
        self._body = ""
        self._head = ""
        self._html5 = False
        self._title = ""
        self._description = ""
        self._keywords = []
        self._template = tmpl
        self._website = ""
        self._version = ""
        self._inlet_counter = 0
        self._cur_canvas = None
        self._image_counter = 0
        self._cur_layout = []
        self._example_brect = ()
        self._pdobj_id_map = {}
        self._include = None
        self._css_theme = "../theme.css"
        self._img_output_dir = "./out"

    def title_begin(self, t):
        self._title = t.text()
        self._head += u"<title>PureData [{0:s}] object</title>\n".format(self._title)

    def website_begin(self, w):
        self._website = w.text()

    def object_begin(self, obj):
        self._head += '<meta http-equiv="Content-Type" content="text/html; charset=utf-8">\n'
        self._head += '<link rel="stylesheet" type="text/css" href="{0:s}">\n'.format(self._css_theme)

    def keywords_begin(self, k):
        self._keywords = k.keywords()
        self._head += u'<meta name="keywords" content="{0:s}">\n'.format(" ".join(self._keywords))

    def description_begin(self, d):
        self._description = d.text()
        self._head += u'<meta name="description" content="{0:s}">\n'.format(self._description)

    def version_begin(self, v):
        self._version = v.text()

    def footer(self):
        res = u'<div class="footer">version: {0:s}</div>\n'.format(self._version)
        return res

    def example_begin(self, ex):
        self._body += '<div class="example">\n'

    def example_end(self, ex):
        self._body += '</div>\n'

    def has_inlets(self, obj):
        return len(obj.inlet_dict()) > 0

    def has_outlets(self, obj):
        return len(obj.outlet_dict()) > 0

    def core_type_help(self, t):
        assert t in ("bang", "float", "list", "symbol", "any", "pointer")
        return '<a href="http://puredata.info/wiki/{0:s}.html">{1:s}</a>'.format(t, t)

    def process_xlets(self, xlets):
        for xlet_number in sorted(xlets):
            xlet_list = xlets[xlet_number]
            col_span = len(xlet_list)
            xlet_list_count = col_span

            for xl in xlet_list:
                self._body += "<tr>\n"
                if col_span == xlet_list_count:
                    self._body += "<td rowspan=\"{0:d}\" class=\"number\"><span>{1:s}</span></td>\n".format(col_span,
                                                                                                            xlet_number)

                self._body += u"<td class=\"type\">{0:s}</td>\n".format(self.core_type_help(xl.type()))
                range_str = lambda x: ("&ndash;".join(map(str, x))) if (len(x) > 1) else "&nbsp;"
                self._body += u"<td class=\"range\">{0:s}</td>\n".format(range_str(xl.range()))
                self._body += u"<td class=\"description\">{0:s}</td>\n".format(xl.text())
                self._body += "</tr>\n"
                col_span -= 1

    def pdexample_begin(self, pd):
        self._cur_canvas = pdcanvas.PdCanvas(0, 0, pd.width(), pd.height(), name="10")
        self._cur_canvas.type = pdcanvas.PdCanvas.TYPE_WINDOW

    def row_begin(self, row):
        lh = Layout(Layout.HORIZONTAL, 10)
        self._cur_layout.append(lh)

    def row_end(self, row):
        lh = self._cur_layout.pop()
        if self._cur_layout:
            self._cur_layout[-1].add_layout(lh)

        self._example_brect = lh.brect()

    def col_begin(self, col):
        lv = Layout(Layout.VERTICAL, 15)
        self._cur_layout.append(lv)

    def col_end(self, col):
        lv = self._cur_layout.pop()
        if len(self._cur_layout) > 0:
            self._cur_layout[-1].add_layout(lv)

        self._example_brect = lv.brect()

    def pdmessage_begin(self, obj):
        cnv = self._cur_canvas
        pdm = pdmessage.PdMessage(10, 10, [obj._msg])

        litem = LayoutItem(0, 0, 50, 20)
        self._cur_layout[-1].add_item(litem)
        setattr(pdm, "layout", litem)
        cnv.append_object(pdm)
        self._pdobj_id_map[obj._id] = pdm._id

    def pdobject_begin(self, obj):
        cnv = self._cur_canvas
        args = filter(None, obj._args.split(" "))

        pdo = pdobject.PdObject(obj.name(), 10, 10, -1, -1, args)
        pdo._id = obj._id
        litem = LayoutItem(0, 0, 50, 20)
        self._cur_layout[-1].add_item(litem)
        setattr(pdo, "layout", litem)

        cnv.append_object(pdo)
        self._pdobj_id_map[obj._id] = pdo._id

    def pdobject_end(self, obj):
        pass

    def pdinclude_begin(self, inc):
        fname = inc._file
        parser = pdparser.PdParser()
        parser.parse(fname)

        self._cur_canvas = parser.canvas
        self._include = True

    def pdexample_end(self, pd):
        if self._include:
            img_height = self._cur_canvas.width
            img_width = self._cur_canvas.height
        else:
            for pdo in self._cur_canvas.objects:
                litem = getattr(pdo, "layout")
                pdo.x = litem.x()
                pdo.y = litem.y()

            img_width = self._example_brect[2]
            img_height = self._example_brect[3]

        self._image_counter += 1
        fname = "image_{0:02d}.png".format(self._image_counter)
        output_fname = "./out/" + fname

        pad = 10
        painter = cairopainter.CairoPainter(img_width + 2 * pad, img_height + 2 * pad,
                                            output_fname, xoffset=pad, yoffset=pad)
        walker = pddrawer.PdDrawer()
        walker.draw(self._cur_canvas, painter)

        self._body += u'<img src="{0:s}" alt="example:{1:d}"/>\n'.format(fname, self._image_counter)

        self._include = False

    def pdconnect_begin(self, c):
        src_id = self._pdobj_id_map[c._src_id]
        dest_id = self._pdobj_id_map[c._dest_id]
        src_out = c._src_out
        dest_in = c._dest_in

        self._cur_canvas.add_connection(src_id, src_out, dest_id, dest_in)

    def inlets_begin(self, inlets):
        if not self.has_inlets(inlets):
            return

        self._body += '<div class="inlets">\n<h2>Inlets:</h2>\n'
        self._body += "<table>\n"
        self.process_xlets(inlets.inlet_dict())
        self._body += "</table>\n"
        self._body += '</div>\n'

    def outlets_begin(self, outlets):
        if not self.has_outlets(outlets):
            return

        self._body += '<div class="outlets">\n<h2>Outlets:</h2>\n'
        self._body += "<table>\n"
        self.process_xlets(outlets.outlet_dict())
        self._body += "</table>\n"
        self._body += '</div>\n'

    def arguments_begin(self, args):
        if args.argument_count() < 1:
            return

        self._body += '<div class="arguments">\n<h2>Arguments:</h2>\n'
        self._body += '<ol>\n'

        for arg in args._elements:
            self._body += u"<li>{0:s}</li>".format(arg.text())

        self._body += '</ol>\n'
        self._body += "</div>\n"

    def header(self):
        res = '<div class="header">\n' \
              '<h1>[{0:s}]</h1>\n' \
              '<div class="description">{0:s}</div>\n' \
              '</div>\n'.format(self._title, self._description)
        return res

    def __str__(self):
        res = '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">\n'
        res += u"<html>\n<head>\n{0:s}</head>\n<body>\n".format(self._head)
        res += self.header()
        res += self._body
        res += self.footer()
        res += "</body>\n</html>\n"

        return res