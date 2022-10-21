#!/bin/bash

cd $(dirname $0)

for lang in *
do
	if [ -d $lang ]
	then
		msgfmt "${lang}/LC_MESSAGES/photobooth.po" -o "${lang}/LC_MESSAGES/photobooth.mo"
	fi
done

