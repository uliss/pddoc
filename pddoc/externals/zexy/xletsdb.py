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


XLET_MESSAGE = 0
XLET_SOUND = 1


_objects = {
    "mux~": (
        lambda args: (2 if not args else len(args)) * [XLET_SOUND],
        lambda args: [XLET_SOUND]
    )
}


def has_object(name):
    return name in _objects


def inlets(name, args):
    if name in ("mux~", "multiplex~"):
        return _objects["mux~"][0](args)

    return []


def outlets(name, args):
    if name in ("mux~", "multiplex~"):
        return _objects["mux~"][1](args)

    return []