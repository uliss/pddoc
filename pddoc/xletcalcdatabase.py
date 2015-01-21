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

        # INLETS
        # MESSAGE
        self._one_msg_inlet = (
            "r~", "receive~", "unpack", "t", "trigger", "outlet"
        )

        self._two_msg_inlet = (
            "route", "bag", "poly",
        )

        self._tree_msg_inlet = (
            "noteout", "ctlout", "polytouchout"
        )
        # SOUND
        self._one_snd_inlet = (
            "s~", "send~", "sin~", "cos~", "q8_sqrt~", "q8_rsqrt~", "wrap~",
            "rfft~", "mtof~", "ftom~", "rmstodb~", "dbtorms~", "outlet~"
        )

        self._two_snd_inlet = (
            "rifft~", "fft~", "ifft~", "framp~"
        )

        # OUTLETS
        # MESSAGE
        self._one_msg_outlet = (
            "pack", "bag"
        )

        self._three_msg_outlet = {
            "poly",
        }

        # SOUND
        self._one_snd_outlet = (
            "sin~", "cos~", "osc~", "r~", "receieve~", "+~", "*~", "-~", "/~",
            "max~", "min~", "clip~", "q8_sqrt~", "q8_rsqrt~", "wrap~", "mtof~",
            "ftom~", "rmstodb~", "dbtorms~"
        )

        self._two_snd_outlet = (
            "fft~", "ifft~", "rfft~", "rifft~", "framp~"
        )

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

        # [osc~]
        if name in ("osc~", ):
            return [self.XLET_SOUND, self.XLET_MESSAGE]

        return self.inlet_conditional(name, nargs)

    def inlet_conditional(self, name, nargs):
        # [s] or [send]
        if name in ("s", "send"):
            if nargs == 0:
                return [self.XLET_MESSAGE] * 2
            else:
                return [self.XLET_MESSAGE]

        # [dac~]
        if name == "dac~":
            if nargs == 0:
                return [self.XLET_SOUND] * 2
            else:
                return [self.XLET_SOUND] * nargs

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

        if name in self._three_msg_outlet:
            return [self.XLET_MESSAGE] * 3

        # 1 snd outlet
        if name in self._one_snd_outlet:
            return [self.XLET_SOUND]

        # 2 snd outlet
        if name in self._two_snd_outlet:
            return [self.XLET_SOUND] * 2

        return self.outlet_conditional(name, nargs)

    def outlet_conditional(self, name, nargs):
        lout_msg = lambda x, func: [self.XLET_MESSAGE] * func(x)

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

        if XletCalcDatabase.re_num.search(name):
            return [self.XLET_MESSAGE]

        return []