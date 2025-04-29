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

import copy
from typing import Optional

from ply.lex import LexToken

from pddoc.pd import factory
from pddoc.pd.array import Array
from pddoc.pd.canvas import Canvas
from pddoc.pd.comment import Comment
from pddoc.pd.constants import XLET_SOUND, XLET_MESSAGE
from pddoc.pd.coregui import CoreGui
from pddoc.pd.message import Message
from .graph_lexer import *


class Node(object):
    def __init__(self, tok: LexToken, char_pos: int):
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
        self.obj_ax = None
        self.obj_ay = None;

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

    def is_comment(self) -> bool:
        if self.tok is None:
            return False

        return self.tok.type == 'COMMENT'

    def is_object(self) -> bool:
        if self.tok is None:
            return False

        return self.tok.type in ('OBJECT', 'MESSAGE', 'COMMENT')

    def is_object_id(self) -> bool:
        if self.tok is None:
            return False

        return self.tok.type == 'OBJECT_ID'

    def is_connection(self) -> bool:
        return self.tok.type in (
            'CONNECTION', 'CONNECTION_LEFT', 'CONNECTION_RIGHT', 'CONNECTION_X', 'CONNECTION_MANUAL')

    def is_all_in_connection(self) -> bool:
        return self.multi_connect == 'all_in'

    def is_all_out_connection(self) -> bool:
        return self.multi_connect == 'all_out'

    def is_connect_all(self) -> bool:
        return self.multi_connect == 'all'

    def is_multi_connect(self) -> bool:
        return self.multi_connect is not None

    @property
    def id(self) -> int:
        return self.line_pos * 1000 + self.char_pos

    @property
    def type(self):
        if self.tok is None:
            return None

        return self.tok.type

    @property
    def width(self) -> int:
        return len(self.tok.value)

    @property
    def value(self):
        return self.tok.value

    @property
    def line_pos(self) -> int:
        return self.tok.lineno - 1

    @property
    def char_pos(self) -> int:
        return self.char_pos_

    @char_pos.setter
    def char_pos(self, pos: int):
        self.char_pos_ = pos

    def contains(self, char_pos: int) -> bool:
        return self.char_pos <= char_pos <= (self.char_pos + self.width)

    def has_abs_pos(self):
        return (self.obj_ax is not None) and (self.obj_ay is not None)


