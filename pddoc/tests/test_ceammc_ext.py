#!/usr/bin/env python
# coding=utf-8

#   Copyright (C) 2017 by Serge Poltavski                                 #
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

from unittest import TestCase, expectedFailure
import pddoc.pd.factory as f
from pddoc.pd.obj import PdObject

__author__ = 'Serge Poltavski'


class TestCeammcExt(TestCase):
    def test_ui_scope(self):
        self.assertTrue(f.find_external_object("ceammc/ui.scope~"))
        self.assertTrue(f.find_external_object("ceammc/ui_scope~"))

        self.assertFalse(f.find_external_object("ui.scope~"))
        self.assertFalse(f.find_external_object("ui_scope~"))
        self.assertFalse(f.find_external_object("ui.scope"))
        self.assertFalse(f.find_external_object("ui_scope"))
        f.add_import("ceammc")
        self.assertTrue(f.find_external_object("ui.scope"))
        self.assertTrue(f.find_external_object("ui_scope"))
        self.assertTrue(f.find_external_object("ui.scope~"))
        self.assertTrue(f.find_external_object("ui_scope~"))


        args = dict()
        args['@size'] = '100x200'
        sc = f.make_by_name("ceammc/ui_scope~", **args)
        self.assertTrue(issubclass(sc.__class__, PdObject))
        self.assertEqual(sc.width, 100)
        self.assertEqual(sc.height, 200)

        # default size
        sc = f.make_by_name("ceammc/ui_scope~")
        self.assertTrue(issubclass(sc.__class__, PdObject))
        self.assertEqual(sc.width, 100)
        self.assertEqual(sc.height, 25)

        self.assertEqual(sc.args, ['@size', '100', '25'])

    def test_export(self):
        sc = f.make_by_name("ceammc/ui_scope~")

        self.assertEqual(sc.to_string(), "ui.scope~ @size 100 25")
        sc.x = 10
        sc.y = 20

        sc.calc_brect()
        self.assertEqual(sc.brect(), (10, 20, 100, 25))
