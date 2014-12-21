# /usr/bin/env python
from __future__ import print_function

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


# -*- coding: utf-8 -*-

__author__ = 'Serge Poltavski'

import sys
import os.path as path
from termcolor import colored
from colorama import init
import inspect

# use Colorama to make Termcolor work on Windows too
init()

def warning(*objs):
    print(colored("WARNING: ", "red"), *objs, file=sys.stderr)


def error_place():
    info = inspect.getframeinfo(inspect.currentframe().f_back)[0:3]
    return '[file: %s, method: %s, line:%d]' % (path.basename(info[0]), info[2], info[1])


