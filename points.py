class Point(object):
    def __init__(self, lat, lon):
        self.lat = lat
        self.lon = lon

class PointCluster(object):

    def __init__(self):
        self.clusters = set()
        self.points = []

    def add(self, point):
        dist = 999999
        closest_p = None
        for p in self.points:
            d = point.dist(p)
            if d < THRESHOLD:
                if not hasattr(p, "cluster"):
                    p.cluster = set()
                p.cluster.add(point)
                return
        self.points.append(point)

    def get_points(self):
        return self.points
