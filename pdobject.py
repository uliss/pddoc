# /usr/bin/env python

#   Copyright (C) 2014 by Serge Poltavski                                 #
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


# -*- coding: utf-8 -*-

__author__ = 'Serge Poltavski'

import re
from pdbaseobject import *

class PdObject(PdBaseObject):
    def __init__(self, x, y, w, h, args):
        super(PdObject, self).__init__(x, y, w, h)
        self.id = -1
        self.args = args
        self.connected_objects = []

    def is_connected(self, obj):
        assert issubclass(obj.__class__, self.__class__)

        if obj in self.connected_objects:
            return True
        return False

    def connect_to(self, obj):
        assert issubclass(obj.__class__, self.__class__)

        if not self.is_connected(obj):
            self.connect_to(obj)

        if not obj.is_connected(self):
            obj.connect_to(self)

    def to_string(self):
        res = ""

        esc_args = []
        for arg in self.args:
            esc_args.append(re.sub(r'\\(.)', r'\1', arg))

        for arg in esc_args:
            if arg == ",":
                res += ", "
            elif arg == ";":
                res += ";"
            else:
                res += " " + arg

        res = " ".join(res.strip().split())
        return res

    def __str__(self):
        res = "[%-40s {x:%i,y:%i,id:%i}" %(" ".join(self.args) + "]", self.x, self.y, self.id)
        return res

    def draw(self, painter):
        painter.draw_object(self)

    def name(self):
        return self.args[0]

    def inlets(self):
        # [b] or [bang]
        if self.name() in ("bang", "b"):
            return [self.XLET_MESSAGE]

        # [f] or [float]
        if self.name() in ("float", "f"):
            return [self.XLET_MESSAGE, self.XLET_MESSAGE]

        # [s] or [send]
        if self.name() in ("s", "send"):
            if len(self.args) > 1:
                return [self.XLET_MESSAGE]
            else:
                return [self.XLET_MESSAGE, self.XLET_MESSAGE]

        # [s~] or [send~]
        if self.name() in ("s~", "send~"):
            return [self.XLET_SOUND]

        # [r~] or [receive~]
        if self.name() in ("r~", "receive~"):
            return [self.XLET_MESSAGE]

        # [osc~]
        if self.name() in ("osc~"):
            return [self.XLET_SOUND, self.XLET_MESSAGE]


    def outlets(self):
        # [b] or [bang]
        if self.name() in ("bang", "b"):
            return [self.XLET_MESSAGE]

        # [f] or [float]
        if self.name() in ("float", "f"):
            return [self.XLET_MESSAGE]

        # [r]
        if self.name() in ("r", "receive"):
            return [self.XLET_MESSAGE]

        # [r~] or [receive~]
        if self.name() in ("r~", "receive~"):
            return [self.XLET_SOUND]

        # [osc~]
        if self.name() == "osc~":
            return [self.XLET_SOUND]
