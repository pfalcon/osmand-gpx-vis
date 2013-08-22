#!/bin/sh
# Losslessly auto-rotate images based on EXIF orientation tag.
#
# Only files which actually need rotation are touched. All tags and comments
# in file are preserved (note: exiftran removes some tags!) File's mtime
# is preserved (or to be exact, set to photo timestamp tag, as jhead doesn't
# have true preserve option).
#
# This requires "jhead" tool ("jhead" Debian package).

if [ $# != 1 ]; then
    echo "Usage: $0 <dir>"
    exit 1
fi

jhead -autorot -ft -se $1/*.jpg
