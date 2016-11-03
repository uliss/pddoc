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

from pddoc.pd import XLET_SOUND, XLET_MESSAGE


_objects = {
    "mux~": (
        lambda args: (2 if not args else len(args)) * [XLET_SOUND],
        lambda args: [XLET_SOUND]
    ),
    "multiplex~": (
        lambda args: (2 if not args else len(args)) * [XLET_SOUND],
        lambda args: [XLET_SOUND]
    ),
    "mux": (
        lambda args: (3 if len(args) < 3 else len(args) + 1) * [XLET_MESSAGE],
        lambda args: [XLET_MESSAGE]
    ),
    "multiplex": (
        lambda args: (3 if len(args) < 3 else len(args) + 1) * [XLET_MESSAGE],
        lambda args: [XLET_MESSAGE]
    ),
    "demux": (
        lambda args: 2 * [XLET_MESSAGE],
        lambda args: (2 if len(args) < 3 else len(args)) * [XLET_MESSAGE]
    ),
    "demultiplex": (
        lambda args: 2 * [XLET_MESSAGE],
        lambda args: (2 if len(args) < 3 else len(args)) * [XLET_MESSAGE]
    ),
    "demultiplex~": (
        lambda args: [XLET_SOUND],
        lambda args: (2 if not args else len(args)) * [XLET_SOUND]
    ),
    "demux~": (
        lambda args: [XLET_SOUND],
        lambda args: (2 if not args else len(args)) * [XLET_SOUND]
    ),
    "limiter~": (
        lambda args: (1 if not args else len(args)) * [XLET_SOUND],
        lambda args: [XLET_SOUND]
    )
}


def has_object(name):
    return name in _objects


def inlets(name, args):
    if name in _objects:
        return _objects[name][0](args)

    return []


def outlets(name, args):
    if name in _objects:
        return _objects[name][1](args)

    return []