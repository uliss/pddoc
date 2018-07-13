#!/usr/bin/env python
# coding=utf-8

# Copyright (C) 2015 by Serge Poltavski                                 #
# serge.poltavski@gmail.com                                             #
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

import re
from pddoc.pd import XLET_MESSAGE, XLET_SOUND


def expr_args_parse(args):
    if len(args) == 0:
        return 1
    params = list(set(re.findall("(\$[fsi][0-9])", " ".join(args))))
    if len(params) == 0:
        return 1
    else:
        return int(max(params, key=lambda x: int(x[2]))[2])


def expr_tilde_args_parse(args):
    if len(args) == 0:
        return []
    inl = list(set(re.findall("(\$[fsiv][0-9])", " ".join(args))))
    if len(inl) == 0:
        return []
    else:
        inl.sort(key=lambda x: int(x[2:]))
        res = []
        for i in inl:
            if i == "$v1":
                continue
            if i[1] == 'v':
                res.append(XLET_SOUND)
            else:
                res.append(XLET_MESSAGE)
        return res


def func_list_in(args):
    if not args:
        return 2
    if args[0] in ("trim", "length"):
        return 1
    else:
        return 2


def func_list_out(args):
    if not args:
        return 1
    if args[0] == "split":
        return 3
    else:
        return 1


def fexpr_tilde_args_parse(args):
    if len(args) == 0:
        return []
    inl = list(set(re.findall("(\$[fsixy][0-9])", " ".join(args))))
    if len(inl) == 0:
        return []
    else:
        inl.sort(key=lambda x: int(x[2:]))
        res = []
        for i in inl:
            if i == "$x1":
                continue
            if i[1] == 'x':
                res.append(XLET_SOUND)
            else:
                res.append(XLET_MESSAGE)
        return res

_re_num = re.compile(r"^\d+$")

_objects = {
    "adc~": (
        lambda args: [XLET_MESSAGE],
        lambda args: (2 if len(args) == 0 else len(args)) * [XLET_SOUND]
    ),
    "dac~": (
        lambda args: (2 if len(args) == 0 else len(args)) * [XLET_SOUND],
        lambda args: []
    ),
    "readsf~": (
        lambda args: [XLET_MESSAGE],
        lambda args: (1 if len(args) == 0 else int(args[0])) * [XLET_SOUND] + [XLET_MESSAGE]
    ),
    "writesf~": (
        lambda args: (1 if len(args) == 0 else int(args[0])) * [XLET_SOUND],
        lambda args: []
    ),
    "expr": (
        lambda args: expr_args_parse(args) * [XLET_MESSAGE],
        lambda args: len(list(filter(None, " ".join(args).split(";")))) * [XLET_MESSAGE]
    ),
    "expr~": (
        lambda args: [XLET_SOUND] + expr_tilde_args_parse(args),
        lambda args: [XLET_SOUND]
    ),
    "fexpr~": (
        lambda args: [XLET_SOUND] + fexpr_tilde_args_parse(args),
        lambda args: [XLET_SOUND]
    ),
    "sprintf": (
        lambda args: (1 if not len(args) else (len(" ".join(args).replace("%%", "").split("%")) - 1)) * [
            XLET_MESSAGE],
        lambda args: (1 if " ".join(args).replace("%%", "").count("%") > 0 else 0) * [XLET_MESSAGE]
    ),
    "select": (
        lambda args: (2 if len(args) < 2 else 1) * [XLET_MESSAGE],
        lambda args: (2 if len(args) == 0 else len(args) + 1) * [XLET_MESSAGE]
    ),
    "sel": (
        lambda args: (2 if len(args) < 2 else 1) * [XLET_MESSAGE],
        lambda args: (2 if len(args) == 0 else len(args) + 1) * [XLET_MESSAGE]
    ),
    "route": (
        lambda args: (2 if len(args) < 2 else 1) * [XLET_MESSAGE],
        lambda args: (2 if len(args) == 0 else len(args) + 1) * [XLET_MESSAGE]
    ),
    "send": (
        lambda args: (2 if not args else 1) * [XLET_MESSAGE],
        lambda args: []
    ),
    "s": (
        lambda args: (2 if not args else 1) * [XLET_MESSAGE],
        lambda args: []
    ),
    "pointer": (
        lambda args: 2 * [XLET_MESSAGE],
        lambda args: (len(args) + 2) * [XLET_MESSAGE]
    ),
    "pack": (
        lambda args: (2 if len(args) == 0 else len(args)) * [XLET_MESSAGE],
        lambda args: [XLET_MESSAGE]
    ),
    "unpack": (
        lambda args: [XLET_MESSAGE],
        lambda args: (2 if len(args) == 0 else len(args)) * [XLET_MESSAGE]
    ),
    "trigger": (
        lambda args: [XLET_MESSAGE],
        lambda args: (2 if len(args) == 0 else len(args)) * [XLET_MESSAGE]
    ),
    "t": (
        lambda args: [XLET_MESSAGE],
        lambda args: (2 if len(args) == 0 else len(args)) * [XLET_MESSAGE]
    ),
    "notein": (
        lambda args: [],
        lambda args: (3 if len(args) == 0 else 2) * [XLET_MESSAGE]
    ),
    "ctlin": (
        lambda args: [],
        lambda args: (3 if len(args) == 0 else 2 if len(args) == 1 else 1) * [XLET_MESSAGE]
    ),
    "pgmin": (
        lambda args: [],
        lambda args: (2 if len(args) == 0 else 1) * [XLET_MESSAGE]
    ),
    "bendin": (
        lambda args: [],
        lambda args: (2 if len(args) == 0 else 1) * [XLET_MESSAGE]
    ),
    "touchin": (
        lambda args: [],
        lambda args: (2 if len(args) == 0 else 1) * [XLET_MESSAGE]
    ),
    "polytouchin": (
        lambda args: [],
        lambda args: (3 if len(args) == 0 else 2) * [XLET_MESSAGE]
    ),
    "list": (
        lambda args: func_list_in(args) * [XLET_MESSAGE],
        lambda args: func_list_out(args) * [XLET_MESSAGE]
    )
}


def is_snd_math(name):
    return name in ("+~", "*~", "-~", "/~", "max~", "min~")


def is_digit_object(name):
    return _re_num.search(name)


def inlets(name, args):
    # digits float object [2], [3] and others
    if is_digit_object(name):
        return [XLET_MESSAGE]

    if is_snd_math(name):

        if len(args) == 0:
            return [XLET_SOUND] * 2
        else:
            return [XLET_SOUND, XLET_MESSAGE]

    if name in _objects:
        return _objects[name][0](args)

    return []


def outlets(name, args):
    # digits float object [2], [3] and others
    if is_digit_object(name):
        return [XLET_MESSAGE] * 2

    if is_snd_math(name):
        return [XLET_SOUND]

    if name in _objects:
        return _objects[name][1](args)

    return []


def has_object(name):
    if is_snd_math(name) or is_digit_object(name):
        return True

    return name in _objects