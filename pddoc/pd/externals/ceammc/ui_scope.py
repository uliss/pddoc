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
from pddoc.pd import XLET_SOUND


def create_by_name(name, args=None, **kwargs):
    return UIScope(0, 0, **kwargs)


class UIScope(UIBase):
    @staticmethod
    def from_atoms(atoms):
        return UIScope(0, 0,
                    size=atoms[1],
                    min=atoms[3],
                    max=atoms[4],
                    log=atoms[5],
                    init=atoms[6],
                    send=atoms[7],
                    receive=atoms[8],
                    label=atoms[9],
                    label_xoff=atoms[10],
                    label_yoff=atoms[11],
                    font_type=atoms[12],
                    font_size=atoms[13],
                    bg_color=atoms[14],
                    fg_color=atoms[15],
                    label_color=atoms[16],
                    init_value=atoms[17],
                    steady=atoms[18])

    def __init__(self, x, y, **kwargs):
        if '@size' not in kwargs:
            kwargs['@size'] = '150x100'

        UIBase.__init__(self, "ui.scope~", x, y, **kwargs)

    def inlets(self):
        return [XLET_SOUND]

    def outlets(self):
        return []
