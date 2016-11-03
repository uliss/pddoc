#!/usr/bin/env python
# coding=utf-8
import os.path

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


def detect_format(args):
    if args['format'] is None:
        name, ext = os.path.splitext(args['output'].lower())
        if len(ext) > 2:
            ext = ext[1:]
        else:
            ext = None
    else:
        ext = args['format'][0].lower()

    if ext not in ('png', 'pdf', 'svg'):
        raise ValueError("output format not supported or can't be detected")

    return ext
