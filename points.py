import math

from settings import *


class Point(object):
    def __init__(self, lat, lon):
        self.lat = lat
        self.lon = lon
        self.cluster = []

    def dist(self, p):
        # Return heuristical distance metric, doing calculation
        # in degree units
        return math.hypot(self.lat - p.lat, self.lon - p.lon)


class PointCluster(object):

    def __init__(self):
        self.clusters = set()
        self.points = []

    def append(self, point):
        for p in self.points:
            d = point.dist(p)
            if d < CLUSTER_DISTANCE:
                p.cluster.append(point)
                return
        self.points.append(point)

    def get_points(self):
        return self.points

    def __iter__(self):
        return iter(self.points)
