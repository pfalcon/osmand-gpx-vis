#!/usr/bin/env python
import sys
import os
import optparse
import xml.dom.minidom

from points import *
from settings import *


optparser = optparse.OptionParser(usage='%prog [options] <input.gpx> <output.kml>')
optparser.add_option('', '--debug', action="store_true",
        help='Debug logging')
optparser.add_option('-q', '--quiet', action="store_true",
        help='Quiet operation')
optparser.add_option('--dropbox', action="store_true",
        help='Use Dropbox integration to reference (and share) media files')

(options, args) = optparser.parse_args()
if len(args) != 2:
    optparser.error("Wrong number of arguments.")

if options.dropbox:
    import dp
    dp.init()


dom = xml.dom.minidom.parse(args[0])
out = open(args[1], "wt")

def text(n):
    assert len(n.childNodes) == 1
    tn = n.childNodes[0]
    assert tn.nodeType == tn.TEXT_NODE
    return tn.data

seen = {}
#alt photo:
#http://mw1.google.com/mw-earth-vectordb/smartmaps_icons/tourist_destination-15.png
#video:
#http://maps.google.com/mapfiles/kml/shapes/movies.png
#audio:
#http://maps.google.com/mapfiles/kml/shapes/phone.png

print >>out, """\
<?xml version="1.0" standalone="yes"?>
<kml creator="osmand2kml" xmlns="http://earth.google.com/kml/2.0" xmlns:gx="http://www.google.com/kml/ext/2.2">
<Document>
<name><![CDATA[Sample File Name]]></name>
<description><![CDATA[Sample File Description]]></description>

<Style id="photo-normal">
    <IconStyle>
        <color>ff00aaff</color><scale>0.75</scale>
        <Icon><href>http://maps.google.com/mapfiles/kml/shapes/camera.png</href></Icon>
        <hotSpot x="0.5" y="0" xunits="fraction" yunits="fraction"/>
    </IconStyle>
    <LabelStyle>
        <scale>0</scale>
    </LabelStyle>
</Style>
<Style id="photo-hilite">
    <IconStyle>
        <color>ff00aaff</color><scale>1.2</scale>
        <Icon><href>http://maps.google.com/mapfiles/kml/shapes/camera.png</href></Icon>
        <hotSpot x="0.5" y="0" xunits="fraction" yunits="fraction"/>
    </IconStyle>
</Style>
<StyleMap id="photo">
    <Pair><key>normal</key><styleUrl>#photo-normal</styleUrl></Pair>
    <Pair><key>highlight</key><styleUrl>#photo-hilite</styleUrl></Pair>
</StyleMap>

<Style id="photo-multiple-normal">
    <IconStyle>
        <color>ff00aaff</color><scale>1</scale>
        <Icon><href>http://maps.google.com/mapfiles/kml/shapes/camera.png</href></Icon>
        <hotSpot x="0.5" y="0" xunits="fraction" yunits="fraction"/>
    </IconStyle>
    <LabelStyle>
        <scale>0.5</scale>
    </LabelStyle>
</Style>
<StyleMap id="media-multiple">
    <Pair><key>normal</key><styleUrl>#photo-multiple-normal</styleUrl></Pair>
    <Pair><key>highlight</key><styleUrl>#photo-hilite</styleUrl></Pair>
</StyleMap>

<Style id="video-normal">
    <IconStyle>
        <color>ff00aaff</color><scale>0.75</scale>
        <Icon><href>http://maps.google.com/mapfiles/kml/shapes/movies.png</href></Icon>
        <hotSpot x="0.5" y="0" xunits="fraction" yunits="fraction"/>
    </IconStyle>
    <LabelStyle>
        <scale>0</scale>
    </LabelStyle>
</Style>
<Style id="video-hilite">
    <IconStyle>
        <color>ff00aaff</color><scale>1.2</scale>
        <Icon><href>http://maps.google.com/mapfiles/kml/shapes/movies.png</href></Icon>
        <hotSpot x="0.5" y="0" xunits="fraction" yunits="fraction"/>
    </IconStyle>
</Style>
<StyleMap id="video">
    <Pair><key>normal</key><styleUrl>#video-normal</styleUrl></Pair>
    <Pair><key>highlight</key><styleUrl>#video-hilite</styleUrl></Pair>
</StyleMap>

<Style id="audio-normal">
    <IconStyle>
        <color>ff00aaff</color><scale>0.75</scale>
        <Icon><href>http://maps.google.com/mapfiles/kml/shapes/phone.png</href></Icon>
        <hotSpot x="0.5" y="0" xunits="fraction" yunits="fraction"/>
    </IconStyle>
    <LabelStyle>
        <scale>0</scale>
    </LabelStyle>
</Style>
<Style id="audio-hilite">
    <IconStyle>
        <color>ff00aaff</color><scale>1.2</scale>
        <Icon><href>http://maps.google.com/mapfiles/kml/shapes/phone.png</href></Icon>
        <hotSpot x="0.5" y="0" xunits="fraction" yunits="fraction"/>
    </IconStyle>
</Style>
<StyleMap id="audio">
    <Pair><key>normal</key><styleUrl>#audio-normal</styleUrl></Pair>
    <Pair><key>highlight</key><styleUrl>#audio-hilite</styleUrl></Pair>
</StyleMap>


<Style id="track-normal">
    <LineStyle>
        <color>99ffac59</color>
        <width>6</width>
    </LineStyle>
    <IconStyle>
        <Icon>
            <href>%(TRACK_ICON)s</href>
        </Icon>
    </IconStyle>
</Style>
<Style id="track-hilite">
    <LineStyle>
        <color>99ffac59</color>
        <width>8</width>
    </LineStyle>
    <IconStyle>
        <scale>1.2</scale>
        <Icon>
            <href>%(TRACK_ICON)s</href>
        </Icon>
    </IconStyle>
</Style>
<StyleMap id="track">
    <Pair>
        <key>normal</key>
        <styleUrl>#track-normal</styleUrl>
    </Pair>
    <Pair>
        <key>highlight</key>
        <styleUrl>#track-hilite</styleUrl>
    </Pair>
</StyleMap>

<Folder>
<name><![CDATA[Multimedia Notes]]></name>
<description><![CDATA[Photos, Audio & Video recorded during journey]]></description>
""" % globals()


