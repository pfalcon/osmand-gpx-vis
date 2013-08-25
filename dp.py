# Dropbox integration
import os
import urllib2
import re

import dropbox
from settings import *

DIR = os.path.expanduser("~/.osmand2kml")
DROPTOK = DIR + "/droptok"
DROPCACHE = DIR + "/dropcache"

def authorize():
    try:
        os.makedirs(DIR)
    except OSError:
        pass

    flow = dropbox.client.DropboxOAuth2FlowNoRedirect(DROPBOX_APP_KEY, DROPBOX_APP_SECRET)
    authorize_url = flow.start()

    print '1. Go to: ' + authorize_url
    print '2. Click "Allow" (you might have to log in first)'
    print '3. Copy the authorization code.'
    code = raw_input("Enter the authorization code here: ").strip()

    access_token, user_id = flow.finish(code)
    print access_token, user_id

    f = open(DROPTOK, "w")
    f.write(access_token)
    f.close()
    return access_token


def get_token():
    if os.path.exists(DROPTOK):
        return open(DROPTOK).read()
    return authorize()


def init():
    global client
    global cache
    tok = get_token()
    client = dropbox.client.DropboxClient(tok)
    cache = {}
    if os.path.exists(DROPCACHE):
        for l in open(DROPCACHE):
            fname, full, preview = l.rstrip().split(" ", 2)
            cache[fname] = (full, preview)

def fix_preview_size(url, dim):
    url = re.sub(r"/jpeg/\d+x\d+/", "/jpeg/%s/" % dim, url)
    return url

def resolve_image(fname):
    if fname in cache:
        fullsize, preview = cache[fname]
        preview = fix_preview_size(preview, DROPBOX_PREVIEW_SIZE)
        return (fullsize, preview)
    shared = client.share(DROPBOX_AVNOTES_DIR + "/" + fname, short_url=False)
#    print shared
    fullsize = shared["url"]

    f = urllib2.urlopen(fullsize)
    content = f.read(4096)
    f.close()

    m = re.search(r'<meta content="(https://.+?)" property="og:image"', content)
    preview = m.group(1)
    preview = fix_preview_size(preview, DROPBOX_PREVIEW_SIZE)
    f = open(DROPCACHE, "at")
    f.write("%s %s %s\n" % (fname, fullsize, preview))
    f.close()
    cache[fname] = (fullsize, preview)
    return (fullsize, preview)


if __name__ == "__main__":
    init()
    import sys
    print resolve_image(sys.argv[1])
