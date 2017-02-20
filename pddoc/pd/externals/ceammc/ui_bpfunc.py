#!/usr/bin/env python
# coding=utf-8

#   Copyright (C) 2017 by Serge Poltavski                                 #
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

from ui_base import UIBase
from pddoc.pd import XLET_GUI


def create_by_name(name, args=None, **kwargs):
    return UIBPFunc(0, 0, **kwargs)


class UIBPFunc(UIBase):
    def __init__(self, x, y, **kwargs):
        if '@size' not in kwargs:
            kwargs['@size'] = '200x150'

        UIBase.__init__(self, "ui.bpfunc", x, y, **kwargs)

    def inlets(self):
        return [XLET_GUI]

    def outlets(self):
        return [XLET_GUI]
