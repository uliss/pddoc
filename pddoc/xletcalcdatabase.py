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
import re
from xlettextdatabase import XletTextDatabase
import os


class XletCalcDatabase(object):
    XLET_MESSAGE = pdobject.PdBaseObject.XLET_MESSAGE
    XLET_SOUND = pdobject.PdBaseObject.XLET_SOUND
    re_num = re.compile(r"^\d+$")

    def __init__(self, dbname=None):
        if not dbname:
            self._dbfile = os.path.dirname(__file__) + '/pd_objects.db'
        else:
            self._dbfile = dbname

        self._dbtxt = XletTextDatabase(self._dbfile)

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
            inlets = list(set(re.findall("(\$[fsiv][0-9])", " ".join(args))))
            if len(inlets) == 0:
                return []
            else:
                inlets.sort(key=lambda x: int(x[2:]))
                res = []
                for i in inlets:
                    if i == "$v1":
                        continue
                    if i[1] == 'v':
                        res.append(self.XLET_SOUND)
                    else:
                        res.append(self.XLET_MESSAGE)
                return res

        def fexpr_tilde_args_parse(args):
            if len(args) == 0:
                return []
            inlets = list(set(re.findall("(\$[fsixy][0-9])", " ".join(args))))
            if len(inlets) == 0:
                return []
            else:
                inlets.sort(key=lambda x: int(x[2:]))
                res = []
                for i in inlets:
                    if i == "$x1":
                        continue
                    if i[1] == 'x':
                        res.append(self.XLET_SOUND)
                    else:
                        res.append(self.XLET_MESSAGE)
                return res

        self._objects = {
            "adc~": (
                lambda args: [self.XLET_MESSAGE],
                lambda args: (2 if len(args) == 0 else len(args)) * [self.XLET_SOUND]
            ),
            "dac~": (
                lambda args: (2 if len(args) == 0 else len(args)) * [self.XLET_SOUND],
                lambda args: []
            ),
            "readsf~": (
                lambda args: [self.XLET_MESSAGE],
                lambda args: (1 if len(args) == 0 else int(args[0])) * [self.XLET_SOUND] + [self.XLET_MESSAGE]
            ),
            "writesf~": (
                lambda args: (1 if len(args) == 0 else int(args[0])) * [self.XLET_SOUND],
                lambda args: []
            ),
            "expr": (
                lambda args: expr_args_parse(args) * [self.XLET_MESSAGE],
                lambda args: [self.XLET_MESSAGE]
            ),
            "expr~": (
                lambda args: [self.XLET_SOUND] + expr_tilde_args_parse(args),
                lambda args: [self.XLET_SOUND]
            ),
            "fexpr~": (
                lambda args: [self.XLET_SOUND] + fexpr_tilde_args_parse(args),
                lambda args: [self.XLET_SOUND]
            )
        }

        # INLETS
        # MESSAGE
        self._one_msg_inlet = (
            "unpack", "t", "trigger", "outlet"
        )

        self._two_msg_inlet = (
            "route",
        )

        self._tree_msg_inlet = (
            "noteout", "ctlout", "polytouchout"
        )
        # SOUND
        self._one_snd_inlet = (
            "s~", "send~", "outlet~"
        )

        self._two_snd_inlet = []

        # OUTLETS
        # MESSAGE
        self._one_msg_outlet = (
            "pack",
        )

        # SOUND
        self._one_snd_outlet = (
            "+~", "*~", "-~", "/~", "max~", "min~"
        )

        self._two_snd_outlet = []

    def inlets(self, obj):
        if not issubclass(obj.__class__, pdobject.PdObject):
            return []

        name = obj.name

        if self._dbtxt.has_object(name):
            return self._dbtxt.inlets(name)

        nargs = obj.num_args()

        # 1 msg inlet
        if name in self._one_msg_inlet:
            return [self.XLET_MESSAGE]

        # 2 msg inlets
        if name in self._two_msg_inlet:
            return [self.XLET_MESSAGE] * 2

        # 3 msg inlets
        if name in self._tree_msg_inlet:
            return [self.XLET_MESSAGE] * 3

        # 1 snd inlet
        if name in self._one_snd_inlet:
            return [self.XLET_SOUND]

        # 2 snd inlet
        if name in self._two_snd_inlet:
            return [self.XLET_SOUND] * 2

        if name in self._objects:
            return self._objects[name][0](obj.args)

        return self.inlet_conditional(name, nargs)

    def inlet_conditional(self, name, nargs):
        # [s] or [send]
        if name in ("s", "send"):
            if nargs == 0:
                return [self.XLET_MESSAGE] * 2
            else:
                return [self.XLET_MESSAGE]

        # 2 sound
        if name in ("*~", "-~", "+~", "/~", "max~", "min~"):
            if nargs == 0:
                return [self.XLET_SOUND] * 2
            else:
                return [self.XLET_SOUND, self.XLET_MESSAGE]

        if name in ("sel", "select", "route"):
            if nargs in (0, 1):
                return [self.XLET_MESSAGE] * 2
            else:
                return [self.XLET_MESSAGE]

        if name in ("pack",):
            if nargs == 0:
                return [self.XLET_MESSAGE] * 2
            else:
                return [self.XLET_MESSAGE] * nargs

        if name == "clip~":
            return [self.XLET_SOUND] + [self.XLET_MESSAGE] * 2

        # digits float object
        if XletCalcDatabase.re_num.search(name):
            return [self.XLET_MESSAGE] * 2

        return []

    def outlets(self, obj):
        name = obj.name
        nargs = obj.num_args()

        if self._dbtxt.has_object(name):
            return self._dbtxt.outlets(name)

        # 1 msg outlet
        if name in self._one_msg_outlet:
            return [self.XLET_MESSAGE]

        # 1 snd outlet
        if name in self._one_snd_outlet:
            return [self.XLET_SOUND]

        # 2 snd outlet
        if name in self._two_snd_outlet:
            return [self.XLET_SOUND] * 2

        if name in self._objects:
            return self._objects[name][1](obj.args)

        return self.outlet_conditional(name, nargs)

    def outlet_conditional(self, name, nargs):
        lout_msg = lambda x, func: [self.XLET_MESSAGE] * func(x)
        lout_snd = lambda x, func: [self.XLET_SOUND] * func(x)

        if name in ("select", "sel", "route"):
            return lout_msg(nargs, lambda x: 2 if x == 0 else x + 1)

        if name in ("unpack", "t", "trigger"):
            return lout_msg(nargs, lambda x: 2 if x == 0 else x)

        if name in ("notein",):
            return lout_msg(nargs, lambda x: 3 if x == 0 else 2)

        if name in ("ctlin",):
            return lout_msg(nargs, lambda x: 3 if x == 0 else 2 if x == 1 else 1)

        if name in ("pgmin", "bendin", "touchin"):
            return lout_msg(nargs, lambda x: 2 if x == 0 else 1)

        if name in ("polytouchin",):
            return lout_msg(nargs, lambda x: 3 if x == 0 else 2)

        # digits float creation
        if XletCalcDatabase.re_num.search(name):
            return [self.XLET_MESSAGE]

        return []