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

from unittest import TestCase
from pddoc.txt import Parser, Node
import os.path
from pddoc.pd import Canvas
from pddoc.pd.pdexporter import PdExporter
from pddoc import CairoPainter

TEST_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), "ascii.txt")


class TestTxtParser(TestCase):
    def setUp(self):
        self.p = Parser()

    def tearDown(self):
        del self.p

    def test_parse_obj(self):
        self.p.parse('[object]')
        self.assertEqual(self.p.tokens[0].type, 'OBJECT')

        self.p.parse('[dac~ 1 2 3]')
        self.assertEqual(self.p.tokens[1].type, 'OBJECT')

    def test_token_line_lex_pos(self):
        self.p.lines_len = [10, 2, 3, 4]
        self.assertEqual(self.p.token_line_lex_pos(0, 3), 3)
        self.assertEqual(self.p.token_line_lex_pos(1, 12), 1)

    def test_parse_file(self):
        self.p.parse_file(TEST_FILE)

        self.assertEqual(self.p.num_lines(), 9)
        # self.assertEqual(len(self.p.nodes), 14)
        self.assertEqual(self.p.num_elements('OBJECT'), 4)
        self.assertEqual(self.p.num_elements('MESSAGE'), 2)
        self.assertEqual(self.p.num_elements('COMMENT'), 1)
        self.assertEqual(self.p.num_elements('CONNECTION'), 7)

    def test_parse(self):
        pass
        # self.fail()

    def test_parse_tokens(self):
        pass
        # self.fail()

    def test_elements_in_line(self):
        self.p.parse_file(TEST_FILE)
        self.assertEqual(len(self.p.elements_in_line('OBJECT', 3)), 2)
        self.assertEqual(len(self.p.elements_in_line('MESSAGE', 0)), 1)
        self.assertEqual(len(self.p.elements_in_line('COMMENT', 0)), 1)

    def test_export(self):
        n = Node(None, 'CONNECTION')
        self.assertFalse(n.is_object())

        self.p.parse_file(TEST_FILE)
        cnv = Canvas(0, 0, 300, 400)
        cnv.type = Canvas.TYPE_WINDOW
        self.p.export(cnv)

        painter = CairoPainter(400, 500, "out/ascii.png", "png")
        cnv.draw(painter)

        pd_exporter = PdExporter()
        cnv.traverse(pd_exporter)
        pd_exporter.save("out/ascii.pd")


