import osmium as osm
import geojson
from shapely.geometry import shape, Point

with open('havana.geojson', 'r') as f:
    data = geojson.load(f)

havana_polygon: list[(float,float)] = None
for feature in data['features']:
    if feature['geometry']['type'] == 'Polygon':
        havana_polygon = shape(feature['geometry'])
        break

if havana_polygon is None:
    raise ValueError("No se encontró un polígono válido en el archivo GeoJSON")

class MyHandler(osm.SimpleHandler):
    def __init__(self, polygon, writer):
        super(MyHandler, self).__init__()
        self.writer = writer
        self.node_ids = set()
        self.way_ids = set()
        self.relation_ids = set()
        self.polygon = polygon

    def node(self, n: osm.Node):
        point = Point(n.location.lon, n.location.lat)
        if self.polygon.contains(point):
            self.writer.add_node(n)
            self.node_ids.add(n.id)

    def way(self, w: osm.Way):
        if any(n.ref in self.node_ids for n in w.nodes):
            self.writer.add_way(w)
            self.way_ids.add(w.id)

    def relation(self, r: osm.Relation):
        if any(m.ref in self.node_ids or m.ref in self.way_ids for m in r.members):
                self.writer.add_relation(r)
                self.relation_ids.add(r.id)

writer = osm.SimpleWriter('havana.osm')
handler = MyHandler(havana_polygon, writer)
handler.apply_file("cuba-latest.osm")
writer.close()