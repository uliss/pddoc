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

import logging
import os.path as path
from ..colorformatter import ColorizingStreamHandler

root = logging.getLogger()
root.setLevel(logging.DEBUG)
root.addHandler(ColorizingStreamHandler())

EXTERNALS_DIR = path.join(path.dirname(__file__), "externals")
XLET_MESSAGE, XLET_SOUND, XLET_GUI, XLET_IGNORE = range(0, 4)

from .obj import PdObject
from .baseobject import BaseObject
from .canvas import Canvas
from .drawstyle import DrawStyle
from .parser import Parser
from .brectcalculator import BRectCalculator
from .coregui import CoreGui
from .message import Message
from .comment import Comment
from .factory import make_by_name
from .xletcalculator import XletCalculator
from .pdexporter import PdExporter
from .array import Array
