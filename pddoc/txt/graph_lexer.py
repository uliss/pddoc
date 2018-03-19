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
import ply.lex as lex
from ply.lex import TOKEN
import re
import logging

# token names
tokens = (
    'OBJECT',
    'MESSAGE',
    'COMMENT',
    'CONNECTION',
    'CONNECTION_RIGHT',
    'CONNECTION_LEFT',
    'CONNECTION_X'
)

# token regexp
r_OBJECT = r'\[((?:[^\[\\]|\\.)+)\]'
r_MESSAGE = r'\[((?:[^\(\\]|\\.)+)\('
r_COMMENT = r'/\*(.+?)\*/'
r_NEWLINE = r'\n+'
t_CONNECTION = r'\^*\|\.*'          # ^^|.. connection
t_CONNECTION_RIGHT = r'\^*\\_*\.*'  # ^^\______..
t_CONNECTION_LEFT = r'\.*_*/\^*'    # ^^\______..
t_CONNECTION_X = r'(x|X)'
t_ignore = ' \r\t\f'


def t_error(t):
    logging.error("Illegal character '{0:s}'".format(t.value[0]))
    t.lexer.skip(1)


@TOKEN(r_NEWLINE)
def t_newline(t):
    t.lexer.lineno += len(t.value)


@TOKEN(r_OBJECT)
def t_OBJECT(t):
    return t


@TOKEN(r_MESSAGE)
def t_MESSAGE(t):
    return t


@TOKEN(r_COMMENT)
def t_COMMENT(t):
    return t


def lexer():
    return lex.lex(reflags=re.UNICODE)
