#!/usr/bin/env python
# coding=utf-8

# Copyright (C) 2014 by Serge Poltavski                                   #
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

import six
import logging

from .baseobject import BaseObject
from .xletcalculator import XletCalculator
from .xletpatchlookup import XletPatchLookup
from .abstractvisitor import AbstractVisitor


class PdObject(BaseObject):
    xlet_calculator = XletCalculator()
    xlet_patch_finder = XletPatchLookup()
    # calculates xlets number
    XMETHOD_CALCULATE = 0
    # no calculation, xlets should be defined manually by calling set_inlets
    XMETHOD_EXPLICIT = 1
    # cache for external patches
    _patch_cache = {}
    # brect calc
    _brect_calc = None
    # fixed brect
    _fixed_size = False

    def __init__(self, name, x=0, y=0, w=0, h=0, args=None):
        BaseObject.__init__(self, x, y, w, h)
        if args is None:
            args = []
        assert isinstance(name, six.string_types)
        assert len(name) > 0

        self._name = name

        assert isinstance(args, list)
        self._args = args

        self._inlets = []
        self._outlets = []
        self._xlets_method = self.XMETHOD_CALCULATE
        self._gop = False

        if self.name in PdObject._patch_cache:
            if PdObject._patch_cache[self.name] is None:
                self._gop = False
            else:
                self._gop = True
                x, y, w, h = PdObject._patch_cache[self.name].gop_rect()
                self._width = w
                self._height = h
        else:
            # objname.pd patch found
            if self.xlet_patch_finder.has_object(self.name):
                import parser as pd

                obj = self.xlet_patch_finder.get_object(self.name)
                parser = pd.Parser()
                if not parser.parse(obj.path):
                    logging.error("can't parse patch: \"{0:s}\"".format(obj.path))
                    self._gop = False
                    PdObject._patch_cache[self.name] = None

                # success
                if parser.canvas.is_graph_on_parent():
                    self._gop = True
                    PdObject._patch_cache[self.name] = parser.canvas
                    x, y, w, h = parser.canvas.gop_rect()
                    self._width = w
                    self._height = h
                else:
                    self._gop = False
            else:
                PdObject._patch_cache[self.name] = None

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, n):
        assert isinstance(n, six.string_types)
        assert len(n) > 0
        self._name = n

    @property
    def args(self):
        return self._args

    def append_arg(self, a):
        self._args.append(a)

    @staticmethod
    def brect_calc():
        from .brectcalculator import  BRectCalculator

        if not PdObject._brect_calc:
            PdObject._brect_calc = BRectCalculator()

        return PdObject._brect_calc

    @classmethod
    def add_object_xlet_info(cls, name, inlets, outlets):
        cls.xlet_calculator.mem_db.add_object(name, inlets, outlets)

    @classmethod
    def remove_object_xlet_info(cls, name):
        cls.xlet_calculator.mem_db.remove_object(name)

    def num_args(self):
        return len(self._args)

    def args_to_string(self):
        res = ""

        esc_args = []
        for arg in self.args:
            esc_args.append(PdObject.unescape(arg))

        for arg in esc_args:
            if arg == ",":
                res += ", "
            elif arg == ";":
                res += ";"
            else:
                res += " " + arg

        res = " ".join(res.strip().split())
        return res

    def to_string(self):
        res = PdObject.unescape(self.name) + ' ' + self.args_to_string()
        return res.strip()

    def __str__(self):
        res = "[%-40s {x:%i,y:%i,id:%i}" % (self.to_string() + "]", self.x, self.y, self.id)
        return res

    def draw(self, painter):
        if self._gop:
            canvas = PdObject._patch_cache[self.name]
            painter.draw_gop(self, canvas)
        else:
            painter.draw_object(self)

    def inlets(self):
        if self._xlets_method == self.XMETHOD_EXPLICIT:
            return self._inlets
        elif self._xlets_method == self.XMETHOD_CALCULATE:
            return PdObject.xlet_calculator.inlets(self)
        else:
            return []

    def outlets(self):
        if self._xlets_method == self.XMETHOD_EXPLICIT:
            return self._outlets
        elif self._xlets_method == self.XMETHOD_CALCULATE:
            return PdObject.xlet_calculator.outlets(self)
        else:
            return []

    def traverse(self, visitor):
        assert isinstance(visitor, AbstractVisitor)

        if visitor.skip_object(self):
            return

        visitor.visit_object(self)

    def calc_brect(self, use_cached=True):
        if use_cached and (self._width != 0 and self._height != 0):
            return

        brect = self.brect_calc().object_brect(self)
        self._width = brect[2]
        self._height = brect[3]
