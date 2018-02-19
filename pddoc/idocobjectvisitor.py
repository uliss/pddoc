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


class IDocObjectVisitor(object):
    def __init__(self):
        self._name = ""

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, n):
        self._name = n

    def a_begin(self, a):
        pass

    def a_end(self, a):
        pass

    def aliases_begin(self, aliases):
        pass

    def aliases_end(self, aliases):
        pass

    def alias_begin(self, alias):
        pass

    def alias_end(self, alias):
        pass

    def also_begin(self, also):
        pass

    def also_end(self, also):
        pass

    def argument_begin(self, arg):
        pass

    def argument_end(self, arg):
        pass

    def arguments_begin(self, args):
        pass

    def arguments_end(self, args):
        pass

    def author_begin(self, author):
        pass

    def author_end(self, author):
        pass

    def authors_begin(self, authors):
        pass

    def authors_end(self, authors):
        pass

    def category_begin(self, cat):
        pass

    def category_end(self, cat):
        pass

    def col_begin(self, col):
        pass

    def col_end(self, col):
        pass

    def contacts_begin(self, contacts):
        pass

    def contacts_end(self, contacts):
        pass

    def description_begin(self, descr):
        pass

    def description_end(self, descr):
        pass

    def example_begin(self, ex):
        pass

    def example_end(self, ex):
        pass

    def info_begin(self, info):
        pass

    def info_end(self, info):
        pass

    def inlet_begin(self, inlet):
        pass

    def inlet_end(self, inlet):
        pass

    def inlets_begin(self, inlets):
        pass

    def inlets_end(self, inlets):
        pass

    def itemize_begin(self, itemize):
        pass

    def itemize_end(self, itemize):
        pass

    def item_begin(self, item):
        pass

    def item_end(self, item):
        pass

    def keywords_begin(self, kw):
        pass

    def keywords_end(self, kw):
        pass

    def library_begin(self, lib):
        pass

    def library_end(self, lib):
        pass

    def license_begin(self, license):
        pass

    def license_end(self, license):
        pass

    def meta_begin(self, meta):
        pass

    def meta_end(self, meta):
        pass

    def object_begin(self, obj):
        pass

    def object_end(self, obj):
        pass

    def outlet_begin(self, outlet):
        pass

    def outlet_end(self, outlet):
        pass

    def outlets_begin(self, outlets):
        pass

    def outlets_end(self, outlets):
        pass

    def pdascii_begin(self, pdascii):
        pass

    def pdascii_end(self, pdascii):
        pass

    def pdcomment_begin(self, pdcomment):
        pass

    def pdcomment_end(self, pdcomment):
        pass

    def pdconnect_begin(self, pdconn):
        pass

    def pdconnect_end(self, pdconn):
        pass

    def pdexample_begin(self, pdexample):
        pass

    def pdexample_end(self, pdexample):
        pass

    def pdinclude_begin(self, pdinc):
        pass

    def pdinclude_end(self, pdinc):
        pass

    def pdmessage_begin(self, pdmsg):
        pass

    def pdmessage_end(self, pdmsg):
        pass

    def pdobject_begin(self, pdobj):
        pass

    def pdobject_end(self, pdobj):
        pass

    def row_begin(self, row):
        pass

    def row_end(self, row):
        pass

    def see_begin(self, see):
        pass

    def see_end(self, see):
        pass

    def title_begin(self, t):
        pass

    def title_end(self, t):
        pass

    def version_begin(self, v):
        pass

    def version_end(self, v):
        pass

    def website_begin(self, ws):
        pass

    def website_end(self, ws):
        pass

    def xinfo_begin(self, ws):
        pass

    def xinfo_end(self, ws):
        pass

    def since_begin(self, s):
        pass

    def since_end(self, s):
        pass

    def methods_begin(self, m):
        pass

    def methods_end(self, m):
        pass

    def method_begin(self, m):
        pass

    def method_end(self, m):
        pass

    def param_begin(self, p):
        pass

    def param_end(self, p):
        pass

    def par_begin(self, par):
        pass

    def par_end(self, par):
        pass

    def render(self):
        raise NotImplementedError

    def properties_begin(self, p):
        pass

    def properties_end(self, p):
        pass

    def property_begin(self, p):
        pass

    def property_end(self, p):
        pass
