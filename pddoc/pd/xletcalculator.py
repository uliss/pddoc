#!/usr/bin/env python
# coding=utf-8

# Copyright (C) 2014 by Serge Poltavski                                 #
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

from .xlettextdatabase import XletTextDatabase
from .xletcalcdatabase import XletCalcDatabase
from .xletdatabase import XletMemoryDatabase
from .xletpatchlookup import XletPatchLookup
from . import EXTERNALS_DIR
import os


class XletCalculator(object):
    def __init__(self, dbname=None):
        ext_dir = EXTERNALS_DIR

        self.mem_db = XletMemoryDatabase("default_memory")

        self._dbs = [self.mem_db]
        self._dbs.append(XletTextDatabase(os.path.join(ext_dir, 'core/pd_objects.db'), "core"))
        self._dbs.append(XletCalcDatabase(os.path.join(ext_dir, 'core/xletsdb_core.py'), "core"))
        self._dbs.append(XletCalcDatabase(os.path.join(ext_dir, 'ceammc/xletsdb.py'), "ceammc"))

        for paths in os.walk(ext_dir):
            for text_db in [f for f in paths[2] if f.endswith(".db")]:
                extname = os.path.basename(paths[0])
                txt_db = XletTextDatabase(os.path.join(paths[0], text_db), extname)
                self._dbs.append(txt_db)

            for calc_db in [f for f in paths[2] if f == "xletsdb.py"]:
                calc_db = XletCalcDatabase(os.path.join(paths[0], calc_db), extname)
                self._dbs.append(calc_db)

        self._dbs.append(XletPatchLookup())

    def add_db(self, path, name='user'):
        self._dbs.append(XletTextDatabase(path, name))

    def has_ext_prefix(self, obj):
        return "/" in obj.name and obj.name not in ("/", "/~")

    def inlets(self, obj):
        from .obj import PdObject
        if not issubclass(obj.__class__, PdObject):
            return []

        if self.has_ext_prefix(obj):
            ext, name = obj.name.split("/")[:2]
            return self.search_in_named_ext(ext, name, obj.args)[0]

        return self.inlets_by_name(obj.name, obj.args)

    def inlets_by_name(self, name, args=None):
        for db in self._dbs:
            if db.has_object(name):
                return db.inlets(name, args)
        return []

    def outlets(self, obj):
        from .obj import PdObject
        if not issubclass(obj.__class__, PdObject):
            return []

        if self.has_ext_prefix(obj):
            ext, name = obj.name.split("/")[:2]
            return self.search_in_named_ext(ext, name, obj.args)[1]

        return self.outlets_by_name(obj.name, obj.args)

    def outlets_by_name(self, name, args=None):
        for db in self._dbs:
            if db.has_object(name):
                return db.outlets(name, args)

        return []

    def search_in_named_ext(self, extname, name, args):
        for db in self._dbs:
            if db.extname != extname:
                continue

            if db.has_object(name):
                return db.inlets(name, args), db.outlets(name, args)

        return [], []
