#!/usr/bin/env python
# coding=utf-8

#   Copyright (C) 2015 by Serge Poltavski                                 #
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

from pdcoregui import PdCoreGui

[size]? - number of digits the element displays
[height]? - vertical size of element in pixels
[min]? - minimum value, typically -1e+037
[max]? - maximum value, typically 1e+037
[log]? - linear when unset, logarithmic when set
[init]? - when set outputs
[send]? - send symbol name
[receive]? - receive symbol name
[label]? - label
[x_off]? - horizontal position of the label text relative to the upperleft corner of the object
[y_off]? - vertical position of the label text relative to the upperleft corner of the object
[font]? - font type
[fontsize]? - font size in pixels
[bg_color]? - background color
[fg_color]? - foreground color
[label_color]? - label color
[log_height]? - logarithmic steps, accepts values from 10 to 2000, default is 256


class PdNbx(PdCoreGui):
    def __init__(self, x, y, **kwargs):
        PdCoreGui.__init__(self, "nbx", x, y, [1])
        self._size = kwargs.get('size', )
