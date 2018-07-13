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

import logging
import re

from . import XLET_MESSAGE, XLET_SOUND, XLET_IGNORE
from .xletdatabase import XletDatabase


class XletTextDatabase(XletDatabase):
    def __init__(self, fname, extname):
        super(XletTextDatabase, self).__init__(extname)
        self._extname = extname
        self._fname = None
        self._objects = {}
        if fname:
            self.load(fname)

    def has_object(self, objname):
        return objname in self._objects

    def load(self, fname):
        self._fname = fname
        try:
            f = open(fname, "r")
            lines = f.readlines()
            for line in lines:
                self.parse(line)

        except IOError as e:
            logging.error("Load failed: {0:s}".format(fname))
            raise e

    def ignore_inlets(self, objname):
        if not self.has_object(objname):
            return False
        else:
            return XLET_IGNORE in self._objects[objname][0]

    def ignore_outlets(self, objname):
        if not self.has_object(objname):
            return False
        else:
            return XLET_IGNORE in self._objects[objname][1]

    def inlets(self, objname, args=None):
        if not self.has_object(objname):
            return []

        return self._objects[objname][0]

    def outlets(self, objname, args=None):
        if not self.has_object(objname):
            return []

        return self._objects[objname][1]

    def parse(self, line):
        if line and line[0] == "#":  # comment
            return

        atoms = re.split("\s+", line)

        if len(atoms) < 3:
            logging.error("line skip: " + line)
            return

        def parse_xlet(data_str):
            res = []
            if data_str[0] == '-':
                return res

            for char in data_str:
                if char == "~":
                    res.append(XLET_SOUND)
                elif char == ".":
                    res.append(XLET_MESSAGE)
                elif char == '?':
                    res.append(XLET_IGNORE)
                else:
                    logging.error("unknown char in inlet definition")

            return res

        objects = atoms[0].split(",")
        inl = parse_xlet(atoms[1])
        outl = parse_xlet(atoms[2])

        for obj in objects:
            if obj in self._objects:
                logging.warning("object [{0:s}] already exists in database".format(obj))
            self._objects[obj] = (inl, outl)

    def __str__(self):
        return str(self._objects)