class Parser(object):
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
        'A': 'array',
        'L': 'listbox',
    }

    def __init__(self):
        self.X_PAD = 20
        self.Y_PAD = 20
        self.X_SPACE = 8
        self.Y_SPACE = 12
        self.lines: list[str] = []
        self.lines_len: list[int] = []
        self.tokens = []
        self.nodes: list[Node] = []
        self.lexer = lexer()

    def clear(self):
        self.lines = []
        self.lines_len = []
        self.tokens = []
        self.nodes = []
        self.lexer = lexer()

    def parse_file(self, filename: str):
        with open(filename) as f:
            self.parse(f.read())

    def node_by_id(self, node_id: int) -> Optional[Node]:
        res = list(filter(lambda n: node_id == n.id, self.nodes))
        if len(res) < 1:
            return None

        return res[0]

    def parse(self, string: str):
        self.lines = string.split('\n')
        self.lines_len = list(map(lambda x: len(x), self.lines))
        self.lexer.input(string)
        self.parse_tokens()
        self.parse_nodes()
        self.enumerate_objects()
        self.parse_connections()
        self.layout_nodes()
        return True

    def token_line_lex_pos(self, lex_line: int, lex_pos: int):
        assert lex_pos >= 0
        assert lex_line >= 0
        assert lex_line < len(self.lines_len)

        return lex_pos - sum(self.lines_len[0:lex_line]) - lex_line

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
            # logging.debug(f"{tok.type}: {tok.value}")

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

    def find_node_id_by_hash(self, node_hash: str) -> int:
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
            if '#' + node_hash in atoms:
                return n.id

        return -1

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
                elif name == 'X':  # connection object
                    n.tok.type = 'CONNECTION_MANUAL'
                    conn_str = atoms[1]
                    conn = []

                    # syntax: SRC_ID(:OUTLET_N)->DEST_ID(:INLET_N)
                    src_dest = conn_str.split('->')
                    if len(src_dest) != 2:
                        logging.error(f"invalid connection string: '{conn_str}'")
                        continue

                    src_data = src_dest[0].split(':')
                    if len(src_data) > 2:
                        logging.error(f"invalid source: '{src_dest[0]}'")
                        continue

                    # process source
                    src_hash = src_data[0]
                    src_out = 0
                    if len(src_data) == 2:
                        src_out = int(src_data[1])

                    src_id = self.find_node_id_by_hash(src_hash)
                    if src_id < 0:
                        logging.error(f"can't find source node with hash #id: {src_hash}")
                        continue

                    # process destination
                    dest_data = src_dest[1].split(':')
                    if len(dest_data) > 2:
                        logging.error(f"invalid destination: '{src_dest[1]}'")
                        continue

                    dest_hash = dest_data[0]
                    dest_inl = 0
                    if len(dest_data) == 2:
                        dest_inl = int(dest_data[1])

                    dest_id = self.find_node_id_by_hash(dest_hash)
                    if dest_id < 0:
                        logging.error(f"can't find destination node with hash #id: {dest_hash}")
                        continue

                    n.conn_src_id = src_id
                    n.conn_src_outlet = src_out
                    n.conn_dest_id = dest_id
                    n.conn_dest_inlet = dest_inl

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
                        # print("ARRAY args", kwargs)
                        n.pd_object = Array(args[0], int(kwargs.get('size', 100)), int(kwargs.get('save', 0)))
                        n.pd_object.width = int(kwargs.get('w', 200))
                        n.pd_object.height = int(kwargs.get('h', 140))
                        yr = list(map(lambda x: float(x), kwargs.get('yr', "-1..1").split('..')))
                        n.pd_object.set_yrange(yr[0], yr[1])
                        # print(n.pd_object)
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
                    process_object_options(n, opts)

            elif n.type == 'MESSAGE':
                m = re.match(r_MESSAGE, n.value)
                txt = m.group(1).replace(',', '\\,')
                all_atoms = txt.split(' ')
                args = list(filter(lambda a: len(a) > 0 and (not a.startswith('#')), all_atoms))

                # check options
                opts = {}
                for arg in args[:]:
                    # no spaces allowed: {x=1,y=1,etc=...}
                    if arg[0] == '{' and arg[-1] == '}':
                        args.remove(arg)
                        opts.update(parse_object_options(arg.replace('\\,', ',')))

                # adding id arguments defined with '#id arg1 arg2...'
                all_id = list(filter(lambda b: b.startswith("#"), all_atoms))
                if len(all_id) > 0 and all_id[0][1:] in obj_args:
                    # logging.error(obj_args[all_id[0][1:]])
                    args += obj_args[all_id[0][1:]]

                n.pd_object = Message(0, 0, args)
                process_object_options(n, opts)
            elif n.type == 'COMMENT':
                m = re.match(r_COMMENT, n.value)
                txt = m.group(1).replace(';', ' \\;').replace(',', ' \\,')
                n.pd_object = Comment(0, 0, txt.split(' '))
            else:
                logging.warning("Unknown type {0:s}".format(n.type))

    def parse_connections(self):
        for c in filter(lambda n: n.is_connection(), self.nodes):
            self.process_connection(c)

    def find_connection(self, line: int, char_pos: list):
        """
        :type line: int
        :type char_pos: list
        """
        return next(filter(
            lambda x:
            x.line_pos == line and any(list(map(lambda c: x.contains(c), char_pos))), self.nodes), None)

    def find_by_line_idx(self, line: int, idx: int) -> Optional[Node]:
        return next((filter(lambda n: n.line_pos == line and n.obj_line_index == idx, self.nodes)), None)

    def process_cross_connection(self, conn: Node):
        assert isinstance(conn, Node)
        line = conn.line_pos
        src_idx = conn.obj_line_index - 1
        dest_idx = conn.obj_line_index + 1

        src = self.find_by_line_idx(line, src_idx)
        if not src:
            logging.error(f"X-connection source not found: {line} {src_idx}")
            return

        dest = self.find_by_line_idx(line, dest_idx)
        if not src:
            logging.error(f"X-connection destination not found: {line} {dest_idx}")
            return

        if src and dest:
            if len(src.pd_object.outlets()) == 0:
                logging.error(f"no outlets in source object: [{src.pd_object.name}] id={src.id}")
                return

            if len(src.pd_object.inlets()) == 0:
                logging.error(f"no inlets in source object: [{src.pd_object.name}] id={src.id}")
                return

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

    def process_connection(self, c: Node):
        if c.type == 'CONNECTION' and c.connected:
            return

        if c.type == 'CONNECTION_MANUAL':
            c.connected = True
            return

        if c.type == 'CONNECTION_X':  # replace cross-connections with common connections
            self.process_cross_connection(c)
            return

        if c.type == 'CONNECTION_LEFT':
            conn_start = [c.char_pos + c.tok.value.index('/')]
        else:
            conn_start = [c.char_pos]

        # find object on previous line
        src = self.find_connection(c.line_pos - 1, conn_start)
        if src is None:
            logging.warning("connection source (type {1:s}) is not found for: {0:s}".format(str(c.value), c.type))
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
            if n.has_abs_pos():
                n.pd_object.x = n.obj_ax
                n.pd_object.y = n.obj_ay
            else:
                n.pd_object.x = n.char_pos * self.X_SPACE + self.X_PAD
                n.pd_object.y = n.line_pos * self.Y_SPACE + self.Y_PAD

    def num_lines(self):
        return len(self.lines)

    def num_elements(self, type):
        return len(self.elements(type))

    def elements(self, type):
        return list(filter(lambda x: x.type == type, self.nodes))

    def elements_in_line(self, type, line_pos: int):
        return list(filter(lambda x: x.type == type and x.line_pos == line_pos, self.nodes))

    def export(self, cnv: Canvas):
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


