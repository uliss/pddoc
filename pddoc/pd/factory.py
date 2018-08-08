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

import os
import re
import sys
import logging
import importlib

from .floatatom import FloatAtom
from . import EXTERNALS_DIR
from .obj import PdObject
from .bng import PdBng
from .toggle import PdToggle
from .slider import PdSlider, PdHSlider, PdVSlider
from .radio import Radio, PdVRadio, PdHRadio
from .gcanvas import GCanvas
from .nbx import Nbx
from .vu import PdVu
from .symbolatom import PdSymbolAtom

sys.path.append(EXTERNALS_DIR)

externals = {}
not_found = set()
imports = []


def _clean_ext_name(name):
    if '.' in name:
        name = name.replace('.', '_')
    if '~' in name:
        name = name.replace('~', '')

    return name


def make(atoms):
    assert isinstance(atoms, list)
    assert len(atoms) > 0
    name = atoms[0]

    if name == "floatatom":
        return FloatAtom.from_atoms(atoms[1:])
    elif name == "symbolatom":
        return PdSymbolAtom.from_atoms(atoms[1:])
    # elif name == "declare":
    #     print atoms
    #     assert False
    elif name == "bng":
        return PdBng.from_atoms(atoms[1:])
    elif name == "tgl":
        return PdToggle.from_atoms(atoms[1:])
    elif name in ("hsl", "vsl"):
        return PdSlider.from_atoms(atoms)
    elif name in ("hradio", "vradio"):
        return Radio.from_atoms(atoms)
    elif name == "cnv":
        return GCanvas.from_atoms(atoms[1:])
    elif name == "vu":
        return PdVu.from_atoms(atoms)
    elif name == "nbx":
        return Nbx.from_atoms(atoms)
    elif name not in not_found:
        if find_external_object(name):
            return externals[_clean_ext_name(name)].create(atoms)
    else:
        pass

    # handle import
    if name == "import":
        add_import(atoms[1])

    return PdObject(name, 0, 0, 0, 0, atoms[1:])


def add_import(name):
    import_path = os.path.join(EXTERNALS_DIR, name)
    if import_path in imports:
        return

    if os.path.exists(import_path):
        logging.debug("import path added: \"%s\"", import_path)
        imports.append(import_path)
    else:
        logging.warning("import path not found: \"%s\"", name)


def make_by_name(name, args=None, **kwargs):
    if args is None:
        args = []
    if name == "floatatom":
        return FloatAtom(0, 0, **kwargs)
    elif name == "symbolatom":
        return PdSymbolAtom(0, 0, **kwargs)
    elif name == "bng":
        return PdBng(0, 0, **kwargs)
    elif name == "tgl":
        return PdToggle(0, 0, **kwargs)
    elif name == "nbx":
        return Nbx(0, 0, **kwargs)
    elif name == "hslider":
        return PdHSlider(0, 0, **kwargs)
    elif name == "vslider":
        return PdVSlider(0, 0, **kwargs)
    elif name == "hradio":
        return PdHRadio(0, 0, **kwargs)
    elif name == "vradio":
        return PdVRadio(0, 0, **kwargs)
    elif name == "vu":
        return PdVu(0, 0, **kwargs)
    elif name not in not_found and find_external_object(name):
        return externals[_clean_ext_name(name)].create_by_name(name, args, **kwargs)
    else:
        return PdObject(name, 0, 0, 0, 0, args)


def _find_in_externals(name):
    mod_path = os.path.join(EXTERNALS_DIR, name)
    if os.path.exists(mod_path + ".py"):
        return mod_path
    else:
        return None


def _find_in_imports(name):
    for path in imports:
        mod_path = os.path.join(path, name)
        if os.path.exists(mod_path + ".py"):
            return mod_path

    return None


def find_external_object(name):
    clean_ext_name = _clean_ext_name(name)

    if clean_ext_name in externals:
        return True

    rname = re.compile(r"^([-a-zA-Z0-9~/*=+><!_%|&.^]+)$")
    if not rname.match(clean_ext_name):
        logging.warning("name contains invalid characters: [%s]", clean_ext_name)
        return False

    mod_path = _find_in_externals(clean_ext_name)
    if not mod_path:
        mod_path = _find_in_imports(clean_ext_name)
    if not mod_path:
        not_found.add(clean_ext_name)
        return False

    mod_dir = os.path.dirname(mod_path)
    mod_name = os.path.basename(mod_path)

    if mod_dir not in sys.path:
        sys.path.append(mod_dir)
    try:
        mod = importlib.import_module(mod_name, 'ceammc')
        # mod = __import__(mod_name, globals(), locals(), [name], 0)
        externals[clean_ext_name] = mod
        logging.debug("module \"%s.py\" imported from \"%s\".", mod_name, mod_dir)
        return True
    except ImportError as e:
        logging.error("Error while importing extension: %s - \"%s\". Search paths: = %s", mod_name, e, "\n\t".join(sys.path))
        not_found.add(clean_ext_name)
        return None
