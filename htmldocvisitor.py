# /usr/bin/env python

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


# -*- coding: utf-8 -*-

__author__ = 'Serge Poltavski'



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

    def title_begin(self, t):
        self._title = t.text()
        self._head += "<title>PureData [%s] object</title>\n" % (self._title)

    def website_begin(self, w):
        self._website = w.text()

    def object_begin(self, obj):
        self._head += '<meta http-equiv="Content-Type" content="text/html; charset=utf-8">\n'
        self._head += '<link rel="stylesheet" type="text/css" href="theme.css">\n'

    def keywords_begin(self, k):
        self._keywords = k.keywords()
        self._head += '<meta name="keywords" content="%s">\n' % (" ".join(self._keywords))

    def description_begin(self, d):
        self._description = d.text()
        self._head += '<meta name="description" content="%s">\n' % (self._description)

    def version_begin(self, v):
        self._version = v.text()

    def footer(self):
        res = '<div class="footer">version: %s</div>\n' % (self._version)
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
        return '<a href="http://puredata.info/wiki/%s.html">%s</a>' % (t, t)

    def process_xlets(self, xlets):
        for xlet_number in sorted(xlets):
            xlet_list = xlets[xlet_number]
            col_span = len(xlet_list)
            xlet_list_count = col_span

            for xl in xlet_list:
                self._body += "<tr>\n"
                if col_span == xlet_list_count:
                    self._body += "<td rowspan=\"%s\" class=\"number\"><span>%s</span></td>\n" % (col_span, xlet_number)

                self._body += "<td class=\"type\">%s</td>\n" % (self.core_type_help(xl.type()))
                range_str = lambda x: ("&ndash;".join(map(str, x))) if (len(x) > 1) else "&nbsp;"
                self._body += "<td class=\"range\">%s</td>\n" % (range_str(xl.range()))
                self._body += "<td class=\"description\">%s</td>\n" % (xl.text())
                self._body += "</tr>\n"
                col_span -= 1

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
            self._body += '<li>%s</li>' % (arg.text())

        self._body += '</ol>\n'
        self._body += "</div>\n"

    def header(self):
        res = '<div class="header">\n' \
              '<h1>[%s]</h1>\n' \
              '<div class="description">%s</div>\n' \
              '</div>\n' % (self._title, self._description)
        return res

    def __str__(self):
        res = '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">\n'
        res += "<html>\n<head>\n%s</head>\n<body>\n" % (self._head)
        res += self.header()
        res += self._body
        res += self.footer()
        res += "</body>\n</html>\n"

        return res




