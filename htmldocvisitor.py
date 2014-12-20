# /usr/bin/env python

# Copyright (C) 2014 by Serge Poltavski                                 #
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


class HtmlDocVisitor(object):
    def __init__(self):
        self._body = ""
        self._head = ""
        self._html5 = False

    def title_begin(self, t):
        self._head += "<title>PureData [%s] object</title>\n" % (t.text())


    def object_begin(self, obj):
        self._head += '<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>\n'

    def keywords_begin(self, k):
        self._head += '<meta name="keywords" content="%s"/>\n' % (" ".join(k.keywords()))

    def __str__(self):
        return '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">\n' + \
               "<html>\n<head>\n%s\n</head>\n<body>\n%s\n</body>\n</html>\n" % (self._head, self._body)




