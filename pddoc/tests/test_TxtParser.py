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

import os.path
from unittest import TestCase

from pddoc import CairoPainter
from pddoc.pd import factory
from pddoc.pd.pdexporter import PdExporter
from pddoc.txt import Parser, Node
from .nologging import NoLogging
from ..pd.canvas import Canvas
from ..pd.obj import PdObject

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

    def test_parse_obj_id(self):
        self.p.parse('#a 1 2 3 @p 123')
        self.assertEqual(self.p.tokens[0].type, 'OBJECT_ID')

    def test_token_line_lex_pos(self):
        self.p.lines_len = [10, 2, 3, 4]
        self.assertEqual(self.p.token_line_lex_pos(0, 3), 3)
        self.assertEqual(self.p.token_line_lex_pos(1, 12), 1)

    def test_parse_file(self):
        nl = NoLogging()
        self.p.parse_file(TEST_FILE)

        self.assertEqual(self.p.num_lines(), 23)
        self.assertEqual(len(self.p.nodes), 34)
        self.assertEqual(self.p.num_elements('OBJECT'), 13)
        self.assertEqual(self.p.num_elements('MESSAGE'), 2)
        self.assertEqual(self.p.num_elements('COMMENT'), 1)
        self.assertEqual(self.p.num_elements('CONNECTION'), 15)

    def test_parse(self):
        pass
        # self.fail()

    def test_parse_tokens(self):
        pass
        # self.fail()

    def test_elements_in_line(self):
        nl = NoLogging()
        self.p.parse_file(TEST_FILE)
        self.assertEqual(len(self.p.elements_in_line('OBJECT', 3)), 3)
        self.assertEqual(len(self.p.elements_in_line('MESSAGE', 0)), 1)
        self.assertEqual(len(self.p.elements_in_line('COMMENT', 0)), 1)

    def test_export(self):
        nl = NoLogging()
        n = Node(None, 'CONNECTION')
        self.assertFalse(n.is_object())

        self.p.parse_file(TEST_FILE)
        cnv = Canvas(0, 0, 300, 400)
        cnv.type = Canvas.TYPE_WINDOW
        self.p.export(cnv)

        painter = CairoPainter(500, 400, "out/ascii.png", "png")
        cnv.draw(painter)

        pd_exporter = PdExporter()
        cnv.traverse(pd_exporter)
        pd_exporter.save("out/ascii.pd")

    def test_parse_kwargs(self):
        factory.add_import("ceammc")
        self.p.parse('[ui.scope~ @size=300x400]')
        self.assertEqual(self.p.tokens[0].type, 'OBJECT')
        self.assertTrue(self.p.nodes[0].pd_object is not None)
        obj = self.p.nodes[0].pd_object
        self.assertTrue(issubclass(obj.__class__, PdObject));
        self.assertEqual(obj.width, 300)
        self.assertEqual(obj.height, 400)
        self.assertEqual(obj.to_string(), 'ui.scope~ @size 300 400')
        self.assertEqual(obj.brect(), (20, 20, 300, 400))

    def test_find_by_hash(self):
        str = '''[int #a]
[mtof]
[float #b]
[msg #c(
        '''

        self.p.lines = str.split('\n')
        self.p.lines_len = list(map(lambda x: len(x), self.p.lines))
        self.p.lexer.input(str)
        self.p.parse_tokens()

        self.assertEqual(self.p.find_node_id_by_hash('a'), 0)
        self.assertEqual(self.p.find_node_id_by_hash('b'), 2000)
        self.assertEqual(self.p.find_node_id_by_hash('c'), 3000)

    def test_parse_named_connection(self):
        self.p.parse('''
        [float #a]
        [float #b]
        [X a:0->b:1]
        #b 1 2 3
        ''')
        self.assertEqual(self.p.tokens[0].type, 'OBJECT')
        self.assertEqual(self.p.nodes[0].id, 1008)
        self.assertEqual(self.p.tokens[1].type, 'OBJECT')
        self.assertEqual(self.p.nodes[1].id, 2008)
        self.assertEqual(self.p.tokens[2].type, 'CONNECTION_MANUAL')
        self.assertEqual(self.p.tokens[3].type, 'OBJECT_ID')
        self.assertEqual(self.p.nodes[2].conn_src_id, 1008)
        self.assertEqual(self.p.nodes[2].conn_dest_id, 2008)
        self.assertEqual(self.p.nodes[2].conn_src_outlet, 0)
        self.assertEqual(self.p.nodes[2].conn_dest_inlet, 1)
