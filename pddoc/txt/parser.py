#!/usr/bin/env python
# coding=utf-8

# Copyright (C) 2016 by Serge Poltavski                                 #
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

from __future__ import print_function
import lexer as lex
import re
from pddoc.pd import Message, Comment, Canvas
from six import string_types
from pddoc.pd import factory


class Node(object):
    def __init__(self, tok, char_pos):
        self.tok = tok
        self.char_pos_ = char_pos
        self.pd_object = None

    def group(self, n=1):
        return self.tok.lexmatch.group(n)

    def is_object(self):
        if self.tok is None:
            return False

        return self.tok.type in ('OBJECT', 'MESSAGE', 'COMMENT')

    def is_connection(self):
        return self.tok.type == 'CONNECTION'

    @property
    def id(self):
        return self.line_pos * 1000 + self.char_pos

    @property
    def type(self):
        if self.tok is None:
            return None

        return self.tok.type

    @property
    def width(self):
        return len(self.tok.value)

    @property
    def value(self):
        return self.tok.value

    @property
    def line_pos(self):
        return self.tok.lineno - 1

    @property
    def char_pos(self):
        return self.char_pos_

    def contains(self, char_pos):
        return self.char_pos <= char_pos <= (self.char_pos + self.width)


class Parser(object):
    tokens = []
    lexer = None
    lines = []
    lines_len = []
    nodes = []

    def __init__(self):
        self.clear()

    def clear(self):
        self.lines = []
        self.lines_len = []
        self.tokens = []
        self.nodes = []
        self.lexer = lex.lexer()

    def parse_file(self, fname):
        with open(fname) as f:
            self.parse(f.read())

    def parse(self, string):
        assert isinstance(string, string_types)

        self.lines = string.split('\n')
        self.lines_len = map(lambda x: len(x), self.lines)
        self.lexer.input(string)
        self.parse_tokens()
        self.parse_nodes()
        self.layout_nodes()

    def token_line_lex_pos(self, lexline, lexpos):
        assert lexpos >= 0
        assert lexline >= 0
        assert lexline < len(self.lines_len)

        return lexpos - sum(self.lines_len[0:lexline]) - lexline

    def parse_tokens(self):
        while True:
            tok = self.lexer.token()
            if not tok:
                break

            self.tokens.append(tok)

            ln = tok.lineno - 1
            char_pos = self.token_line_lex_pos(ln, tok.lexpos)
            n = Node(tok, char_pos)
            self.nodes.append(n)

    def parse_nodes(self):
        for n in self.nodes:
            if not n.is_object():
                continue

            if n.type == 'OBJECT':
                m = re.match(lex.r_OBJECT, n.value)
                atoms = m.group(1).split(' ')
                assert len(atoms) > 0
                name = atoms[0]
                args = atoms[1:]
                n.pd_object = factory.make_by_name(name, args)
            elif n.type == 'MESSAGE':
                m = re.match(lex.r_MESSAGE, n.value)
                args = m.group(1).split(' ')
                n.pd_object = Message(0, 0, args)
            elif n.type == 'COMMENT':
                m = re.match(lex.r_COMMENT, n.value)
                txt = m.group(1).replace(';', ' \;').replace(',', ' \,')
                n.pd_object = Comment(0, 0, txt.split(' '))
            else:
                print(u"Unknown type {0:s}".format(n.type))

    def layout_nodes(self):
        X_OFF = 20
        Y_OFF = 20
        X_SPACE = 10
        Y_SPACE = 20
        obj = filter(lambda x: x.is_object(), self.nodes)
        for n in obj:
            n.pd_object.x = n.char_pos * X_SPACE + X_OFF
            n.pd_object.y = n.line_pos * Y_SPACE + Y_OFF

    def num_lines(self):
        return len(self.lines)

    def num_elements(self, type):
        return len(self.elements(type))

    def elements(self, type):
        return filter(lambda x: x.type == type, self.nodes)

    def elements_in_line(self, type, line_pos):
        return filter(lambda x: x.type == type and x.line_pos == line_pos, self.nodes)

    def export(self, cnv):
        assert isinstance(cnv, Canvas)
        for n in filter(lambda x: x.is_object(), self.nodes):
            cnv.append_object(n.pd_object)

