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

import sys
import os

package_directory = os.path.dirname(os.path.abspath(__file__))
sys.path.append(package_directory + "/..")
from cairopainter import *
from pddrawer import *


if __name__ == '__main__':
    parser = PdParser()
    # parser.parse(package_directory + "/simple.pd")
    parser.parse("/Applications/Pd-extended.app/Contents/Resources/doc/5.reference/intro-help.pd")

    canvas = parser.canvas
    canvas.height = 5000

    cp = CairoPainter(canvas.width, canvas.height, "output_cairo.png")
    drawer = PdDrawer()
    drawer.draw(canvas, cp)