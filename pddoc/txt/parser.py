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
import logging
import re

from .graph_lexer import *
from pddoc.pd import Message, Comment, Canvas, Array, XLET_SOUND, XLET_MESSAGE
from six import string_types
from pddoc.pd import factory
from pddoc.pd.coregui import CoreGui
import copy
import logging



class Node(object):
    def __init__(self, tok, char_pos):
        self.tok = tok
        self.char_pos_ = char_pos
        self.pd_object = None
        self.conn_src_id = []
        self.conn_src_outlet = 0
        self.conn_dest_id = []
        self.conn_dest_inlet = 0
        self.connected = False
        self.multi_connect = None
        self.conn_multi = {}
        self.obj_line_index = -1

        if self.tok and self.is_connection():
            # calc connection source outlet
            self.conn_src_outlet = self.tok.value.count('^')
            self.conn_dest_inlet = self.tok.value.count('.')

            all_connect = list(map(lambda x: x.count('*'), self.tok.value.split('|')))
            if len(all_connect) == 2:
                if all_connect[0] > 0 and all_connect[1] > 0:
                    self.multi_connect = 'all'
                elif all_connect[0] > 0:
                    self.multi_connect = 'all_in'
                elif all_connect[1] > 0:
                    self.multi_connect = 'all_out'
            elif len(all_connect) == 1:
                if all_connect[0] > 0:
                    self.multi_connect = 'all_in'

            # only single \
            if self.tok.value == '\\':
                self.conn_dest_inlet += 1

    def group(self, n=1):
        return self.tok.lexmatch.group(n)

    def is_object(self):
        if self.tok is None:
            return False

        return self.tok.type in ('OBJECT', 'MESSAGE', 'COMMENT')

    def is_object_id(self):
        if self.tok is None:
            return False

        return self.tok.type == 'OBJECT_ID'

    def is_connection(self):
        return self.tok.type in ('CONNECTION', 'CONNECTION_LEFT', 'CONNECTION_RIGHT', 'CONNECTION_X', 'CONNECTION_MANUAL')

    def is_all_in_connection(self):
        return self.multi_connect == 'all_in'

    def is_all_out_connection(self):
        return self.multi_connect == 'all_out'

    def is_connect_all(self):
        return self.multi_connect == 'all'

    def is_multi_connect(self):
        return self.multi_connect is not None

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
    X_PAD = 20
    Y_PAD = 20
    X_SPACE = 8
    Y_SPACE = 12

    ALIASES = {
        '_': 'tgl',
        'T': 'tgl',
        'B': 'bng',
        'O': 'bng',
        'o': 'bng',
        'fa': 'floatatom',
        'F': 'floatatom',
        'S': 'symbolatom',
        'HR': 'hradio',
        'VR': 'vradio',
        'hsl': 'hslider',
        'vsl': 'vslider',
        'HS': 'hslider',
        'VS': 'vslider',
        'A': 'array'
    }

    def __init__(self):
        self.lines = []
        self.lines_len = []
        self.tokens = []
        self.nodes = []
        self.lexer = lexer()

    def clear(self):
        self.lines = []
        self.lines_len = []
        self.tokens = []
        self.nodes = []
        self.lexer = lexer()

    def parse_file(self, fname):
        with open(fname) as f:
            self.parse(f.read())

    def node_by_id(self, id):
        res = list(filter(lambda n: id == n.id, self.nodes))
        if len(res) < 1:
            return None

        return res[0]

    def parse(self, string):
        assert isinstance(string, string_types)

        self.lines = string.split('\n')
        self.lines_len = list(map(lambda x: len(x), self.lines))
        self.lexer.input(string)
        self.parse_tokens()
        self.parse_nodes()
        self.enumerate_objects()
        self.parse_connections()
        self.layout_nodes()
        return True

    def token_line_lex_pos(self, lexline, lexpos):
        assert lexpos >= 0
        assert lexline >= 0
        assert lexline < len(self.lines_len)

        return lexpos - sum(self.lines_len[0:lexline]) - lexline

    def enumerate_objects(self):
        for l in range(0, self.num_lines()):
            idx = 0
            for o in filter(lambda x: x.line_pos == l, self.nodes):
                o.obj_line_index = idx
                idx += 1

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

    @classmethod
    def find_alias(cls, atoms):
        name = atoms[0]
        args = atoms[1:]
        if name in cls.ALIASES:
            return cls.ALIASES[name], args
        return name, args

    def find_node_id_by_hash(self, hash):
        for n in filter(lambda x: x.is_object(), self.nodes):
            if n.value.startswith('X'):
                continue

            m = re.match(r_OBJECT, n.value)
            if not m:
                m = re.match(r_MESSAGE, n.value)
                if not m:
                    continue

            # filter spaces and #ID values
            atoms = filter(lambda a: len(a) > 0 and a.startswith('#'), m.group(1).split(' '))
            if '#' + hash in atoms:
                return n.id

        return False

    def parse_nodes(self):
        obj_args = dict()

        for n in filter(lambda x: x.is_object_id(), self.nodes):
            m = re.match(r_OBJECT_ID, n.value)
            # skip spaces
            atoms = list(filter(lambda b: len(b) > 0, m.group(1).split(' ')))
            obj_args[atoms[0]] = atoms[1:]
            # logging.error(atoms[1:])

        for n in filter(lambda x: x.is_object(), self.nodes):
            if n.type == 'OBJECT':
                m = re.match(r_OBJECT, n.value)
                # skip spaces
                all_atoms = list(filter(lambda b: len(b) > 0, m.group(1).split(' ')))
                # skip #ID values
                atoms = list(filter(lambda b: not b.startswith('#'), all_atoms))
                assert len(atoms) > 0
                name, args = self.find_alias(atoms)
                kwargs = dict()

                for a in args:
                    pair = a.split('=')
                    if len(pair) == 2:
                        kwargs[pair[0]] = pair[1]

                if CoreGui.is_coregui(name):
                    n.pd_object = factory.make_by_name(name, **kwargs)
                elif name == 'pd':
                    n.pd_object = Canvas.subpatch(args[0])
                elif name == 'X':
                    n.tok.type = 'CONNECTION_MANUAL'
                    str = atoms[1]
                    conn = []

                    # syntax: SRC_ID(:OUTLET_N)->DEST_ID(:INLET_N)
                    for i in map(lambda x: x.split(':'), str.split('->')):
                        # if xlet is not specified using first xlet
                        if len(i) == 1:
                            i.append(0)

                        # i now is [OBJ_ID, XLET_IDX]
                        assert len(i) == 2

                        obj_id = self.find_node_id_by_hash(i[0])
                        if obj_id is False:
                            logging.error("can't find node with id: {0:s}".format(i[0]))
                            return

                        i[0] = obj_id
                        conn.append(i)

                    # conn at this moment: [[SRC, OUT_IDX], [DEST, IN_IDX]]
                    assert len(conn) == 2

                    n.conn_src_id = conn[0][0]
                    n.conn_src_outlet = int(conn[0][1])
                    n.conn_dest_id = conn[1][0]
                    n.conn_dest_inlet = int(conn[1][1])

                elif name == 'array':
                    # check for id
                    array_ids = list(filter(lambda b: b.startswith("#"), all_atoms))
                    if len(array_ids) > 0:
                        # trim '#'
                        aid = array_ids[0][1:]
                        if aid in obj_args:
                            for kv in obj_args[aid]:
                                k, v = kv.split('=')
                                kwargs[k] = v

                    if args[0] in ("set", "get", "define", "sum", "size", "random", "min", "max"):
                        n.pd_object = factory.make_by_name(name + " " + args[0], args[1:], **kwargs)
                    else:
                        n.pd_object = Array(args[0], kwargs.get('size', 100), kwargs.get('save', 0))
                        n.pd_object.width = kwargs.get('w', 200)
                        n.pd_object.height = kwargs.get('h', 140)
                        yr = list(map(lambda x: float(x), kwargs.get('yr', "-1..1").split('..')))
                        n.pd_object.set_yrange(yr[0], yr[1])
                        if 'style' in kwargs:
                            values = ('line', 'point', 'curve')
                            st = kwargs['style']
                            if st in values:
                                n.pd_object.set_style(values.index(st))
                            else:
                                logging.error("invalid style: '%s', supported values are: '%s'", st, ", ".join(values))
                else:
                    # check options
                    opts = {}
                    for arg in args[:]:
                        # no spaces allowed: {x=1,y=1,etc=...}
                        if arg[0] == '{' and arg[-1] == '}':
                            opts.update(parse_object_options(arg))
                            args.remove(arg)

                    # adding id arguments defined with '#id arg1 arg2...'
                    all_id = list(filter(lambda b: b.startswith("#"), all_atoms))
                    if len(all_id) > 0 and all_id[0][1:] in obj_args:
                        args += obj_args[all_id[0][1:]]

                    n.pd_object = factory.make_by_name(name, args, **kwargs)
                    process_object_options(n.pd_object, opts)

            elif n.type == 'MESSAGE':
                m = re.match(r_MESSAGE, n.value)
                txt = m.group(1).replace(',', '\,')
                all_atoms = txt.split(' ')
                args = list(filter(lambda a: len(a) > 0 and (not a.startswith('#')), all_atoms))

                # adding id arguments defined with '#id arg1 arg2...'
                all_id = list(filter(lambda b: b.startswith("#"), all_atoms))
                if len(all_id) > 0 and all_id[0][1:] in obj_args:
                    # logging.error(obj_args[all_id[0][1:]])
                    args += obj_args[all_id[0][1:]]

                n.pd_object = Message(0, 0, args)
            elif n.type == 'COMMENT':
                m = re.match(r_COMMENT, n.value)
                txt = m.group(1).replace(';', ' \;').replace(',', ' \,')
                n.pd_object = Comment(0, 0, txt.split(' '))
            else:
                logging.warning("Unknown type {0:s}".format(n.type))

    def parse_connections(self):
        for c in filter(lambda n: n.is_connection(), self.nodes):
            self.process_connection(c)

    def find_connection(self, line, char_pos):
        """
        :type line: int
        :type char_pos: list
        """
        return next(filter(
            lambda x:
            x.line_pos == line and any(list(map(lambda c: x.contains(c), char_pos))), self.nodes), None)

    def find_by_line_idx(self, line, idx):
        return next((filter(lambda n: n.line_pos == line and n.obj_line_index == idx, self.nodes)), None)

    def process_cross_connection(self, conn):
        assert isinstance(conn, Node)
        line = conn.line_pos
        src_idx = conn.obj_line_index - 1
        dest_idx = conn.obj_line_index + 1

        src = self.find_by_line_idx(line, src_idx)
        dest = self.find_by_line_idx(line, dest_idx)

        if src and dest:
            c1 = copy.deepcopy(conn)
            c1.tok.type = 'CONNECTION'
            c1.conn_src_id = src.id
            c1.conn_dest_id = dest.id
            c1.conn_dest_inlet = 0
            c1.conn_src_outlet = len(src.pd_object.outlets()) - 1
            c1.connected = True

            c2 = copy.deepcopy(conn)
            c2.tok.type = 'CONNECTION'
            c2.conn_src_id = dest.id
            c2.conn_dest_id = src.id
            c2.conn_src_outlet = 0
            c2.conn_dest_inlet = len(src.pd_object.inlets()) - 1
            c2.connected = True

            self.nodes.append(c1)
            self.nodes.append(c2)

    def process_connection(self, c):
        if c.type == 'CONNECTION_MANUAL':
            c.connected = True
            return

        if c.type == 'CONNECTION_X':
            self.process_cross_connection(c)
            return

        if c.type == 'CONNECTION_LEFT':
            conn_start = [c.char_pos + c.tok.value.index('/')]
        else:
            conn_start = [c.char_pos]

        # find object on previous line
        src = self.find_connection(c.line_pos - 1, conn_start)
        if src is None:
            logging.warning("connection source is not found for: {0:s}".format(str(c)))
            return

        c.conn_src_id = src.id
        if src.is_connection():
            # multiline connection
            c.conn_src_id = src.conn_src_id
            c.conn_src_outlet = src.conn_src_outlet
            src.connected = False

        # find on next line
        dest = self.find_connection(c.line_pos + 1, [c.char_pos, c.char_pos + c.width])
        if dest is None:
            logging.warning("connection destination is not found for: {0:s}".format(c.tok.value))
            return

        c.conn_dest_id = dest.id
        c.connected = True

    def layout_nodes(self):
        obj = filter(lambda x: x.is_object() and x.pd_object is not None, self.nodes)
        for n in obj:
            n.pd_object.x = n.char_pos * self.X_SPACE + self.X_PAD
            n.pd_object.y = n.line_pos * self.Y_SPACE + self.Y_PAD

    def num_lines(self):
        return len(self.lines)

    def num_elements(self, type):
        return len(self.elements(type))

    def elements(self, type):
        return list(filter(lambda x: x.type == type, self.nodes))

    def elements_in_line(self, type, line_pos):
        return list(filter(lambda x: x.type == type and x.line_pos == line_pos, self.nodes))

    def export(self, cnv):
        assert isinstance(cnv, Canvas)
        for n in filter(lambda x: x.is_object() and x.pd_object is not None, self.nodes):
            cnv.append_object(n.pd_object)

        for c in filter(lambda x: x.is_connection() and x.connected, self.nodes):
            src = self.node_by_id(c.conn_src_id)
            dest = self.node_by_id(c.conn_dest_id)

            if not src or not dest:
                continue

            if not src.pd_object or not dest.pd_object:
                logging.warning("can't connect {0:s} and {1:s}".format(src.tok, dest.tok))
                return

            if not c.is_multi_connect():
                cnv.add_connection(
                    src.pd_object.id,
                    c.conn_src_outlet,
                    dest.pd_object.id,
                    c.conn_dest_inlet)
            elif c.is_all_in_connection():
                n = len(src.pd_object.outlets())
                for i in range(n):
                    cnv.add_connection(
                        src.pd_object.id,
                        i,
                        dest.pd_object.id,
                        c.conn_dest_inlet)
            elif c.is_all_out_connection():
                n = len(dest.pd_object.inlets())
                for i in range(n):
                    cnv.add_connection(
                        src.pd_object.id,
                        c.conn_src_outlet,
                        dest.pd_object.id,
                        i)
            elif c.is_connect_all():
                n_in = len(src.pd_object.outlets())
                n_out = len(dest.pd_object.inlets())

                # print("c:", src.pd_object.name, src.pd_object.outlets(), dest.pd_object.name, dest.pd_object.inlets())
                for i in range(min(n_in, n_out)):
                    cnv.add_connection(
                        src.pd_object.id,
                        i,
                        dest.pd_object.id,
                        i)


