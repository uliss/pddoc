#!/bin/bash

msgmerge --update pddoc.po ../../pddoc.pot
msgfmt --check pddoc.po -o pddoc.mo
msgfmt pddoc.po -o pddoc.mo
