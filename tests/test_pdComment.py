#!/usr/bin/env python

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
from unittest import TestCase

__author__ = 'Serge Poltavski'

from pdcomment import *


class TestPdComment(TestCase):
    def test_unescape(self):
        self.assertEqual(PdComment.unescape("a\n\rb"), "ab")
        self.assertEqual(PdComment.unescape('\\,'), ',')
        self.assertEqual(PdComment.unescape("\\;"), ";")


    def test_text(self):
        c = PdComment(0, 0, ['test', 'message', 'with', '\\,', '\\;', ' special', 'chars'])
        self.assertEqual(c.text(), 'test message with,; special chars')