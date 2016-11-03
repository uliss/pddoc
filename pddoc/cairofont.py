#!/usr/bin/env python
# coding=utf-8

# Copyright (C) 2015 by Serge Poltavski                                 #
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

import ctypes
import cairo
import os
import cairo
import pango
import pangocairo

_initialized = False


def create_cairo_font_face_for_file(filename, faceindex=0, loadoptions=0):
    global _initialized
    global _freetype_so
    global _cairo_so
    global _ft_lib
    global _surface

    CAIRO_STATUS_SUCCESS = 0
    FT_Err_Ok = 0

    if not _initialized:
        # find shared objects
        _freetype_so = ctypes.CDLL("/opt/local/lib/libfreetype.dylib")
        _cairo_so = ctypes.CDLL("/opt/local/lib/libcairo.dylib")

        _cairo_so.cairo_ft_font_face_create_for_ft_face.restype = ctypes.c_void_p
        _cairo_so.cairo_ft_font_face_create_for_ft_face.argtypes = [ctypes.c_void_p, ctypes.c_int]
        _cairo_so.cairo_set_font_face.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        _cairo_so.cairo_font_face_status.argtypes = [ctypes.c_void_p]
        _cairo_so.cairo_status.argtypes = [ctypes.c_void_p]

        # initialize freetype
        _ft_lib = ctypes.c_void_p()
        if FT_Err_Ok != _freetype_so.FT_Init_FreeType(ctypes.byref(_ft_lib)):
            raise "Error initialising FreeType library."

        class PycairoContext(ctypes.Structure):
            _fields_ = [("PyObject_HEAD", ctypes.c_byte * object.__basicsize__),
                        ("ctx", ctypes.c_void_p),
                        ("base", ctypes.c_void_p)]

        _surface = cairo.ImageSurface(cairo.FORMAT_A8, 0, 0)

        _initialized = True

    # create freetype face
    ft_face = ctypes.c_void_p()
    cairo_ctx = cairo.Context(_surface)
    cairo_t = PycairoContext.from_address(id(cairo_ctx)).ctx

    if FT_Err_Ok != _freetype_so.FT_New_Face(_ft_lib, filename, faceindex, ctypes.byref(ft_face)):
        raise Exception("Error creating FreeType font face for " + filename)

    # create cairo font face for freetype face
    cr_face = _cairo_so.cairo_ft_font_face_create_for_ft_face(ft_face, loadoptions)
    if CAIRO_STATUS_SUCCESS != _cairo_so.cairo_font_face_status(cr_face):
        raise Exception("Error creating cairo font face for " + filename)

    _cairo_so.cairo_set_font_face(cairo_t, cr_face)
    if CAIRO_STATUS_SUCCESS != _cairo_so.cairo_status(cairo_t):
        raise Exception("Error creating cairo font face for " + filename)

    face = cairo_ctx.get_font_face()

    return face


if __name__ == '__main__':
    share_path = os.path.join(os.path.dirname(__file__), "share", "terminus.ttf")
    face = create_cairo_font_face_for_file(share_path, 0)

    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 128, 128)
    ctx = cairo.Context(surface)
    ctx.set_font_face(face)
    ctx.set_font_size(14)
    ctx.move_to(0, 44)
    ctx.show_text("Hello,")
    ctx.move_to(30, 74)
    ctx.show_text("world!")

    del ctx

    surface.write_to_png("hello.png")
