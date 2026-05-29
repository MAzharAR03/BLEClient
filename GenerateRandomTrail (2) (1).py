#!/usr/bin/env python3
import argparse
import gpxpy.gpx
import random
from Haversine import Haversine
from math import sin
from math import cos
from math import pi
from datetime import datetime, timedelta
import datetime as dt

# Command line arguments
parser = argparse.ArgumentParser()
parser.add_argument('-d', '--totalDistance', type=float, default=1.932782, help='total distance in km')
parser.add_argument('--lat', type=float, default=3.2206334, help='latitude of starting point')
parser.add_argument('--lon', type=float, default=101.9676587, help='longitude of starting point')
parser.add_argument('-m', '--durationMinutes', type=float, default=25.7238, help='duration trail in minutes')
parser.add_argument('-e', '--endTime', type=lambda s: datetime.strptime(s, '%Y-%m-%d %H:%M:%S'), default=datetime.now(dt.timezone.utc), help='end time in YYYY-MM-DD HH:MM:SS format')
parser.add_argument('-o', '--outputFile', type=str, help='name of the output file')
args = parser.parse_args()


# Configurations
SCALE = 0.0001
angle = 0.0
angleVariability = pi/7

# Calculations start here
currentTime = args.endTime
durationSeconds = 60*args.durationMinutes
distanceBetweenPoints = Haversine((args.lon, args.lat),(args.lon+SCALE, args.lat)).km
speed = durationSeconds/(args.totalDistance/distanceBetweenPoints)  # seconds per segment
lat0 = args.lat
lon0 = args.lon
lat=[args.lat, 0]
lon=[args.lon, 0]

# Calculate Before Trail
gpx = gpxpy.gpx.GPX()
gpx_track = gpxpy.gpx.GPXTrack()
gpx.tracks.append(gpx_track)
gpx_segment = gpxpy.gpx.GPXTrackSegment()
gpx_track.segments.append(gpx_segment)

distance = 0.0
i = 1
while distance<args.totalDistance:
    lat[i%2] = lat[(i+1)%2]+ cos(angle)*SCALE
    lon[i%2] = lon[(i+1)%2]+ sin(angle)*SCALE
    distance+=Haversine((lon[i%2],lat[i%2]),(lon[(i+1)%2],lat[(i+1)%2])).km
    i=i+1
    currentTime = currentTime - timedelta(seconds=speed)
    gpx_segment.points.insert(0,gpxpy.gpx.GPXTrackPoint(latitude=lat[i%2],longitude=lon[i%2],time=currentTime))
    angle = angle + (random.random() * angleVariability)-(angleVariability/2.0)

local_timezone = dt.datetime.now(dt.timezone.utc).astimezone().tzinfo

startTime = currentTime
print("Distance of the trail:",distance)
print("Start time:", startTime.astimezone(local_timezone))
print("End time of added part:", args.endTime.astimezone(local_timezone))
print("Total time of added part:", args.endTime.astimezone(local_timezone)-startTime.astimezone(local_timezone))

print("Total Distance:",distance)
outputFileName = args.outputFile if args.outputFile else "randomTrail.gpx"
outfile = open(outputFileName,"w")
outfile.write(gpx.to_xml())
outfile.close()
