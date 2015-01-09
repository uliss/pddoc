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

from pdfloatatom import PdFloatAtom
from pdcoregui import PdCoreGui
from pdobject import PdObject
from pdbng import PdBng
from pdtoggle import PdToggle
from pdslider import PdSlider


def make(atoms):
    assert isinstance(atoms, list)
    assert len(atoms) > 0
    name = atoms[0]

    if name == "floatatom":
        return PdFloatAtom.from_atoms(atoms[1:])
    elif name == "bng":
        return PdBng.from_atoms(atoms[1:])
    elif name == "tgl":
        return PdToggle.from_atoms(atoms[1:])
    elif name in ("hsl", "vsl"):
        return PdSlider.from_atoms(atoms)
    elif name in ("cnv", "hradio", "nbx", "vradio", "vu"):
        return PdCoreGui(name, 0, 0, atoms[1:])
    else:
        return PdObject(name, 0, 0)


def make_by_name(name, args = [], **kwargs):
    if name == "floatatom":
        return PdFloatAtom(0, 0, **kwargs)
    elif name == "bng":
        return PdBng(0, 0, **kwargs)
    else:
        return PdObject(name, 0, 0, 0, 0, args)