def parse_object_option(name: str, txt: str):
    if name == 'w':
        return {'w': int(txt)}
    elif name == 'x':
        return {'x': int(txt)}
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
    elif name == 'ax':
        return {'ax': int(txt)}
    elif name == 'ay':
        return {'ay': int(txt)}
    else:
        logging.warning(f"invalid object option: {txt}")
        return {}


def parse_object_options(arg: str) -> dict:
    res = {}
    arg_str = arg[1:-1]
    if len(arg_str) < 1:
        return res

    re_opt = re.compile(r"(\w{1,2})=(.+)")

    for opt in arg_str.split(","):
        res_opt = re.match(re_opt, opt)
        if res_opt:
            res.update(parse_object_option(res_opt.group(1), res_opt.group(2)))

    return res


def process_object_options(node: Node, opts: dict):
    # print(opts)

    if 'w' in opts:
        node.pd_object.fixed_width = opts['w']

    if 'x' in opts:
        node.char_pos = opts['x']

    if 'i' in opts:
        xin = opts.get('in_sig', 0) * [XLET_SOUND] + opts.get('in_ctl', 0) * [XLET_MESSAGE]
        node.pd_object.set_inlets(xin)

    if 'o' in opts:
        xout = opts.get('out_sig', 0) * [XLET_SOUND] + opts.get('out_ctl', 0) * [XLET_MESSAGE]
        node.pd_object.set_outlets(xout)

    if 'ax' in opts:
        node.obj_ax = int(opts['ax'])

    if 'ay' in opts:
        node.obj_ay = int(opts['ay'])
