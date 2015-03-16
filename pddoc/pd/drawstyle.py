#!/usr/bin/env python
# coding=utf-8

# Copyright (C) 2014 by Serge Poltavski                                   #
# serge.poltavski@gmail.com                                             #
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

from sys import platform as _platform

from . import XLET_MESSAGE, XLET_GUI, XLET_SOUND


class DrawStyle(object):
    fill_color = property(lambda self: (1, 1, 1))
    font_size = property(lambda self: 12)

    obj_fill_color = property(lambda self: (0.95, 0.95, 0.95))
    obj_text_color = property(lambda self: (0, 0, 0))
    obj_border_color = property(lambda self: (0.2, 0.2, 0.2))
    obj_line_width = property(lambda self: 1)
    obj_pad_x = property(lambda self: 2.5)
    obj_pad_y = property(lambda self: 2)
    obj_min_width = property(lambda self: 22)

    msg_fill_color = property(lambda self: 0.94)
    msg_min_width = property(lambda self: 22)

    xlet_width = property(lambda self: 8)
    xlet_msg_height = property(lambda self: 2)
    xlet_snd_height = property(lambda self: 2)
    xlet_gui_height = property(lambda self: 1)
    xlet_msg_color = property(lambda self: (0, 0, 0))
    xlet_snd_color = property(lambda self: (0.3, 0.2, 0.4))
    xlet_gui_color = property(lambda self: (0, 0, 0))

    conn_snd_width = property(lambda self: 2)
    conn_snd_stripe = property(lambda self: True)
    conn_snd_color = property(lambda self: (0.2, 0.2, 0.2))
    conn_snd_color2 = property(lambda self: (0.6, 0.6, 0))
    conn_snd_dash = property(lambda self: [4, 8])

    conn_msg_color = property(lambda self: (0, 0, 0))
    conn_msg_width = property(lambda self: 1)

    comment_color = property(lambda self: (0.5, 0.5, 0.5))

    highlight_color = property(lambda self: (1, 0.9, 0.8))
    highlight_padding = 3

    @property
    def obj_height(self):
        return self.font_size + 5

    def xlet_height(self, t):
        if t == XLET_MESSAGE:
            return self.xlet_msg_height
        elif t == XLET_GUI:
            return self.xlet_gui_height
        elif t == XLET_SOUND:
            return self.xlet_snd_height
        else:
            assert False

    @property
    def font_family(self):
        # FIXME
        return "Menlo"

        if _platform == "darwin":
            return "Menlo"
        else:
            return "terminus"
