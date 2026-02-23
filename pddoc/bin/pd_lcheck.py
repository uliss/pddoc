#!/usr/bin/env python
# coding=utf-8

#   Copyright (C) 2025 by Serge Poltavski                                 #
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
import difflib
import json
import logging
import os
from pathlib import Path

import language_tool_python
from lxml import etree
from termcolor import colored

from pddoc.parser import PddocFormatParser

LANGTOOL_CONFIG = "langtool.json"
IGNORED_OBJECTS = dict()
IGNORED_WORDS = list()


def add_to_ignored(objname: str, tag: str, lang: str, text: str):
    global IGNORED_OBJECTS
    if objname not in IGNORED_OBJECTS:
        IGNORED_OBJECTS[objname] = {f"{tag}-{lang}": text}


def should_ignore(objname: str, tag: str, lang: str, text: str):
    global IGNORED_OBJECTS
    lang_tag = f"{tag}-{lang}"
    return objname in IGNORED_OBJECTS \
           and lang_tag in IGNORED_OBJECTS[objname] \
           and IGNORED_OBJECTS[objname][lang_tag] == text


def highlight_diff(s1: str, s2: str):
    output = []
    matcher = difflib.SequenceMatcher(None, s1, s2)
    for opcode, a0, a1, b0, b1 in matcher.get_opcodes():
        if opcode == 'equal':
            output.append(s1[a0:a1])
        elif opcode == 'insert':
            output.append(colored(s2[b0:b1], "green"))
        elif opcode == 'delete':
            output.append(colored(s1[a0:a1], "red"))
        elif opcode == 'replace':
            output.append(colored(s1[a0:a1], "red"))
            output.append(colored(s2[b0:b1], "green"))

    return "".join(output)


def is_correctly_spelled(rule, objname: str):
    global IGNORED_WORDS
    return rule.rule_issue_type == 'misspelling' \
           and (rule.matched_text in IGNORED_WORDS or rule.matched_text == objname)


def add_word(word: str):
    global IGNORED_WORDS
    if len(word) > 0:
        IGNORED_WORDS.append(word)
        logging.info(f"adding word to dict: '{word}'")


def fix_description(objname: str, tag: str, lang: str, new_text: str, root_dir: str):
    logging.warning(f"fix [{objname}]")
    doc_file = f"{root_dir}/{objname}.pddoc"
    if not os.path.exists(doc_file):
        logging.error(f"pddoc file not found: {doc_file}")
        return

    pddoc = PddocFormatParser(doc_file)
    pddoc.set_tag_tr(tag, lang, new_text)
    pddoc.save_to(doc_file)


def check_description_tr(tool, lang: str, root, root_dir: str):
    global IGNORED_OBJECTS

    descriptions = root.xpath(f"//*/description/tr[@lang='{lang}' and (not(@finished) or @finished!='false')]")
    for d in descriptions:
        objname = d.getparent().getparent().getparent().get("name")
        src_text = ' '.join(d.text.split())
        matches = []
        misspelled_word = ''
        for rule in tool.check(src_text):
            if not is_correctly_spelled(rule, objname):
                matches.append(rule)
                misspelled_word = rule.matched_text

        correct = language_tool_python.utils.correct(src_text, matches)
        if correct != src_text:
            if should_ignore(objname, "description", lang, src_text):
                logging.info(f"ignore: {objname}")
                continue

            print(colored(f"[{objname}] <description>", 'blue'))
            print(colored(f"source: {src_text}", 'white', 'on_grey', ['dark']))
            print(">>      {}".format(highlight_diff(src_text, correct)))

            user_input = input("Do you want to\n"
                               "\t- apply?       (y|a)\n"
                               "\t- skip?        (n|s)\n"
                               "\t- quit?        (q)\n"
                               "\t- ignore file? (i)\n"
                               f"\t- add word '{misspelled_word}'? (w): ").lower()
            if user_input in ("y", "a"):
                fix_description(objname, "description", lang, correct, root_dir)
            elif user_input in ("n", "s"):
                continue
            elif user_input == "q":
                return
            elif user_input.startswith("w"):
                add_word(misspelled_word)
            else:
                add_to_ignored(objname, 'description', lang, src_text)


def load_config_file():
    global IGNORED_OBJECTS
    global IGNORED_WORDS
    global LANGTOOL_CONFIG
    if os.path.exists(LANGTOOL_CONFIG):
        with open(LANGTOOL_CONFIG, 'rb') as file:
            loaded_data = json.load(file)
            IGNORED_OBJECTS = loaded_data.get('ignored', dict())
            IGNORED_WORDS = loaded_data.get('words', [])
            print(f"load langtool file: {LANGTOOL_CONFIG}")
            print(f"ignored words: {IGNORED_WORDS}")


def save_config_file():
    global IGNORED_OBJECTS
    global IGNORED_WORDS
    global LANGTOOL_CONFIG

    IGNORED_WORDS = list(set(IGNORED_WORDS))
    IGNORED_WORDS.sort()

    with open(LANGTOOL_CONFIG, "w") as file:
        data = {'ignored': IGNORED_OBJECTS, 'words': IGNORED_WORDS}
        json.dump(data, file, indent=4)


def main():
    arg_parser = argparse.ArgumentParser(description='update translations in the object pddoc file')
    arg_parser.add_argument('name', metavar='PDDOC', help="pddoc file")
    arg_parser.add_argument('--lang', '-l', metavar='LANG', choices=("en", "ru",), default='en',
                            help='language (currently "en", "ru")')
    arg_parser.add_argument('--verbose', '-v', action='store_true', help='verbose output')
    arg_parser.add_argument('--in-place', '-i', action='store_true', help='format in place (overwrite source file)')

    home = Path.home()
    os.environ['LTP_JAR_DIR_PATH'] = f"{home}/.cache/language_tool_python/LanguageTool-6.7-SNAPSHOT"

    load_config_file()

    args = vars(arg_parser.parse_args())
    in_file = args['name']
    lang = args['lang']
    # verbose = args['verbose']
    root_dir = os.path.dirname(in_file)

    logging.getLogger().setLevel(logging.INFO)

    xml = etree.parse(in_file)
    if not xml:
        exit(-1)

    xml.xinclude()
    root = xml.getroot()

    tool = language_tool_python.LanguageTool('en-US',
                                             config={'rulesFile': '/Users/serge/.languagetool.cfg',
                                                     'disabledRuleIds': 'UPPERCASE_SENTENCE_START'})

    check_description_tr(tool, lang, root, root_dir)

    tool.close()

    save_config_file()

    return 0


if __name__ == '__main__':
    main()
