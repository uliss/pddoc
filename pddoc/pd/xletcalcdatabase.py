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

import imp
import logging

from .xletdatabase import XletDatabase


class XletCalcDatabase(XletDatabase):
    _counter = 0

    def __init__(self, path, extname):
        super(XletCalcDatabase, self).__init__(extname)
        self._extname = extname
        XletCalcDatabase._counter += 1
        self._module = None

        try:
            self._module = imp.load_source("plugin{0:d}".format(XletCalcDatabase._counter), path)
        except IOError as e:
            logging.error("Plugin not found: {0:s}".format(path))
            raise e

    def outlets(self, name, args=None):
        if args is None:
            args = []
        return self._module.outlets(name, args)

    def inlets(self, name, args=None):
        if args is None:
            args = []
        return self._module.inlets(name, args)

    def has_object(self, name):
        return self._module.has_object(name)
