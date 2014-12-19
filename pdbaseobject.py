# /usr/bin/env python

#   Copyright (C) 2014 by Serge Poltavski                                 #
#   serge.poltavski@gmail.com                                            #
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


class PdBaseObject(object):
    XLET_MESSAGE = 0
    XLET_SOUND = 1

    def __init__(self, x, y, h, w):
        self.x = int(x)
        self.y = int(y)
        self.height = int(h)
        self.width = int(w)

    def draw(self, painter):
        pass

    def inlets(self):
        return ()

    def outlets(self):
        return ()
