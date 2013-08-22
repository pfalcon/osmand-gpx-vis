#!/usr/bin/env python
#
# This tool fixed GPX with audio/video/picture note waypoints improperly
# recorded due to bug http://code.google.com/p/osmand/issues/detail?id=1945
#
# It gets rid of a/v waypoints which don't belong to the current track
# (were made before its start or after end times) and removes duplicates
# in remaining waypoints.
#
import os
import sys
import stat
from datetime import datetime, timedelta
import xml.dom.minidom

import EXIF as exifread


# Diffenece between local timezone and UTC. Specified as such
# to avoid dependencies on pytz and tzlocal.
TZ_DIFF = timedelta(hours=-3)

GPX_HEADER = """\
<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>
<gpx version="1.1" creator="OsmAnd~" xmlns="http://www.topografix.com/GPX/1/1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd">
"""

def local2utc(t):
    return t + TZ_DIFF

def text(n):
    assert len(n.childNodes) == 1
    tn = n.childNodes[0]
    assert tn.nodeType == tn.TEXT_NODE
    return tn.data

def get_time_span(dom):
    min_time = "Z"
    max_time = "0"

    for wpt in dom.getElementsByTagName("trkpt"):
        time = text(wpt.getElementsByTagName("time")[0])
        if time < min_time:
            min_time = time
        if time > max_time:
            max_time = time

    min_time = datetime.strptime(min_time, "%Y-%m-%dT%H:%M:%SZ")
    max_time = datetime.strptime(max_time, "%Y-%m-%dT%H:%M:%SZ")
    return min_time, max_time


def main():
    dom = xml.dom.minidom.parse(sys.argv[1])
    out = open(sys.argv[2], "wt")
    mismatched = None
    if len(sys.argv) > 3:
        mismatched = open(sys.argv[3], "wt")

    min_time, max_time = get_time_span(dom)

    images = {}
    for wpt in dom.getElementsByTagName("wpt"):
        name = text(wpt.getElementsByTagName("name")[0])
        images[name] = True

    print "Start time:", min_time
    print "End time  :", max_time
    print "Total deduplicated input A/V waypoints:", len(images.keys())

    for fname in images.keys():
#    print "Processing " + fname
        fullname = "../avnotes/" + fname
        f = open(fullname)
        tags = exifread.process_file(f)
        if len(tags) == 0:
            # Non-JPEG file, like mp3 or mp4
            st = os.stat(fullname)
            d = datetime.fromtimestamp(st[stat.ST_MTIME])
        else:
            d = tags["Image DateTime"]
            d = datetime.strptime(str(d), "%Y:%m:%d %H:%M:%S")
        d = local2utc(d)
#    print d
        if d < min_time or d > max_time:
            del images[fname]

    print "Total A/V waypoints belonging to the track:", len(images.keys())


    out.write(GPX_HEADER)

    for n in dom.getElementsByTagName("trk"):
        print >>out, " ", n.toxml()

    seen = {}
    for wpt in dom.getElementsByTagName("wpt"):
        name = text(wpt.getElementsByTagName("name")[0])
        if name in images:
            if name not in seen:
                print >>out, " ", wpt.toxml()
                seen[name] = True
        else:
            if mismatched and name not in seen:
                print >>mismatched, " ", wpt.toxml()
                seen[name] = True

    print >>out, "</gpx>"


if __name__ == "__main__":
    main()
