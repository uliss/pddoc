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
import logging
import os
import json

from pddoc.pd import Canvas, PdExporter, PdObject, Comment, Message
from pddoc.pd.gcanvas import GCanvas
from pddoc.pd.coregui import Color

GRID = 25

def obj_props(json):
    lst = []

    def props(el):
        if el['type'] in ('vslider', 'hslider', 'nentry', 'checkbox'):
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
        if el['type'] in ('vslider', 'hslider', 'nentry', 'checkbox'):
            if 'init' in el:
                d['@' + el['label']] = el['init']
        elif 'items' in el:
            for i in el['items']:
                props(i)

    for k, v in json.items():
        if k == "ui":
            for ui in v:
                props(ui)

def export_ui(cnv, counter, prop_route, el, x, y, main_obj):
    MSG_XOFF = 250

    if el['type'] in ('vslider', 'hslider'):
        lbl_txt = "{0}:".format(el['label'])
        if 'meta' in el:
            for m in el['meta']:
                if 'unit' in m:
                     lbl_txt = "{0}({1}):".format(el['label'], m['unit'])

        lbl = Comment(x, y, args=[lbl_txt])
        cnv.append_object(lbl)
        y += 19

        obj = PdObject('ui.slider', args=["@size", "120", "12", "@active_scale", "1"])
        obj.append_arg("@presetname")
        obj.append_arg("/gui/{0}/slider{1}".format(main_obj.name, counter))
        obj.set_x(x + 2)
        obj.set_y(y)

        cnv.append_object(obj)

        nbx = PdObject('ui.number', args=["@size", "40", "12", "@digits", "3"])
        nbx.set_x(x + 130)
        nbx.set_y(y)
        cnv.append_object(nbx)
        cnv.add_connection(obj.id, 0, nbx.id, 0, check_xlets=False)

        if 'min' in el:
            obj.append_arg("@min")
            obj.append_arg(str(el['min']))
            nbx.append_arg("@min")
            nbx.append_arg(str(el['min']))

        if 'max' in el:
            obj.append_arg("@max")
            obj.append_arg(str(el['max']))
            nbx.append_arg("@max")
            nbx.append_arg(str(el['max']))

        set_msg = PdObject('msg', args=['set'])
        set_msg.set_x(x + 180)
        set_msg.set_y(y)
        cnv.append_object(set_msg)
        cnv.add_connection(nbx.id, 0, set_msg.id, 0, check_xlets=False)
        cnv.add_connection(set_msg.id, 0, obj.id, 0, check_xlets=False)

        msg = Message(x + MSG_XOFF, y, ["@" + el['label'], "$1"])
        cnv.append_object(msg)
        cnv.add_connection(obj.id, 0, msg.id, 0, check_xlets=False)
        cnv.add_connection(msg.id, 0, main_obj.id, 0, check_xlets=False)
        cnv.add_connection(prop_route.id, counter, obj.id, 0, check_xlets=False)

        y += 14
        counter += 1
    elif el['type'] in ('nentry'):
        lbl_txt = "{0}:".format(el['label'])
        if 'meta' in el and 'unit' in el['meta']:
            lbl_txt = "{0}({1}):".format(el['label'], el['meta']['unit'])

        lbl = Comment(x, y, args=[lbl_txt])
        cnv.append_object(lbl)
        y += 19

        nbx = PdObject('ui.number', args=["@size", "60", "12"])
        nbx.append_arg("@presetname")
        nbx.append_arg("/gui/{0}/numbox{1}".format(main_obj.name, counter))
        nbx.set_x(x + 2)
        nbx.set_y(y)

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

        y += 14
        counter += 1
    elif el['type'] in ('checkbox', 'button'):
        tgl = PdObject('ui.toggle', args=["@size", "12", "12"])
        tgl.set_x(x + 2)
        tgl.set_y(y + 8)
        tgl.append_arg("@presetname")
        tgl.append_arg("/gui/{0}/checkbox{1}".format(main_obj.name, counter))

        cnv.append_object(tgl)

        lbl = Comment(x + 16, y + 3, args=[el['label']])
        cnv.append_object(lbl)

        msg = Message(x + MSG_XOFF, y, ["@" + el['label'], "$1"])
        cnv.append_object(msg)
        cnv.add_connection(tgl.id, 0, msg.id, 0, check_xlets=False)
        cnv.add_connection(msg.id, 0, main_obj.id, 0, check_xlets=False)
        cnv.add_connection(prop_route.id, counter, tgl.id, 0, check_xlets=False)

        y += 20
        counter += 1
    elif 'items' in el:
        for i in el['items']:
            y, counter = export_ui(cnv, counter, prop_route, i, x, y, main_obj)

    return y, counter


