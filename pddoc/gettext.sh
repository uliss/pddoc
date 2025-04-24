#!/bin/bash

xgettext -L Python \
	--sort-by-file \
	--force-po \
	--join-existing \
	--default-domain=pddoc \
	--package-name=pddoc \
	--package-version=0.9.1 \
	--msgid-bugs-address=serge.poltavski@gmail.com \
	--copyright-holder='Serge Poltavski' \
	--output=share/locales/pddoc.pot \
	*.py
