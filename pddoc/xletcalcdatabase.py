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
        self._dbs = []

        for paths in os.walk(os.path.dirname(__file__) + "/externals"):
            for db in [f for f in paths[2] if f.endswith(".db")]:
                self._dbs.append(XletTextDatabase(paths[0] + "/" + db))

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
            ),
            "sprintf": (
                lambda args: (1 if not len(args) else len([a for a in args if a[0] == "%" and a[0:2] != "%%"])) * [self.XLET_MESSAGE],
                lambda args: [self.XLET_MESSAGE]
            ),
            "select": (
                lambda args: (2 if len(args) < 2 else 1) * [self.XLET_MESSAGE],
                lambda args: (2 if len(args) == 0 else len(args) + 1) * [self.XLET_MESSAGE]
            ),
            "sel": (
                lambda args: (2 if len(args) < 2 else 1) * [self.XLET_MESSAGE],
                lambda args: (2 if len(args) == 0 else len(args) + 1) * [self.XLET_MESSAGE]
            ),
            "route": (
                lambda args: (2 if len(args) < 2 else 1) * [self.XLET_MESSAGE],
                lambda args: (2 if len(args) == 0 else len(args) + 1) * [self.XLET_MESSAGE]
            ),
            "send": (
                lambda args: (2 if not args else 1) * [self.XLET_MESSAGE],
                lambda args: []
            ),
            "s": (
                lambda args: (2 if not args else 1) * [self.XLET_MESSAGE],
                lambda args: []
            ),
            "pack": (
                lambda args: (2 if len(args) == 0 else len(args)) * [self.XLET_MESSAGE],
                lambda args: [self.XLET_MESSAGE]
            ),
            "unpack": (
                lambda args: [self.XLET_MESSAGE],
                lambda args: (2 if len(args) == 0 else len(args)) * [self.XLET_MESSAGE]
            ),
            "trigger": (
                lambda args: [self.XLET_MESSAGE],
                lambda args: (2 if len(args) == 0 else len(args)) * [self.XLET_MESSAGE]
            ),
            "t": (
                lambda args: [self.XLET_MESSAGE],
                lambda args: (2 if len(args) == 0 else len(args)) * [self.XLET_MESSAGE]
            ),
            "notein": (
                lambda args: [],
                lambda args: (3 if len(args) == 0 else 2) * [self.XLET_MESSAGE]
            ),
            "ctlin": (
                lambda args: [],
                lambda args: (3 if len(args) == 0 else 2 if len(args) == 1 else 1) * [self.XLET_MESSAGE]
            ),
            "pgmin": (
                lambda args: [],
                lambda args: (2 if len(args) == 0 else 1) * [self.XLET_MESSAGE]
            ),
            "bendin": (
                lambda args: [],
                lambda args: (2 if len(args) == 0 else 1) * [self.XLET_MESSAGE]
            ),
            "touchin": (
                lambda args: [],
                lambda args: (2 if len(args) == 0 else 1) * [self.XLET_MESSAGE]
            ),
            "polytouchin": (
                lambda args: [],
                lambda args: (3 if len(args) == 0 else 2) * [self.XLET_MESSAGE]
            )
        }

        # OUTLETS
        # SOUND
        self._one_snd_outlet = (
            "+~", "*~", "-~", "/~", "max~", "min~"
        )

    def inlets(self, obj):
        if not issubclass(obj.__class__, pdobject.PdObject):
            return []

        name = obj.name

        if self._dbtxt.has_object(name):
            return self._dbtxt.inlets(name)

        nargs = obj.num_args()

        if name in self._objects:
            return self._objects[name][0](obj.args)

        return self.inlet_conditional(name, nargs)

    def inlet_conditional(self, name, nargs):
        # 2 sound
        if name in ("*~", "-~", "+~", "/~", "max~", "min~"):
            if nargs == 0:
                return [self.XLET_SOUND] * 2
            else:
                return [self.XLET_SOUND, self.XLET_MESSAGE]

        # digits float object [2], [3] and others
        if XletCalcDatabase.re_num.search(name):
            return [self.XLET_MESSAGE] * 2

        return self.search_in_extdb(name, True)

    def outlets(self, obj):
        name = obj.name
        nargs = obj.num_args()

        if self._dbtxt.has_object(name):
            return self._dbtxt.outlets(name)

        # 1 snd outlet
        if name in self._one_snd_outlet:
            return [self.XLET_SOUND]

        if name in self._objects:
            return self._objects[name][1](obj.args)

        return self.outlet_conditional(name, nargs)

    def outlet_conditional(self, name, nargs):
        # digits float creation
        if XletCalcDatabase.re_num.search(name):
            return [self.XLET_MESSAGE]

        return self.search_in_extdb(name, False)

    def search_in_extdb(self, name, inlets=True):
        for db in self._dbs:
            if db.has_object(name):
                if inlets:
                    return db.inlets(name)
                else:
                    return db.outlets(name)

        return []