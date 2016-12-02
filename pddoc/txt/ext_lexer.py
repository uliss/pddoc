#!/usr/bin/env python
# coding=utf-8

#   Copyright (C) 2016 by Serge Poltavski                                 #
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
import ply.yacc as yacc
from ply.lex import TOKEN
import re

tokens = (
    'COMMENT_START',
    'COMMENT_END',
    'ASTERISK',
    'EOL',
    'WORD',
    'TAG'
)

t_COMMENT_END = r'(\*)+\/'
t_ASTERISK = '\*'
t_EOL = r'(\r|\n|(\r\n))'
t_WORD = r'[^ \t\r\n*]+'
t_TAG = r'@[^ \t\r\n*]+'
t_ignore = ' \t'


@TOKEN(r'\/\*(\*)+?')
def t_COMMENT_START(t):
    return t


def t_error(t):
    print("Illegal character '{0:s}'".format(t.value[0]))
    t.lexer.skip(1)


def lexer():
    return lex.lex(reflags=re.UNICODE | re.DOTALL)


doc = {}


def global_tags(name, value):
    name = name[1:]
    if name in ('version', 'license', 'brief', 'author', 'depends', 'see', 'library', 'name', 'category'):
        doc[name] = value

    if name == 'inlet':
        if not name in doc:
            doc[name] = list()

        d = dict()
        d['info'] = value

        for i in ('type', 'range', 'values'):
            k = 'xlet_' + i
            if k in doc:
                d[i] = doc[k]
                doc.pop(k, None)

        doc[name].append(d)

    if name == 'outlet':
        if not name in doc:
            doc[name] = list()

        d = dict()
        d['info'] = value

        for i in ('type', 'range', 'values'):
            k = 'xlet_' + i
            if k in doc:
                d[i] = doc[k]
                doc.pop(k, None)

        doc[name].append(d)

    if name in ('type', 'range', 'values'):
        doc['xlet_' + name] = value

    doc['prev_tag'] = name


def p_pddoc(p):
    '''pddoc : pddoc eol
             | COMMENT_START pdbody COMMENT_END'''
    # javaDoc ::=  <COMMENT_START > asteriskFound (eol(line)? ) * < COMMENT_END >
    if len(p) == 3:
        if p[1]:
            p[0] = p[1]
        else:
            p[0] = p[2]
    else:
        p[0] = p[2]


def p_pdbody(p):
    '''pdbody : pdcontent'''
    if len(p) > 1:
        p[0] = p[1]


def p_pdcontent(p):
    '''pdcontent : line
                 | line pdcontent'''
    lst = filter(None, p[1:])
    p[0] = ' '.join(lst)


# line 	::= 	( word restOfLine | asterisk asteriskFound | tag tagLine )
def p_line(p):
    '''line : rest_of_line
            | ASTERISK rest_of_line'''
    if len(p) > 2:
        p[0] = p[2]


def p_rest_of_line(p):
    '''rest_of_line : eol
                    | WORD rest_of_line
                    | ASTERISK rest_of_line
                    | TAG rest_of_line'''

    ln = filter(None, p[1:])
    # last word of line
    if len(ln) == 1:
        # empty tag
        if ln[0] == '@pddoc':
            doc['pddoc'] = True
        elif ln[0] == '@pddoc_end':
            doc['pddoc'] = False
        else:
            if not 'pddoc' in doc:
                p[0] = ln[0]

    if len(ln) == 2:
        if ln[0][0] == '@':
            global_tags(p[1], p[2])
        else:
            p[0] = ' '.join(p[1:])


def p_eol(p):
    '''eol : EOL'''


def p_error(p):
    print('Unexpected token:', p)


def parse_string(data):
    do_lex(data, None)
    parser = yacc.yacc()
    txt = parser.parse(data)
    return txt, doc


def do_lex(data, func=print):
    l = lexer()
    l.input(data)

    while True:
        tok = l.token()
        if not tok:
            break
        if func:
            func(tok)


if __name__ == '__main__':
    test_data = '''/**
 *  tanh -- hyperbolic tangent function
 *  it contains
 *
   @author Serge Poltavski, Alex,
   @library ceammc
    @license GPL
    @version 1.2-beta
    @inlet test
    @outlet test outlet
    @depends czexy
 *  @see inlet
 *  @inlet float [0-1) @type float @range -1,1 @values 1,2,3,4
 *  @inlet list - range
 *  @empty_tag
    @outlet - 1 or 0, @type symbol
    @method set - sets name
    @brief - brief description @obj[test]
    @arguments args
 *


   @pddoc
   [osc~ 440]
   |\
   [dac~]
   @pddoc_end
    ***/

    '''

    print(parse_string(test_data))
