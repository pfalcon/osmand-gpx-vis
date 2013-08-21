#!/usr/bin/env python
import sys
import xml.dom.minidom


TRACK_ICON = "http://earth.google.com/images/kml-icons/track-directional/track-0.png"
#TRACK_ICON = "http://maps.google.com/mapfiles/kml/shapes/motorcycling.png"

dom = xml.dom.minidom.parse(sys.argv[1])

def text(n):
    assert len(n.childNodes) == 1
    tn = n.childNodes[0]
    assert tn.nodeType == tn.TEXT_NODE
    return tn.data

seen = {}
#video:
#http://maps.google.com/mapfiles/kml/shapes/movies.png

print """\
<?xml version="1.0" standalone="yes"?>
<kml creator="osmand2kml" xmlns="http://earth.google.com/kml/2.0" xmlns:gx="http://www.google.com/kml/ext/2.2">
<Document>
<name><![CDATA[Sample File Name]]></name>
<description><![CDATA[Sample File Description]]></description>

<Style id="photo-normal">
    <IconStyle>
        <color>ff00aaff</color>
        <scale>0.75</scale>
        <Icon>
            <href>http://maps.google.com/mapfiles/kml/shapes/camera.png</href>
        </Icon>
        <hotSpot x="0.5" y="0" xunits="fraction" yunits="fraction"/>
    </IconStyle>
</Style>
<Style id="photo-hilite">
    <IconStyle>
        <color>ff00aaff</color>
        <scale>1.2</scale>
        <Icon>
            <href>http://maps.google.com/mapfiles/kml/shapes/camera.png</href>
        </Icon>
        <hotSpot x="0.5" y="0" xunits="fraction" yunits="fraction"/>
    </IconStyle>
</Style>
<StyleMap id="photo">
    <Pair>
        <key>normal</key>
        <styleUrl>#photo-normal</styleUrl>
    </Pair>
    <Pair>
        <key>highlight</key>
        <styleUrl>#photo-hilite</styleUrl>
    </Pair>
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

for wpt in dom.getElementsByTagName("wpt"):
    name = text(wpt.getElementsByTagName("name")[0])
    if name in seen:
        continue
    seen[name] = True

    time = text(wpt.getElementsByTagName("time")[0])
    lon = text(wpt.attributes["lon"])
    lat = text(wpt.attributes["lat"])
    print """\
<Placemark>
        <name><![CDATA[%(time)s]]></name>
        <Snippet maxLines="2"><![CDATA[%(lat)s, %(lon)s]]></Snippet>
        <styleUrl>#photo</styleUrl>
        <description><![CDATA[
            <img width="600" src="../avnotes/%(name)s"><br>
            <a href="http://localhost/avnotes/%(name)s">Full-size image</a>
        ]]>
        </description>
        <Point>
                <!--<altitudeMode>absolute</altitudeMode>-->
                <coordinates>%(lon)s,%(lat)s,0</coordinates>
        </Point>
</Placemark>
""" % locals()

print "</Folder>"

print """\
    <Folder>
      <name>Tracks</name>
      <Placemark>
        <!--<name>Track1</name>-->
        <description>Long track</description>
        <styleUrl>#track</styleUrl>
        <gx:MultiTrack>
"""


for seg in dom.getElementsByTagName("trkseg"):
    print "<gx:Track>"
    times = []
    coords = []
    for wpt in seg.getElementsByTagName("trkpt"):
        time = text(wpt.getElementsByTagName("time")[0])
        lon = text(wpt.attributes["lon"])
        lat = text(wpt.attributes["lat"])
        times.append(time)
        coords.append("%s %s 0" % (lon, lat))

    for t in times:
        print "<when>%s</when>" % t

    for c in coords:
        print "<gx:coord>%s</gx:coord>" % c

    print "</gx:Track>"

print """\
        </gx:MultiTrack>
      </Placemark>
    </Folder>
"""

print """\
</Document>
</kml>
"""
