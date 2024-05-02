#!/usr/bin/env python
#   Copyright (C) 2018 by Serge Poltavski                                 #
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

import argparse
import json
import logging
import math
import os

from pddoc.pd.canvas import Canvas
from pddoc.pd.coregui import Color
from pddoc.pd.gcanvas import GCanvas
from pddoc.pd.message import Message
from pddoc.pd.obj import PdObject
from pddoc.pd.pdexporter import PdExporter

GRID = 25


def obj_props(json):
    lst = []

    def props(el):
        if el['type'] in ('vslider', 'hslider', 'nentry', 'checkbox', 'button'):
            return ['@' + el['label']]
        elif 'items' in el:
            lst = []
            for i in el['items']:
                lst += props(i)

            return lst

        return []

    for k, v in json.items():
        if k == "ui":
            for ui in v:
                lst += props(ui)

    return lst


def obj_prop_defs(json, d):
    def props(el):
        if el['type'] in ('vslider', 'hslider', 'nentry', 'checkbox', 'button'):
            if 'init' in el:
                d['@' + el['label']] = el['init']
        elif 'items' in el:
            for i in el['items']:
                props(i)

    for k, v in json.items():
        if k == "ui":
            for ui in v:
                props(ui)


def export_ui(cnv: Canvas, counter: int, prop_route, el, x: int, y: int, main_obj: PdObject, **kwargs):
    MSG_XOFF = 250

    if el['type'] in ('vslider', 'hslider'):
        lbl_txt = "{0}:".format(el['label'])
        if 'meta' in el:
            for m in el['meta']:
                if 'unit' in m:
                    lbl_txt = "{0}({1}):".format(el['label'], m['unit'])

        y += 18
        obj = PdObject('ui.slider', args=["@size", "125", "12", "@active_scale", "1",
                                          "@label", lbl_txt, "@label_side", "top",
                                          "@label_align", "left", "@fontsize", "10"])
        obj.append_arg("@presetname")
        obj.append_arg("/gui/\\$1/{0}/slider{1}".format(main_obj.name, counter))
        obj.x = (x + 2)
        obj.y = y
        cnv.append_object(obj)

        sync = PdObject("sync")
        sync.x = (x + 205)
        sync.y = y
        cnv.append_object(sync)

        # range and type checks
        has_min = 'min' in el
        has_max = 'max' in el
        is_meta_int = 'meta' in el and 'type' in el['meta'] and (el['meta']['type'] == 'int')
        is_step_int = 'step' in el and (el['step'] == 1)

        nbx = PdObject('ui.number', args=["@size", "50", "12"])
        nbx.x = (x + 135)
        nbx.y = y
        cnv.append_object(nbx)

        cnv.add_connection(obj.id, 0, sync.id, 0, check_xlets=False)
        cnv.add_connection(sync.id, 0, obj.id, 0, check_xlets=False)
        cnv.add_connection(nbx.id, 0, sync.id, 1, check_xlets=False)
        cnv.add_connection(sync.id, 1, nbx.id, 0, check_xlets=False)

        if has_min:
            obj.append_arg("@min")
            obj.append_arg(str(el['min']))
            nbx.append_arg("@min")
            nbx.append_arg(str(el['min']))

        if has_max:
            obj.append_arg("@max")
            obj.append_arg(str(el['max']))
            nbx.append_arg("@max")
            nbx.append_arg(str(el['max']))

        ndig = 3
        if has_min and has_max:
            rng = abs(el['max'] - el['min'])
            ndig = int(math.ceil(math.log10(rng))) - 4

        if is_meta_int or is_step_int:
            ndig = 0

        nbx.append_arg("@digits")
        nbx.append_arg(str(abs(ndig)))

        msg = Message(x + MSG_XOFF, y, ["@" + el['label'], "$1"])
        cnv.append_object(msg)
        cnv.add_connection(obj.id, 0, msg.id, 0, check_xlets=False)
        cnv.add_connection(msg.id, 0, main_obj.id, 0, check_xlets=False)
        cnv.add_connection(prop_route.id, counter, obj.id, 0, check_xlets=False)

        y += 12
        counter += 1
    elif el['type'] in ('nentry'):
        lbl_txt = "{0}:".format(el['label'])
        if 'meta' in el and 'unit' in el['meta']:
            lbl_txt = "{0}({1}):".format(el['label'], el['meta']['unit'])

        y += 18
        nbx = PdObject('ui.number', args=["@size", "60", "12",
                                          "@label", lbl_txt, "@label_side", "top",
                                          "@label_align", "left", "@fontsize", "10"])
        nbx.append_arg("@presetname")
        nbx.append_arg("/gui/\\$1/{0}/numbox{1}".format(main_obj.name, counter))
        nbx.x = (x + 2)
        nbx.y = y

        if 'min' in el:
            nbx.append_arg("@min")
            nbx.append_arg(str(el['min']))

        if 'max' in el:
            nbx.append_arg("@max")
            nbx.append_arg(str(el['max']))

        if 'step' in el:
            nbx.append_arg("@step")
            nbx.append_arg(str(el['step']))

        cnv.append_object(nbx)

        msg = Message(x + MSG_XOFF, y, ["@" + el['label'], "$1"])
        cnv.append_object(msg)
        cnv.add_connection(nbx.id, 0, msg.id, 0, check_xlets=False)
        cnv.add_connection(msg.id, 0, main_obj.id, 0, check_xlets=False)
        cnv.add_connection(prop_route.id, counter, nbx.id, 0, check_xlets=False)

        y += 12
        counter += 1
    elif el['type'] in ('checkbox', 'button'):
        is_bypass = (el['type'] == 'checkbox' and el['label'] == 'bypass')
        if is_bypass:
            tgl = PdObject('ui.toggle', args=["@size", "12", "12",
                                              "@label", el['label'], "@label_side", "left",
                                              "@label_align", "right", "@fontsize", "10"])

            wd = kwargs.get("width", 200)
            tgl.x = (wd - 15)
            tgl.y = (kwargs.get("top", 200))
        else:
            tgl = PdObject('ui.toggle', args=["@size", "12", "12",
                                              "@label", el['label'], "@label_side", "right",
                                              "@label_align", "left", "@fontsize", "10"])
            tgl.x = (x + 2)
            tgl.y = (y + 8)

        if el["label"] != "gate":
            tgl.append_arg("@presetname")
            tgl.append_arg("/gui/\\$1/{0}/checkbox{1}".format(main_obj.name, counter))

        cnv.append_object(tgl)

        msg = Message(x + MSG_XOFF, y, ["@" + el['label'], "$1"])
        cnv.append_object(msg)
        cnv.add_connection(tgl.id, 0, msg.id, 0, check_xlets=False)
        cnv.add_connection(msg.id, 0, main_obj.id, 0, check_xlets=False)
        cnv.add_connection(prop_route.id, counter, tgl.id, 0, check_xlets=False)

        if not is_bypass:
            y += 18

        counter += 1
    elif 'items' in el:
        for i in el['items']:
            y, counter = export_ui(cnv, counter, prop_route, i, x, y, main_obj, **kwargs)

    return y, counter


