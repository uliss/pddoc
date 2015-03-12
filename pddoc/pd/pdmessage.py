#!/usr/bin/env python
# coding=utf-8

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

__author__ = 'Serge Poltavski'

from pdobject import *


class PdMessage(PdObject):
    def __init__(self, x, y, atoms):
        super(PdMessage, self).__init__("msg", x, y, 0, 0, atoms)

    def __str__(self):
        res = "[%-40s {x:%i,y:%i,id:%i}" % (self.args_to_string() + "(", self._x, self._y, self._id)
        return res

    def to_string(self):
        return self.args_to_string()

    def draw(self, painter):
        painter.draw_message(self)

    def inlets(self):
        return [self.XLET_MESSAGE]

    def outlets(self):
        return [self.XLET_MESSAGE]

    def traverse(self, visitor):
        visitor.visit_message(self)