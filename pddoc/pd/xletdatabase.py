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


class XletDatabase(object):
    def __init__(self, extname=None):
        self._extname = extname

    def has_object(self, name):
        return False

    def ignore_inlets(self, objname):
        return False

    def ignore_outlets(self, objname):
        return False

    def inlets(self, name, args=None):
        if args is None:
            args = []
        return []

    def outlets(self, name, args=None):
        if args is None:
            args = []
        return []

    @property
    def extname(self):
        return self._extname


class XletMemoryDatabase(XletDatabase):
    def __init__(self, extname):
        super(XletMemoryDatabase, self).__init__(extname)
        self._extname = extname
        self._objects = {}

    def has_object(self, objname):
        return objname in self._objects

    def inlets(self, objname, args=None):
        if args is None:
            args = []
        if not self.has_object(objname):
            return []

        return self._objects[objname][0]

    def outlets(self, objname, args=None):
        if args is None:
            args = []
        if not self.has_object(objname):
            return []

        return self._objects[objname][1]

    def add_object(self, name, inlets, outlets):
        self._objects[name] = (inlets, outlets)

    def remove_object(self, name):
        del self._objects[name]

    def set_inlets(self, name, inlets):
        self._objects[name][0] = inlets

    def set_outlets(self, name, outlets):
        self._objects[name][1] = outlets