def parse_object_option(name, txt):
    if name == 'w':
        return {'w': int(txt)}
    elif name == 'i':
        res = {'i': True}

        opt_res = re.match(r"(\d*)(~?)(\d*)", txt)
        if opt_res.group(1) != "":
            res["in_sig"] = int(opt_res.group(1))
        if opt_res.group(3) != "":
            res["in_ctl"] = int(opt_res.group(3))

        return res
    elif name == 'o':
        res = {'o': True}

        opt_res = re.match(r"(\d*)(~?)(\d*)", txt)
        if opt_res.group(1) != "":
            res["out_sig"] = int(opt_res.group(1))
        if opt_res.group(3) != "":
            res["out_ctl"] = int(opt_res.group(3))

        return res


def parse_object_options(arg):
    res = {}
    arg_str = arg[1:-1]
    if len(arg_str) < 1:
        return res

    re_opt = re.compile(r"(\w)=(.+)")

    for opt in arg_str.split(","):
        res_opt = re.match(re_opt, opt)
        if res_opt:
            res.update(parse_object_option(res_opt.group(1), res_opt.group(2)))

    return res


def process_object_options(obj, opts: dict):
    # print(opts)

    if 'w' in opts:
        obj.fixed_width = opts['w']

    if 'i' in opts:
        xin = opts.get('in_sig', 0) * [XLET_SOUND] + opts.get('in_ctl', 0) * [XLET_MESSAGE]
        obj.set_inlets(xin)

    if 'o' in opts:
        xout = opts.get('out_sig', 0) * [XLET_SOUND] + opts.get('out_ctl', 0) * [XLET_MESSAGE]
        obj.set_outlets(xout)
