#!/usr/bin/env python
# coding=utf-8

#   Copyright (C) 2016 by Serge Poltavski                                 #
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

from .idocobjectvisitor import IDocObjectVisitor
from .pd.obj import PdObject


class XletDocVisitor(IDocObjectVisitor):
    def __init__(self, write_to_file=True, add_to_mem_db=True):
        IDocObjectVisitor.__init__(self)
        self._inlet_types = []
        self._outlet_types = []
        self._write_to_file = write_to_file
        self._add_to_mem_db = add_to_mem_db
        self._dynamic_inlets = False
        self._dynamic_outlets = False
        self._aliases = []

    def inlets_begin(self, inlets):
        self._inlet_types = inlets.pd_type_list()
        self._dynamic_inlets = inlets.is_dynamic()

    def alias_begin(self, a):
        self._aliases.append(a)

    def outlets_begin(self, outlets):
        self._outlet_types = outlets.pd_type_list()
        self._dynamic_outlets = outlets.is_dynamic()

    def inlet_types(self):
        if self._dynamic_inlets:
            return [3]  # XLET_IGNORE

        return self._inlet_types

    def outlet_types(self):
        if self._dynamic_outlets:
            return [3]  # XLET_IGNORE

        return self._outlet_types

    @staticmethod
    def as_db_type(xlets):
        if len(xlets) < 1:
            return '-'

        def x_type(x):
            return ('.', '~', '_', '?')[x]

        return ''.join(map(x_type, xlets))

    def names(self):
        return ",".join([self.name] + list(map(lambda a: a.text(), self._aliases)))

    def object_end(self, obj):
        if self._write_to_file:
            fname = "{0}-xlet_db.txt".format(self.name)
            with open(fname, "w") as f:
                f.write("{0}\t\t{1}\t\t{2}\n".format(self.names(),
                                                     self.as_db_type(self.inlet_types()),
                                                     self.as_db_type(self.outlet_types())))

        if self._add_to_mem_db:
            PdObject.add_object_xlet_info(self.name, self.inlet_types(), self.outlet_types())
