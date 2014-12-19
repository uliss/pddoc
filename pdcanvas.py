# /usr/bin/env python

#   Copyright (C) 2014 by Serge Poltavski                                 #
#   serge.poltavski@gmail.com                                            #
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

__author__ = 'Serge Poltavski'

from pdobject import *

class PdCanvas(PdBaseObject):
    TYPE_NONE, TYPE_WINDOW, TYPE_SUBPATCH, TYPE_GRAPH = range(0, 4)

    def __init__(self, x, y, w, h, **kwargs):
        super(PdCanvas, self).__init__(x, y, w, h)
        self.objects = []
        self.id_counter = 0
        self.name = ""
        self.type = self.TYPE_NONE
        self.graphs = []
        self.subpatches = []

        if kwargs.has_key('name'):
            self.name = kwargs['name']

        if kwargs.has_key('open_on_load'):
            self.open_on_load = kwargs['open_on_load']

    def append_graph(self, obj):
        assert isinstance(obj, PdCanvas)
        assert obj.type == self.TYPE_GRAPH
        self.graphs.append(obj)

    def append_object(self, obj):
        assert issubclass(obj.__class__, PdBaseObject)

        if issubclass(obj.__class__, PdObject):
            obj.id = self.id_counter
            self.id_counter += 1

        self.objects.append(obj)

    def append_subpatch(self, obj):
        assert isinstance(obj, PdCanvas)
        assert obj.type == self.TYPE_SUBPATCH
        self.subpatches.append(obj)

    def get_object_by_id(self, id):
        for obj in self.objects:
            if obj.id == id:
                return obj

        return None

    def identify_objects(self):
        num = 0
        for obj in self.objects:
            if obj.has_id == True:
                obj.id = num
                num += 1
        pass

    def __str__(self):
        name = ""

        if self.type == self.TYPE_WINDOW:
            name = "Canvas "
        elif self.type == self.TYPE_GRAPH:
            name = "Graph "
        elif self.type == self.TYPE_SUBPATCH:
            name = "Subpatch "

        name += "\"%s\"" % (self.name)

        res = "%-30s (%i,%i %ix%i)\n" %(name, self.x, self.y, self.width, self.height)
        for obj in self.objects:
            res += "    " + str(obj)
            res += "\n"

        # res += "\n"
        # graphs
        for graph in self.graphs:
            res += str(graph)

        # res += "\n"
        # subpatches
        for sp in self.subpatches:
            res += str(sp)

        return res

    def draw(self, painter):
        if self.type == self.TYPE_NONE:
            return

        painter.draw_canvas(self)

        for obj in self.objects:
            obj.draw(painter)

        for graph in self.graphs:
            graph.draw(painter)

        for sp in self.subpatches:
            sp.draw(painter)

