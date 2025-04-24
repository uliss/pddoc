#!/usr/bin/env python
# coding=utf-8
import logging
import os
import os.path
import urllib.parse as ul
from xml.etree.ElementTree import Element

from lxml import etree

import pddoc.txt
from .parser import get_schema
from .pd.canvas import Canvas
from .pd.coregui import Color
from .pd.obj import PdObject
from .pd.pdexporter import PdExporter
from .pdpage import PdPage, PdPageStyle


#   Copyright (C) 2016 by Serge Poltavski                                 #
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

def pages_schema():
    etree.register_namespace("xi", "http://www.w3.org/2001/XInclude")
    xml = etree.parse(os.path.join(os.path.dirname(__file__), 'share', 'pddoc_pages.xsd'))
    return etree.XMLSchema(xml.getroot())


class LibraryMaker(object):
    NSMAP = {'xi': "http://www.w3.org/2001/XInclude"}

    def __init__(self, name):
        etree.register_namespace("xi", "http://www.w3.org/2001/XInclude")
        self._name = name
        self._lib = etree.Element("library", version="1.0", name=name, nsmap=self.NSMAP)
        self._cats = {}
        self._cat_entries = {}
        self._authors = {}
        self._version = ""
        self._search_paths = []

    @property
    def version(self):
        return self._version

    @version.setter
    def version(self, v):
        self._version = v

    def add_search_path(self, path):
        if not os.path.exists(path) or not os.path.isdir(path):
            logging.error("invalid search path added: {0:s}".format(path))
            return False

        if path in self._search_paths:
            logging.warning("search path already exists in search path list: {0:s}".format(path))
            return False

        self._search_paths.append(path)
        return True

    def find_in_path(self, path):
        if os.path.exists(path):
            return path

        for p in self._search_paths:
            new_path = os.path.join(p, path)
            if os.path.exists(new_path):
                return new_path

        return False

    def process_files(self, files):
        for f in files:
            self.process_object_file(f)

        self.fill_library_meta()
        self.fill_library_info_pages()

    def process_object_file(self, f):
        try:
            xml = etree.parse(f)
            xml.xinclude()
            schema = get_schema()
            schema.assertValid(xml)
        except etree.XMLSyntaxError as e:
            logging.error("XML syntax error:\n \"%s\"\n\twhile parsing file: \"%s\"", e, f)
            return

        pddoc = xml.getroot()
        # find all object tags, but normally it's only one per file
        objects = filter(lambda x: x.tag == 'object', pddoc)
        for obj in objects:
            self.process_object_doc(f, obj)

    def process_object_doc(self, doc_fname, xml_obj):
        name = xml_obj.get('name')
        descr_tr = xml_obj.find('meta/description/tr[@lang="en"]')
        if descr_tr is None:
            descr_tr = xml_obj.find('meta/description/tr')
            if descr_tr is None:
                logging.warning(f"object description is not found in '{doc_fname}'")
                return

        descr = ' '.join(descr_tr.text.split())
        categ = xml_obj.find('meta/category')
        if categ is None:
            self.add_to_others(doc_fname, name=name, descr=descr)
        else:
            self.add_to_cat(categ.text, doc_fname, name=name, descr=descr, ref_view=categ.get('view', 'object'))
        lib = xml_obj.find('meta/library').text
        if lib != self._name:
            logging.warning("library differs in file: '%s': %s != %s", doc_fname, self._name, lib)
        authors = xml_obj.findall('meta/authors/author')
        for a in authors:
            self._authors[a.text] = True

    def fill_library_meta(self):
        # process library meta
        meta = etree.Element("meta")
        version = etree.Element("version")
        version.text = self._version
        meta.append(version)
        authors = etree.Element("authors")
        for a in sorted(self._authors.keys()):
            author = etree.Element("author")
            author.text = a
            authors.append(author)
        meta.append(authors)

        lib_info_fname = self.find_in_path("{0}_meta.xml".format(self._name))
        if lib_info_fname:
            xi = self.xi_include(os.path.basename(lib_info_fname))
            meta.append(xi)

        self._lib.append(meta)

    def fill_library_info_pages(self):
        info_pages = self.find_in_path("{0}_pages.xml".format(self._name))
        if info_pages:
            try:
                xml = etree.parse(info_pages)
                xml.xinclude()

                schema = pages_schema()
                schema.assertValid(xml)

                root = xml.getroot()
                for page in root.findall("page"):
                    self.process_info_page(page)
            except etree.XMLSyntaxError as e:
                logging.error("XML syntax error:\n \"%s\"\n\twhile parsing file: \"%s\"", e, info_pages)
                return

    def process_info_page(self, page: Element):
        for path in self._search_paths:
            db = os.path.join(path, 'ceammc.db')
            if os.path.exists(db):
                PdObject.xlet_calculator.add_db(db)

        title = page.find("title").text.strip()
        pd_page = PdPage("")
        y_pos = pd_page.add_header("CEAMMC documentation", False).bottom
        y_pos += 20

        # title
        lbl, hr, bbox = pd_page.make_section(y_pos, txt=title, replace_ws=False, color=PdPageStyle.HEADER_BG_COLOR,
                                             height=32,
                                             width=450)
        pd_page.append_list([hr, lbl])
        y_pos = hr.bottom + 20

        # sections
        for part in page.find('sections'):
            content = part.text.strip()

            if part.tag == 'section':
                title = part.text.strip()
                lbl, hr, bbox = pd_page.make_section(y_pos, txt=title, replace_ws=False, font_size=18, height=24,
                                                     width=200)
                pd_page.append_list([hr, lbl])
                y_pos = hr.bottom + 20
            elif part.tag == 'h1':
                title = part.text.strip()
                lbl = pd_page.make_label(20, y_pos, txt=title, replace_ws=False, font_size=18, height=34, label_yoff=17,
                                         width=400, color=Color.white(), bg_color=Color(30, 30, 30))
                pd_page.append_object(lbl)
                y_pos += lbl.height + 20
            elif part.tag == 'h2':
                title = part.text.strip()
                lbl = pd_page.make_label(20, y_pos, txt=title, replace_ws=False, font_size=16, height=28, label_yoff=14,
                                         width=400, color=Color.white(), bg_color=Color(70, 70, 70))
                pd_page.append_object(lbl)
                y_pos += lbl.height + 20
            elif part.tag == 'par':
                x_margin = 40
                y_pad = 15
                width = 80
                indent = int(part.get("indent", 0))
                y_pos += pd_page.add_txt(part.text, x_margin + (10 * indent), y_pos, width=(width - indent)).height
                y_pos += y_pad
            elif part.tag == 'pdascii':
                y_pad = 20
                x_margin = 40
                indent = int(part.get("indent", 0))
                data = part.text.strip()
                p = pddoc.txt.Parser()
                p.X_PAD = int(part.get("x-pad", 0))
                p.Y_PAD = int(part.get("y-pad", 0))
                p.X_SPACE *= float(part.get("x-space", 1.1))
                p.Y_SPACE *= float(part.get("y-space", 1.1))
                if not p.parse(data):
                    logging.info(f"<pdascii> parse failed: {data}")
                    continue

                cnv = Canvas(0, 0, 300, 100)
                cnv.type = Canvas.TYPE_WINDOW
                p.export(cnv)

                # save as pd
                br_calc = cnv.brect_calc()
                cnv.traverse(br_calc)
                bbox = br_calc.brect()
                wd = bbox[2] + p.X_PAD * 4
                ht = bbox[3] + p.Y_PAD * 4
                cnv.height = ht
                cnv.width = wd
                pd_exporter = PdExporter()
                cnv.traverse(pd_exporter)

                for obj in cnv.objects:
                    obj.y += y_pos
                    obj.x += (x_margin + (10 * indent))
                    pd_page.append_object(obj)

                for conn in cnv.connections.values():
                    pd_page.canvas.add_connection(conn[0].id, conn[1], conn[2].id, conn[3])

                y_pos += cnv.height
                y_pos += y_pad

            elif part.tag == 'a':
                x_margin = 40
                y_pad = 10
                indent = int(part.get("indent", 0))
                y_pos += pd_page.add_link(part.text, part.get("href"), x_margin + (10 * indent), y_pos).height
                y_pos += y_pad
            elif part.tag == 'ul':
                x_margin = 40
                y_pad = 5
                width = 70
                indent = int(part.get("indent", 0))

                for item in part.findall('item'):
                    txt = item.text.strip()
                    y_pos += pd_page.add_txt(f"◦ {txt}", x_margin + (10 * indent), y_pos, width=(width - indent)).height
                    y_pos += y_pad
            elif part.tag == 'li':
                x_margin = 40
                y_pad = 5
                width = 70
                indent = int(part.get("indent", 0))

                i = 1
                for item in part.findall('item'):
                    txt = item.text.strip()
                    y_pos += pd_page.add_txt(f"{i}. {txt}", x_margin + (10 * indent), y_pos,
                                             width=(width - indent)).height
                    i += 1
                    y_pos += y_pad
            elif part.tag == 'wiki':
                pass
                # y_pos += pd_page.add_w(part.text, part.get("url"), 40, y_pos).height + 20
            else:
                pass
                # logging.error("tag name: {}", part.tag)

        footer = pd_page.make_footer(y_pos + 20)
        pd_page.append_object(footer)

        output_name = page.get("output")
        with open(output_name, "w") as f:
            logging.error(f"{output_name} created")
            f.write(pd_page.to_string())

    def __str__(self):
        xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
        return xml + etree.tostring(self._lib, pretty_print=True, encoding='unicode')

    def add_to_others(self, fname, **kwargs):
        self.add_to_cat('others', fname, **kwargs)

    def add_to_cat(self, cat_name, fname, **kwargs):
        # first time add new category
        if cat_name not in self._cats:
            c = etree.Element('category', name=cat_name)
            cat_info_path = self.find_in_path("{0}_category_{1}.xml".format(self._name, cat_name))
            if cat_info_path:
                logging.info("adding: {0:s}".format(cat_info_path))
                cat_element = self.xi_include(os.path.basename(cat_info_path))
                c.append(cat_element)

            self._cats[cat_name] = c
            self._lib.append(c)
            self._cat_entries[cat_name] = {}

        # check for already added object
        if kwargs['name'] in self._cat_entries[cat_name]:
            logging.warning('object %s already in library', kwargs['name'])
            return

        self._cat_entries[cat_name][kwargs['name']] = True

        entry = etree.Element('entry', **kwargs)
        entry.append(self.xi_include(os.path.basename(fname)))
        self._cats[cat_name].append(entry)

    @staticmethod
    def xi_include(fname):
        url = ul.quote(fname)
        return etree.Element('{http://www.w3.org/2001/XInclude}include', href=url, parse="xml")

    @staticmethod
    def sort_cat(cat):
        entries = cat.findall('entry')
        sorted_entries = sorted(entries, key=lambda x: x.get('name'))

        for child in entries:
            cat.remove(child)

        for child in reversed(sorted_entries):
            cat.insert(0, child)

    def sort(self):
        cats = self._lib.findall('category')
        sorted_cats = sorted(cats, key=lambda x: x.get('name'))

        for child in cats:
            self._lib.remove(child)

        for child in reversed(sorted_cats):
            self.sort_cat(child)
            self._lib.insert(0, child)
