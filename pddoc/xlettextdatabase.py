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
from pdbaseobject import PdBaseObject


class XletTextDatabase(object):
    def __init__(self, fname=None):
        self._fname = ""
        self._objects = {}
        if fname:
            self.load(fname)

    def load(self, fname):
        self._fname = fname
        try:
            f = open(fname, "r")
            lines = f.readlines()
            for line in lines:
                self.parse(line)

        except IOError, e:
            logging.error(e.message)
            raise e

    def parse(self, line):
        atoms = line.split(" ")
        if len(atoms) < 3:
            logging.error("line skip: " + line)
            return

        def parse_xlet(line):
            res = []
            if line[0] == '-':
                return res

            for char in line:
                if char == "~":
                    res.append(PdBaseObject.XLET_SOUND)
                elif char == ".":
                    res.append(PdBaseObject.XLET_MESSAGE)
                else:
                    logging.error("unknown char in inlet definition")

            return res

        obj = atoms[0]
        inl = parse_xlet(atoms[1])
        outl = parse_xlet(atoms[2])

        self._objects[obj] = (inl, outl)

    def __str__(self):
        return str(self._objects)


