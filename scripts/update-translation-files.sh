#!/bin/bash
cd "$(dirname "$0")"/..

POTFILE="data/po/goodoldgalaxy.pot"

# Generate the pot file
xgettext --from-code=UTF-8 --keyword=_ --sort-output --language=Python goodoldgalaxy/*.py goodoldgalaxy/ui/*.py bin/goodoldgalaxy -o "${POTFILE}"
xgettext --join-existing --from-code=UTF-8 --keyword=translatable --sort-output --language=Glade data/ui/*.ui -o "${POTFILE}"

# Update each po file
for langfile in data/po/*.po; do
	msgmerge -U "${langfile}" "${POTFILE}"
done
