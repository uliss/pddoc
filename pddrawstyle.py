#!/usr/bin/env python

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


# -*- coding: utf-8 -*-

__author__ = 'Serge Poltavski'


class PdDrawStyle(object):
    def __init__(self):
        self._props = {}
        self.__dict__['fill_color'] = (1, 1, 1)
        self.__dict__['font_family'] = "terminus"
        self.__dict__['font_size'] = 12

        self.__dict__['obj_fill_color'] = (0.95, 0.95, 0.95)
        self.__dict__['obj_text_color'] = (0, 0, 0)
        self.__dict__['obj_border_color'] = (0.2, 0.2, 0.2)
        self.__dict__['obj_line_width'] = 1
        self.__dict__['obj_pad_x'] = 2.5
        self.__dict__['obj_pad_y'] = 1
        self.__dict__['obj_min_width'] = 22

        self.__dict__['msg_fill_color'] = (0.94)
        self.__dict__['msg_min_width'] = 22

        self.__dict__['xlet_width'] = 7
        self.__dict__['xlet_msg_height'] = 2
        self.__dict__['xlet_snd_height'] = 2
        self.__dict__['xlet_gui_height'] = 1
        self.__dict__['xlet_msg_color'] = (0, 0, 0)
        self.__dict__['xlet_snd_color'] = (0.3, 0.2, 0.4)
        self.__dict__['xlet_gui_color'] = (0, 0, 0)

        self.__dict__['conn_snd_width'] = 2
        self.__dict__['conn_snd_stripe'] = True
        self.__dict__['conn_snd_color'] = (0.2, 0.2, 0.2)
        self.__dict__['conn_snd_color2'] = (0.6, 0.6, 0)
        self.__dict__['conn_snd_dash'] = [4, 8]

        self.__dict__['conn_msg_color'] = (0, 0, 0)
        self.__dict__['conn_msg_width'] = 1

        self.__dict__['comment_color '] = (0.5, 0.5, 0.5)

    @property
    def obj_height(self):
        return self.font_size + 5