def main():
    y_off = 0
    arg_parser = argparse.ArgumentParser(description='Create PureData GUI abstraction by Faust JSON file')
    arg_parser.add_argument('json', metavar='JSON', help="Faust json file")

    args = vars(arg_parser.parse_args())
    in_file = args['json']

    if not os.path.exists(in_file):
        logging.error("File not exists: \"%s\"", in_file)
        exit(1)

    fp = open(in_file)

    json_root = json.load(fp)
    fp.close()

    wd = 950
    ht = 600

    cnv = Canvas(0, 0, wd, ht, name="test")
    cnv.type = Canvas.TYPE_WINDOW

    n_ins = 0
    n_outs = 0
    name = ""

    for k, v in json_root.items():
        if k == "inputs":
            n_ins = int(v)
            continue

        if k == "outputs":
            n_outs = int(v)
            continue

        if k == "name":
            name = v
            continue

        if k == "meta":
            for item in v:
                if "ui" in item and item["ui"] == "disable":
                    logging.warning("Skipping UI generation for \"%s\"", in_file)
                    return

    main_obj = PdObject(name + '~')
    main_obj.x = GRID
    main_obj.y = (GRID * 5)
    cnv.append_object(main_obj)

    # create signal inlets
    x_off = GRID
    for i in range(n_ins):
        inlet = PdObject('inlet~')
        inlet.x = x_off
        inlet.y = GRID
        x_off += GRID * 4
        cnv.append_object(inlet)
        cnv.add_connection(inlet.id, 0, main_obj.id, i, check_xlets=False)

    CTL_XOFF = 300
    # create control inlet
    ctl_inlet = PdObject('inlet')
    ctl_inlet.x = (x_off + CTL_XOFF)
    ctl_inlet.y = GRID
    cnv.append_object(ctl_inlet)

    # object name router
    # [route OBJ_NAME * .]
    # |               / /
    # [route..          ]
    in_route = PdObject('route', args=[name, '*', '.'])
    in_route.x = (x_off + CTL_XOFF)
    in_route.y = (GRID * 5)
    cnv.append_object(in_route)
    cnv.add_connection(ctl_inlet.id, 0, in_route.id, 0)

    # check route property
    # [route.prop]
    is_prop = PdObject('route.prop', x=x_off + CTL_XOFF + 200, y=GRID * 6)
    cnv.append_object(is_prop)
    cnv.add_connection(in_route.id, 3, is_prop.id, 0, check_xlets=False)

    # [msg *]
    msg_ast = PdObject('msg', x=x_off + CTL_XOFF + 50, y=GRID * 8, args=['*'])
    cnv.append_object(msg_ast)
    cnv.add_connection(in_route.id, 1, msg_ast.id, 0, check_xlets=False)

    # property checker
    prop_route = PdObject('route')
    for p in obj_props(json_root):
        prop_route.append_arg(p)

    prop_route.append_arg('default')
    prop_route.append_arg('reset')

    cnv.append_object(prop_route)
    prop_route.x = (x_off + CTL_XOFF)
    prop_route.y = (GRID * 10)
    # connect target route
    cnv.add_connection(in_route.id, 0, prop_route.id, 0, check_xlets=False)
    # connect '*'
    cnv.add_connection(in_route.id, 1, prop_route.id, 0, check_xlets=False)
    # connect '.'
    cnv.add_connection(in_route.id, 2, prop_route.id, 0, check_xlets=False)
    # connect 'prop ok'
    cnv.add_connection(is_prop.id, 0, prop_route.id, 0, check_xlets=False)

    # error print
    # [t b a          ]
    # |               |
    # [supported...( [print unknown message]
    # |
    # [print]
    err_x = x_off + 550
    err_trig = PdObject('t', x=err_x, y=GRID * 14, args=['b', 'a'])
    cnv.append_object(err_trig)
    cnv.add_connection(prop_route.id, len(prop_route.outlets()) - 1, err_trig.id, 0)

    err_msg_args = 'supported messages are:'.split(' ') + prop_route.args
    err_msg = Message(err_x, GRID * 15, atoms=err_msg_args)
    cnv.append_object(err_msg)
    cnv.add_connection(err_trig.id, 0, err_msg.id, 0)

    err_msg_print0 = PdObject('print', x=err_x, y=GRID * 17)
    cnv.append_object(err_msg_print0)
    cnv.add_connection(err_msg.id, 0, err_msg_print0.id, 0)

    print_err_prop = PdObject('print', args=[f'[g{name}~] unknown message'])
    print_err_prop.x = (err_x + 50)
    print_err_prop.y = (GRID * 17)
    cnv.append_object(print_err_prop)
    cnv.add_connection(err_trig.id, 1, print_err_prop.id, 0)

    # default values
    default_msg = Message(x_off + 200, GRID * 3, atoms=[])
    kv = {}
    obj_prop_defs(json_root, kv)
    for k, v in kv.items():
        default_msg.append_arg(k)
        default_msg.append_arg(v)
        default_msg.append_arg(',')

    cnv.append_object(default_msg)
    cnv.add_connection(default_msg.id, 0, prop_route.id, 0)

    # connect to default
    def_idx = prop_route.args.index('default')
    if def_idx >= 0:
        cnv.add_connection(prop_route.id, def_idx, default_msg.id, 0)

    # reset message
    # [route ... reset]
    # |
    # [t b b  ]
    # |       |
    # [reset( [default(
    reset_trig = PdObject("t", GRID, GRID * 2, args=['b', 'b'])
    cnv.append_object(reset_trig)
    reset_msg = Message(GRID, GRID * 3, atoms=['reset'])
    cnv.append_object(reset_msg)
    cnv.add_connection(reset_trig.id, 1, reset_msg.id, 0, check_xlets=False)
    cnv.add_connection(reset_trig.id, 0, default_msg.id, 0, check_xlets=False)
    cnv.add_connection(reset_msg.id, 0, main_obj.id, 0, check_xlets=False)
    reset_idx = prop_route.args.index('reset')
    if reset_idx >= 0:
        cnv.add_connection(prop_route.id, reset_idx, reset_trig.id, 0, check_xlets=False)

    default_loadbang = PdObject('msg.onload')
    default_loadbang.x = (x_off + 200)
    default_loadbang.y = GRID
    cnv.append_object(default_loadbang)
    cnv.add_connection(default_loadbang.id, 0, default_msg.id, 0, check_xlets=False)

    # create signal outlets
    x_off = GRID * 20
    for i in range(n_outs):
        outlet = PdObject('outlet~')
        outlet.x = x_off
        outlet.y = (GRID * 22)
        x_off += GRID * 4
        cnv.append_object(outlet)
        cnv.add_connection(main_obj.id, i, outlet.id, 0, check_xlets=False)

    # create control outlet
    outlet = PdObject('outlet ctl')
    outlet.x = x_off
    outlet.y = (GRID * 22)
    cnv.append_object(outlet)
    # connect route to unmatched objects
    cnv.add_connection(is_prop.id, 1, outlet.id, 0, check_xlets=False)
    # connect route to '*' objects
    cnv.add_connection(msg_ast.id, 0, outlet.id, 0, check_xlets=False)

    # background
    bg_cnv = GCanvas(3, 202, size=8, width=198, height=18, bg_color="#AAAAAA")
    cnv.append_object(bg_cnv)

    # label
    lbl_cnv = GCanvas(3, 202, size=8, width=198, height=18, label_xoff=3, label_yoff=9, font_size=12)
    lbl_cnv._bg_color = Color(100, 100, 100)
    lbl_cnv._label_color = Color(255, 255, 255)
    lbl_cnv._label = f"[{name}~]"
    cnv.append_object(lbl_cnv)

    for k, v in json_root.items():
        if k == "ui":
            y_off = 218
            c = 0
            for ui in v:
                y_off, _ = export_ui(cnv, c, prop_route, ui, 10, y_off, main_obj, top=205, width=200)

    cnv.set_graph_on_parent(True, xoff=2, yoff=200, width=200, height=y_off - 200 + 8, hide_args=True)
    bg_cnv.height = y_off - 200 + 3

    pd_exporter = PdExporter()
    cnv.traverse(pd_exporter)
    out_file = f'g{name}~.pd'
    pd_exporter.save(out_file)


if __name__ == '__main__':
    main()
