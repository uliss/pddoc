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

from pddoc.pd import XLET_MESSAGE, XLET_SOUND
from functools import reduce


def find_prop_idx(args):
    idx = 0
    for arg in args:
        if arg[0] == '@':
            return idx

        idx += 1

    return -1


def ceammc_parse_props(args):
    res = {}
    last_key = None
    for arg in args:
        if arg[0] == '@':
            res[arg] = list()
            last_key = arg
        else:
            res[last_key].append(arg)

    for k, v in res:
        if len(v) == 1:
            v = v[0]

    return res


def ceammc_parse_args(args):
    prop_args = {}
    pos_args = []

    prop_idx = find_prop_idx(args)

    if prop_idx == -1:
        return args, prop_args
    else:
        pos_args = args[0:prop_idx]
        prop_args = ceammc_parse_props(args[prop_idx:])
        return pos_args, prop_args


def hoa_get_prop(args, key, pos_idx, default):
    if len(args) < 1:
        return default

    pos, props = ceammc_parse_args(args)
    if len(pos) > pos_idx:
        return pos[pos_idx]

    return props.get(key, default)


_objects = {
    "prop->": (
        lambda args: [XLET_MESSAGE],
        lambda args: (len(args) + 2) * [XLET_MESSAGE]
    ),
    "flow.sync": (
        lambda args: 2 if len(args) < 1 else int(args[0]) * [XLET_MESSAGE],
        lambda args: 2 if len(args) < 1 else int(args[0]) * [XLET_MESSAGE]
    ),
    "xdac~": (
        lambda args: 2 if len(args) < 1 else reduce(lambda a, b: int(b) - int(a), args[0].split(':')) * [XLET_SOUND],
        lambda args: []
    ),
    "hoa.2d.encoder~": (
        lambda args: 2 * [XLET_SOUND],
        lambda args: 7 if len(args) < 1 else (2 * int(args[0]) + 1) * [XLET_SOUND]
    ),
    # "hoa.2d.decoder": (
    #     lambda args: (hoa_get_prop(args, "@order", 0, 7) * 2 + 1) * [XLET_SOUND],
    #     lambda args: (hoa_get_prop(args, "@order", 0, 7) * 2 + 1) * [XLET_SOUND],
    # )
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