def main():
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


    main_obj = PdObject(name + '~')
    main_obj.set_x(GRID)
    main_obj.set_y(GRID * 5)
    cnv.append_object(main_obj)

    # create signal inlets
    x_off = GRID
    for i in range(n_ins):
        inlet = PdObject('inlet~')
        inlet.set_x(x_off)
        inlet.set_y(GRID)
        x_off += GRID * 4
        cnv.append_object(inlet)
        cnv.add_connection(inlet.id, 0, main_obj.id, i, check_xlets=False)

    CTL_XOFF = 300
    # create control inlet
    ctl_inlet = PdObject('inlet')
    ctl_inlet.set_x(x_off + CTL_XOFF)
    ctl_inlet.set_y(GRID)
    cnv.append_object(ctl_inlet)

    in_route = PdObject('route', args=[name])
    in_route.set_x(x_off + CTL_XOFF)
    in_route.set_y(GRID * 8)
    cnv.append_object(in_route)
    cnv.add_connection(ctl_inlet.id, 0, in_route.id, 0)

    # property checker
    prop_route = PdObject('route')
    for p in obj_props(json_root):
        prop_route.append_arg(p)

    cnv.append_object(prop_route)
    prop_route.set_x(x_off + CTL_XOFF)
    prop_route.set_y(GRID * 10)
    cnv.add_connection(in_route.id, 0, prop_route.id, 0, check_xlets=False)

    print_err_prop = PdObject('print', args=['unknown property'])
    print_err_prop.set_x(x_off + 550)
    print_err_prop.set_y(GRID * 14)
    cnv.append_object(print_err_prop)
    cnv.add_connection(prop_route.id, len(prop_route.outlets())-1, print_err_prop.id, 0)

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

    default_loadbang = PdObject('msg.onload')
    default_loadbang.set_x(x_off + 200)
    default_loadbang.set_y(GRID)
    cnv.append_object(default_loadbang)
    cnv.add_connection(default_loadbang.id, 0, default_msg.id, 0, check_xlets=False)

    # create signal outlets
    x_off = GRID * 20
    for i in range(n_outs):
        outlet = PdObject('outlet~')
        outlet.set_x(x_off)
        outlet.set_y(GRID * 22)
        x_off += GRID * 4
        cnv.append_object(outlet)
        cnv.add_connection(main_obj.id, i, outlet.id, 0, check_xlets=False)

    # create control outlet
    outlet = PdObject('outlet ctl')
    outlet.set_x(x_off)
    outlet.set_y(GRID * 22)
    cnv.append_object(outlet)
    cnv.add_connection(in_route.id, 1, outlet.id, 0, check_xlets=False)

    # label
    lbl_cnv = GCanvas(3, 202, size=8, width=198, height=18, label_xoff=3, label_yoff=9, font_size=12)
    lbl_cnv._bg_color = Color(100, 100, 100)
    lbl_cnv._label_color = Color(255, 255, 255)
    lbl_cnv._label = f"[{name}~]"
    cnv.append_object(lbl_cnv)

    # msg_name = Comment(10, 200, args=[f"[{name}~]"])
    # cnv.append_object(msg_name)
    for k, v in json_root.items():
        if k == "ui":
            y_off = 218
            c = 0
            for ui in v:
                y_off, _ = export_ui(cnv, c, prop_route, ui, 10, y_off, main_obj)

    cnv.set_graph_on_parent(True, xoff=2, yoff=200, width=200, height=y_off-200 + 8, hide_args=True)


    pd_exporter = PdExporter()
    cnv.traverse(pd_exporter)
    out_file = f'g{name}~.pd'
    pd_exporter.save(out_file)


if __name__ == '__main__':
    main()
