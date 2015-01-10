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
from pdradio import PdRadio
from pdgcanvas import PdGCanvas
import os
import re
import imp
import sys

externals = {}


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
    elif name in ("hradio", "vradio"):
        return PdRadio.from_atoms(atoms)
    elif name == "cnv":
        return PdGCanvas.from_atoms(atoms[1:])
    # elif name in ("nbx", "vu"):
    #     return PdCoreGui(name, 0, 0, atoms[1:])
    elif find_external_object(name):
        return externals[name].create(atoms)
    else:
        return PdObject(name, 0, 0, 0, 0, atoms[1:])


def make_by_name(name, args=[], **kwargs):
    if name == "floatatom":
        return PdFloatAtom(0, 0, **kwargs)
    elif name == "bng":
        return PdBng(0, 0, **kwargs)
    else:
        return PdObject(name, 0, 0, 0, 0, args)


def find_external_object(name):
    rname = re.compile(r"^([a-z0-9~/]+)$")
    if not rname.match(name):
        return False

    mod_path = os.path.dirname(__file__) + "/externals/" + name
    if not os.path.exists(mod_path + ".py"):
        return False

    mod_dir = os.path.dirname(mod_path)
    mod_name = os.path.basename(mod_path)

    if mod_dir not in sys.path:
        sys.path.append(mod_dir)
    try:
        mod = __import__(mod_name)
        externals[name] = mod
        return True
    except ImportError:
        return None
