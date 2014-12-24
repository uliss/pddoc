#!/usr/bin/env python

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


# -*- coding: utf-8 -*-
from unittest import TestCase

__author__ = 'Serge Poltavski'

from pdcoregui import *


class TestPdCoreGui(TestCase):
    def test_init(self):
        pco = PdCoreGui("tgl", 0, 0, PdCoreGui.tgl_defaults)
        self.assertEqual(pco.inlets(), [PdCoreGui.XLET_GUI])
        self.assertEqual(pco.outlets(), [PdCoreGui.XLET_GUI])
        self.assertEqual(pco.prop("size"), 15)
        self.assertEqual(pco.prop("send"), None)
        self.assertEqual(pco.prop("receive"), None)

    def test_str__(self):
        pco = PdCoreGui("tgl", 5, 6, PdCoreGui.tgl_defaults)
        self.assertEqual(str(pco), "[GUI:tgl]                                 {x:5,y:6,id:-1}")