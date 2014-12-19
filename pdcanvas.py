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
        self._name = ""
        self.type = self.TYPE_NONE
        self.graphs = []
        self.subpatches = []
        self.connections = {}

        if kwargs.has_key('name'):
            self._name = kwargs['name']

        if kwargs.has_key('open_on_load'):
            self.open_on_load = kwargs['open_on_load']

    def name(self):
        return self._name

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

    def find_object_by_id(self, oid):
        for obj in self.objects:
            if issubclass(obj.__class__, PdObject):
                if obj.id == oid:
                    return obj

        return None

    def make_connection_key(self, sid, soutl, did, dinl):
        return "%i %i %i %i" % (sid, soutl, did, dinl)

    def add_connection(self, sid, soutl, did, dinl):
        src_obj = self.find_object_by_id(sid)
        dest_obj = self.find_object_by_id(did)
        if src_obj and dest_obj:
            ckey = self.make_connection_key(sid, soutl, did, dinl)
            self.connections[ckey] = (src_obj, soutl, dest_obj, dinl)

    def remove_connection(self, sid, soutl, did, dinl):
        ckey = self.make_connection_key(sid, soutl, did, dinl)
        del self.connections[ckey]

    def connect(self, args):
        assert len(args) == 4
        src_id = int(args[0])
        src_outl = int(args[1])
        dest_id = int(args[2])
        dest_inl = int(args[3])

        self.add_connection(src_id, src_outl, dest_id, dest_inl)

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

        if self.type == self.TYPE_SUBPATCH:
            painter.draw_subpatch(self)
        elif self.type == self.TYPE_GRAPH:
            painter.draw_graph(self)
        elif self.type == self.TYPE_WINDOW:
            painter.draw_canvas(self)

            for obj in self.objects:
                obj.draw(painter)

            for graph in self.graphs:
                graph.draw(painter)

            for sp in self.subpatches:
                sp.draw(painter)

            painter.draw_connections(self)

    def inlets(self):
        res = []

        for o in self.objects:
            if issubclass(o.__class__, PdObject):
                if o.name() == "inlet":
                    res.append(self.XLET_MESSAGE)
                elif o.name() == "inlet~":
                    res.append(self.XLET_SOUND)

        return res

    def outlets(self):
        res = []

        for o in self.objects:
            if issubclass(o.__class__, PdObject):
                if o.name() == "outlet":
                    res.append(self.XLET_MESSAGE)
                elif o.name() == "outlet~":
                    res.append(self.XLET_SOUND)

        return res