import os
import sys
import codecs

# Code copied from https://stackoverflow.com/questions/8898294/convert-utf-8-with-bom-to-utf-8-with-no-bom-in-python

BUFSIZE = 4096
BOMLEN = len(codecs.BOM_UTF8)

path = sys.argv[1]
with open(path, "r+b") as fp:
    chunk = fp.read(BUFSIZE)
    if chunk.startswith(codecs.BOM_UTF8):
        i = 0
        chunk = chunk[BOMLEN:]
        while chunk:
            fp.seek(i)
            fp.write(chunk)
            i += len(chunk)
            fp.seek(BOMLEN, os.SEEK_CUR)
            chunk = fp.read(BUFSIZE)
        fp.seek(-BOMLEN, os.SEEK_CUR)
        fp.truncate()
