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

from .xletdatabase import XletDatabase
import os
import re
import logging

from . import XLET_MESSAGE, XLET_SOUND


class ObjectRecord(object):
    def __init__(self, path, inlets=None, outlets=None):
        self._path = path
        self._inlets = inlets
        self._outlets = outlets

    @property
    def inlets(self):
        return self._inlets

    @inlets.setter
    def inlets(self, inlets):
        self._inlets = inlets

    @property
    def outlets(self):
        return self._outlets

    @outlets.setter
    def outlets(self, outlets):
        self._outlets = outlets

    @property
    def path(self):
        return self._path

    def no_info(self):
        return self._inlets is None or self._outlets is None

    def __str__(self):
        return "Object: {0:s}\n\tinlets: {1:s}\n\toutlets: {2:s}".format(self._path, self._inlets, self._outlets)


class XletPatchLookup(XletDatabase):
    lines_re = re.compile("(#(.*?)[^\\\])\r?\n?;\r?\n", re.MULTILINE | re.DOTALL)
    split_re = re.compile(" |\r\n?|\n", re.MULTILINE)

    def __init__(self, dirs=None):
        XletDatabase.__init__(self, "pdpatch")
        if dirs is None:
            dirs = []
        self._dirs = dirs
        self._dirs.append(os.getcwd())
        self._cache = {}

    def clean_name(self, name):
        return re.sub("/[\W]+/", '', name) + ".pd"

    def get_object(self, name):
        cleanName = self.clean_name(name)
        return self._cache.get(cleanName)

    def has_object(self, name):
        cleanName = self.clean_name(name)

        if cleanName in self._cache:
            return True

        for directory in self._dirs:
            path = os.path.join(directory, cleanName)
            if os.path.exists(path):
                self._cache[cleanName] = ObjectRecord(path)
                return True

        return False

    def inlets(self, name, args=None):
        if args is None:
            args = []
        cname = self.clean_name(name)
        if cname not in self._cache:
            return []

        if self._cache[cname].no_info():
            self.calc_xlets(cname)

        return self._cache[cname].inlets

    def outlets(self, name, args=None):
        if args is None:
            args = []
        cname = self.clean_name(name)
        if cname not in self._cache:
            return []

        if self._cache[cname].no_info():
            self.calc_xlets(cname)

        return self._cache[cname].outlets

    def calc_xlets(self, cname):
        assert cname in self._cache
        object_info = self._cache[cname]
        # assert isinstance(object_info, ObjectRecord)
        inlets_coords = []
        outlets_coords = []

        try:
            f = open(object_info.path, 'r')

            lines = f.read()
            subpatch_counter = -1
            for found in self.lines_re.finditer(lines):
                line = found.group(1)
                atoms = self.split_re.split(line)

                if atoms[0] == "#N" and atoms[1] == "canvas":
                    subpatch_counter += 1

                if subpatch_counter == 0:
                    if atoms[1] == "obj":
                        x = lambda: int(atoms[2])
                        if atoms[4] == "inlet":
                            inlets_coords.append((XLET_MESSAGE, x()))
                        if atoms[4] == "inlet~":
                            inlets_coords.append((XLET_SOUND, x()))
                        if atoms[4] == "outlet":
                            outlets_coords.append((XLET_MESSAGE, x()))
                        if atoms[4] == "outlet~":
                            outlets_coords.append((XLET_SOUND, x()))

                if atoms[0] == "#X" and atoms[1] == "restore":
                    subpatch_counter -= 1

        except IOError:
            logging.error("can't open file: {0:s}".format(object_info.path))

        inlets_coords.sort(key=lambda el: el[1])
        outlets_coords.sort(key=lambda el: el[1])
        object_info.inlets = [k for k, v in inlets_coords]
        object_info.outlets = [k for k, v in outlets_coords]
