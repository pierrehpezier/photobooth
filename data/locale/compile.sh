#!/bin/bash

for lang in *
do
	if [ -d $lang ]
	then
		msgfmt "${lang}/LC_MESSAGES/photobooth.po" -o "${lang}/LC_MESSAGES/photobooth.mo"
	fi
done