def media_identify(fname):
    ext = name.rsplit(".", 1)[1]
    if ext == "jpg":
        return "photo"

    f = os.popen("avprobe " + fname + " 2>&1", "r")
    lines = f.readlines()
    lines = filter(lambda l: "Stream #" in l, lines)
    lines = filter(lambda l: "Video:" in l, lines)
    if len(lines) > 0:
        return "video"
    return "audio"

if CLUSTER_DISTANCE:
    accum = PointCluster()
else:
    accum = []

for wpt in dom.getElementsByTagName("wpt"):
    name = text(wpt.getElementsByTagName("name")[0])
    if name in seen:
        continue
    seen[name] = True

    lon = text(wpt.attributes["lon"])
    lat = text(wpt.attributes["lat"])
    p = Point(lon=float(lon), lat=float(lat))
    accum.append(p)
    props = {}
    p.props = props
    props["lon"] = lon
    props["lat"] = lat
    props["name"] = text(wpt.getElementsByTagName("time")[0])
    props["style"] = media_identify("../avnotes/" + name)
    if options.dropbox:
        try:
            fullsize_url, preview_url = dp.resolve_image(name)
        except:
            fullsize_url, preview_url = "", ""
    else:
        preview_url = "../avnotes/" + name
        fullsize_url = "http://localhost/avnotes/" + name
    props["preview_url"] = preview_url
    props["fullsize_url"] = fullsize_url

    preview_dims = ""
    if PREVIEW_WIDTH:
        preview_dims = 'width="%s"' % PREVIEW_WIDTH
    if PREVIEW_HEIGHT:
        preview_dims += ' height="%s"' % PREVIEW_HEIGHT
    props["preview_dims"] = preview_dims

cnt = 0
for wayp in accum:
    if len(wayp.cluster) > 0:
        wayp.props["style"] = "media-multiple"
        wayp.props["name"] = len(wayp.cluster) + 1
        pts = [wayp] + wayp.cluster
    else:
        pts = [wayp]
    content = ""
    for p in pts:
        content += """\
            <a href="%(fullsize_url)s"><img %(preview_dims)s src="%(preview_url)s"></a><br /><br />
        """ % p.props
    wayp.props["descr"] = content

    print >>out, """\
<Placemark>
        <name><![CDATA[%(name)s]]></name>
        <Snippet maxLines="2"><![CDATA[%(lat)s, %(lon)s]]></Snippet>
        <styleUrl>#%(style)s</styleUrl>
        <description><![CDATA[
            %(descr)s
        ]]>
        </description>
        <Point>
                <!--<altitudeMode>absolute</altitudeMode>-->
                <coordinates>%(lon)s,%(lat)s,0</coordinates>
        </Point>
</Placemark>
""" % wayp.props
    cnt += 1

print "Output %d waypoints" % cnt

print >>out, "</Folder>"

print >>out, """\
    <Folder>
      <name>Tracks</name>
      <Placemark>
        <!--<name>Track1</name>-->
        <description>Long track</description>
        <styleUrl>#track</styleUrl>
        <gx:MultiTrack>
          <altitudeMode>clampToGround</altitudeMode>
"""


for seg in dom.getElementsByTagName("trkseg"):
    print >>out, "<gx:Track>"
    times = []
    coords = []
    for wpt in seg.getElementsByTagName("trkpt"):
        time = text(wpt.getElementsByTagName("time")[0])
        lon = text(wpt.attributes["lon"])
        lat = text(wpt.attributes["lat"])
        times.append(time)
        coords.append("%s %s 0" % (lon, lat))

    for t in times:
        print >>out, "<when>%s</when>" % t

    for c in coords:
        print >>out, "<gx:coord>%s</gx:coord>" % c

    print >>out, "</gx:Track>"

print >>out, """\
        </gx:MultiTrack>
      </Placemark>
    </Folder>
"""

print >>out, """\
</Document>
</kml>
"""
