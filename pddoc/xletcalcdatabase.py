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


class XletCalcDatabase(object):
    XLET_MESSAGE = pdobject.PdBaseObject.XLET_MESSAGE
    XLET_SOUND = pdobject.PdBaseObject.XLET_SOUND

    re_num = re.compile(r"^\d+$")

    def __init__(self):
        # INLETS
        # MESSAGE
        self._one_msg_inlet = (
            "bang", "b", "change", "makefilename", "print",
            "mtof", "ftom", "powtodb", "dbtopow", "rmstodb", "dbtorms",
            "sin", "cos", "tan", "atan", "atan2", "sqrt", "log", "exp", "abs",
            "loadbang", "bang~",
            "r~", "receive~", "unpack", "value", "v", "t", "trigger",
            "tabread", "tabread4", "soundfiler", "netsend", "qlist",
            "textfile", "openpanel", "savepanel", "init", "outlet"
        )

        self._two_msg_inlet = (
            "pipe", "i", "int", "float", "f", "symbol",
            "+", "-", "*", "/", "pow", "%",
            "==", "!=", "<", ">", ">=", "<=",
            "&", "&&", "|", "||", "mod", "div", "min", "max",
            "route", "spigot", "moses", "until", "swap", "delay", "del", "metro",
            "timer", "cputime", "realtime", "random", "pgmout", "bendout",
            "touchout", "midiout", "stripnote", "tabwrite", "bag", "poly",
        )

        self._tree_msg_inlet = (
            "clip", "line", "noteout", "ctlout", "polytouchout", "makenote"
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
            "bang", "b", "float", "f", "int", "i", "symbol", "receive", "r",
            "change", "makefilename", "pipe", "+", "-", "*", "/", "%", "pow",
            "==", "!=", "<", ">", ">=", "<=", "&", "&&", "|", "||", "mtof",
            "ftom", "powtodb", "dbtopow", "rmstodb", "dbtorms",
            "sin", "cos", "tan", "atan", "atan2", "sqrt", "log", "exp", "abs",
            "random", "mod", "div", "min", "max", "clip", "loadbang", "bang~",
            "pack", "spigot", "until", "value", "v", "line", "delay", "del",
            "metro", "timer", "cputime", "realtime", "tabread", "tabread4",
            "soundfiler", "netsend", "openpanel", "savepanel", "bag", "key",
            "keyup", "init"
        )

        self._two_msg_outlet = (
            "moses", "swap", "sysexin", "midiin", "makenote", "stripnote",
            "netreceive", "qlist", "textfile", "keyname"
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

        # 1 msg outlet
        if name in self._one_msg_outlet:
            return [self.XLET_MESSAGE]

        # 2 msg outlet
        if name in self._two_msg_outlet:
            return [self.XLET_MESSAGE] * 2

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