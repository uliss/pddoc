# /usr/bin/env python

#   Copyright (C) 2014 by Serge Poltavski                                 #
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


# -*- coding: utf-8 -*-

__author__ = 'Serge Poltavski'

from pdcomment import *

class PdPainter(object):

    def draw_canvas(self, canvas):
        pass

    def draw_comment(self, comment):
        print "Draw comment: #", comment.text

    def draw_message(self, message):
        print "Draw message [id:%i]: %s" % (message.id, message.to_string())

    def draw_object(self, object):
        print "Draw object: [id:%i] [%s]" % (object.id, " ".join(object.args))

    def draw_core_gui(self, gui):
        print "Draw core GUI: [id:%i] [%s]" % (gui.id, gui.name)

    def draw_subpatch(self, subpatch):
        print "Draw subpatch: [pd %s]" % (subpatch.name)

    def draw_graph(self, graph):
        print "Draw graph "

    def draw_connections(self, canvas):
        print "Draw connections "

