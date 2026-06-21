import random
from datetime import datetime, timezone
from math import sin, cos, pi

import gpxpy.gpx
from haversine import haversine, Unit

SCALE = 0.000007
ANGLE_VARIABILITY = pi / 7

class GPXManager:
    def __init__(self, start_lat, start_lon):
        self._lat = start_lat
        self._lon = start_lon
        self._angle = 0.0
        self._total_distance_km = 0.0

        self._gpx = gpxpy.gpx.GPX()
        track = gpxpy.gpx.GPXTrack()
        self._gpx.tracks.append(track)
        self._segment = gpxpy.gpx.GPXTrackSegment()
        track.segments.append(self._segment)

        self._segment.points.append(
            gpxpy.gpx.GPXTrackPoint(
                latitude=start_lat,
                longitude=start_lon,
                time=datetime.now(timezone.utc)
            )
        )

    def current_position(self):
        last = self._segment.points[-1]
        return last.latitude, last.longitude

    def total_distance_km(self):
        return self._total_distance_km

    def on_step(self):
        new_lat = self._lat + cos(self._angle) * SCALE
        new_lon = self._lon + sin(self._angle) * SCALE

        step_distance = haversine(
            (self._lat, self._lon),
            (new_lat,new_lon),
            unit = Unit.KILOMETERS
        )
        self._total_distance_km += step_distance

        self._lat = new_lat
        self._lon = new_lon
        self._angle += (random.random() * ANGLE_VARIABILITY) - (ANGLE_VARIABILITY / 2.0)

        self._segment.points.append(
            gpxpy.gpx.GPXTrackPoint(
                latitude=self._lat,
                longitude=self._lon,
                time=datetime.now(timezone.utc)
            )
        )

    def save(self, filepath):
        with open(filepath, "w") as f:
            f.write(self._gpx.to_xml())