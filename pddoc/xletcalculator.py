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

import pdobject
from xlettextdatabase import XletTextDatabase
from xletcalcdatabase import XletCalcDatabase
import os


class XletCalculator(object):
    def __init__(self, dbname=None):
        if not dbname:
            self._dbfile = os.path.dirname(__file__) + '/pd_objects.db'
        else:
            self._dbfile = dbname

        self._dbs = []
        self._dbs.append(XletTextDatabase(self._dbfile))

        for paths in os.walk(os.path.dirname(__file__) + "/externals"):
            for db in [f for f in paths[2] if f.endswith(".db")]:
                self._dbs.append(XletTextDatabase(paths[0] + "/" + db))

        for paths in os.walk(os.path.dirname(__file__) + "/externals"):
            for db in [f for f in paths[2] if f == "xletsdb.py"]:
                self._dbs.append(XletCalcDatabase(paths[0] + "/" + db))

    def inlets(self, obj):
        if not issubclass(obj.__class__, pdobject.PdObject):
            return []

        for db in self._dbs:
            if db.has_object(obj.name):
                return db.inlets(obj.name, obj.args)

        return []

    def outlets(self, obj):
        if not issubclass(obj.__class__, pdobject.PdObject):
            return []

        for db in self._dbs:
            if db.has_object(obj.name):
                return db.outlets(obj.name, obj.args)

        return []