#!/bin/bash

curdir=$( dirname "${BASH_SOURCE[0]}" )
openssl req -x509 -passout pass:123456 -newkey rsa:4096 -keyout "${curdir}/issued/_key.pem" -out "${curdir}/issued/cert.pem" -days 365 << EOF
FR
Ile de France
Paris
pierrehpezier

192.168.2.198
mail@domain
EOF
openssl pkcs12 -passout pass:123456 -passin pass:123456 -export -inkey "${curdir}/issued/_key.pem" -in "${curdir}/issued/cert.pem" -out "${curdir}/issued/cert.p12"
openssl rsa -passin pass:123456 -in "${curdir}/issued/_key.pem" -pubout -outform der > "${curdir}/issued/key.pub"
openssl rsa -pubin -in "${curdir}/issued/key.pub" -inform der -out "${curdir}/issued/pub.pem" -outform pem
openssl rsa -in "${curdir}/issued/_key.pem" -passin pass:123456  -out "${curdir}/issued/key.pem"
rm -f "${curdir}/issued/_key.pem"
