#!/usr/bin/env python
# coding=utf-8

#   Copyright (C) 2015 by Serge Poltavski                                 #
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


class AbstractVisitor(object):
    def visit_object(self, obj):
        raise NotImplementedError

    def visit_message(self, msg):
        raise NotImplementedError

    def visit_comment(self, comment):
        raise NotImplementedError

    def visit_canvas_begin(self, canvas):
        raise NotImplementedError

    def visit_canvas_end(self, canvas):
        raise NotImplementedError

    def visit_core_gui(self, gui):
        raise NotImplementedError

    def visit_connection(self, conn):
        raise NotImplementedError

    def skip_comment(self, comment):
        return False

    def skip_object(self, obj):
        return False

    def skip_message(self, msg):
        return False

    def skip_connection(self, conn):
        return False

    def skip_core_gui(self, conn):
        return False

    def skip_canvas(self, cnv):
        return False

    def skip_children(self, obj):
        return False
