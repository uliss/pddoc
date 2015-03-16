#!/usr/bin/env python
# coding=utf-8

# Copyright (C) 2015 by Serge Poltavski                                 #
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

from unittest import TestCase

from pddoc.pd.slider import PdHSlider


class TestPdHSlider(TestCase):
    def test_draw(self):
        sl = PdHSlider(0, 0, width=10, height=11, min=-10, max=0, value=-1)
        self.assertEqual(sl.width, 10)
        self.assertEqual(sl.height, 11)

        self.assertEqual(sl.slider_pos(), 0.9)
        sl._value = 0
        self.assertEqual(sl.slider_pos(), 1.0)
        sl._value = -9
        self.assertEqual(sl.slider_pos(), 0.1)
        sl._value = -10
        self.assertEqual(sl.slider_pos(), 0)
