#!/usr/bin/env python
# coding=utf-8
from lxml import etree
import logging
import os
import os.path
import urllib.parse as ul

from .parser import get_parser
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

    def process_object_file(self, f):
        try:
            xml = etree.parse(f, get_parser())
            xml.xinclude()
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
        descr = ' '.join(xml_obj.find('meta/description').text.split())
        # logging.info("[%s] doc found: %s", name, descr.text)
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

    def xi_include(self, fname):
        url = ul.quote(fname)
        return etree.Element('{http://www.w3.org/2001/XInclude}include', href=url, parse="xml")

    def sort_cat(self, cat):
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
