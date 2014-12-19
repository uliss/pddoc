# /usr/bin/env python

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


# -*- coding: utf-8 -*-

__author__ = 'Serge Poltavski'

from pdbaseobject import *


class PdComment(PdBaseObject):
    def __init__(self, x, y, args):
        super(PdComment, self).__init__(x, y, -1, -1)
        self.args = args
        self.text = ""
        self.set_text(" ".join(args))

    def set_text(self, text):
        """
        ASCII return codes 13 and 10 are not stored,
        a semicolon character is preceded with the escape character backslash.
        :param text:
        """
        self.text = text.replace(chr(13), "")\
            .replace(chr(10), "")\
            .replace(";", "\\;")

    def __str__(self):
        res = "# %-39s {x:%i,y:%i}" % (self.text, self.x, self.y)
        return res

    def draw(self, painter):
        painter.draw_comment(self)