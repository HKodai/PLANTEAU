import math
import numpy as np
from lxml import etree
from pyproj import Transformer


def parse_citygml_lod1_solids(file_path, from_code, to_code):
    """
    CityGMLファイルからLOD1 Solidの頂点群を読み込み、
    各建物 (core:cityObjectMember) ごとに複数ポリゴン (surfaceMember) を持つ構造に変換。

    返り値:
      buildings = [
         [poly1, poly2, ...],  # building1
         [poly1, poly2, ...],  # building2
         ...
      ]
      ここで poly は Nx3 の numpy配列 (x, y, z)
    """
    tree = etree.parse(file_path)
    root = tree.getroot()

    ns = {
        "core": "http://www.opengis.net/citygml/2.0",
        "bldg": "http://www.opengis.net/citygml/building/2.0",
        "gml": "http://www.opengis.net/gml",
    }

    city_object_members = root.findall(".//core:cityObjectMember", ns)

    transformer = Transformer.from_crs(from_code, to_code, always_xy=False)

    buildings = []
    for com in city_object_members:
        lod1_solids = com.findall(".//bldg:lod1Solid", ns)
        building_polygons = []

        for solid in lod1_solids:
            pos_list_elems = solid.findall(".//gml:posList", ns)
            for pos_list_elem in pos_list_elems:
                coord_text = pos_list_elem.text.strip()
                coords = coord_text.split()

                raw_points = []
                for i in range(0, len(coords), 3):
                    lat = float(coords[i])
                    lon = float(coords[i + 1])
                    alt = float(coords[i + 2])
                    raw_points.append((lat, lon, alt))

                converted_points = []
                for lat, lon, alt in raw_points:
                    x, y = transformer.transform(lat, lon)
                    z = alt
                    converted_points.append([x, y, z])

                poly_array = np.array(converted_points)
                building_polygons.append(poly_array)

        if len(building_polygons) > 0:
            buildings.append(building_polygons)

    return buildings


def get_building_centroid(building):
    """
    building: [poly1, poly2, ...]
    poly は Nx3 の numpy配列 (x, y, z)
    全ての頂点の平均座標を返す (x_c, y_c, z_c)
    """
    all_points = []
    for poly in building:
        all_points.append(poly)  # polyは Nx3
    concat_points = np.vstack(all_points)  # shape=(N_total,3)
    centroid = np.mean(concat_points, axis=0)  # [mean_x, mean_y, mean_z]
    return centroid[0], centroid[1], centroid[2]


def distance_3d(x1, y1, z1, x2, y2, z2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2)


def find_nearest_buildings(buildings, lat, lon, alt, from_code, to_code, top_n):
    transformer = Transformer.from_crs(from_code, to_code, always_xy=False)
    tx, ty = transformer.transform(lat, lon)
    tz = alt

    dist_list = []
    for bldg in buildings:
        cx, cy, cz = get_building_centroid(bldg)
        d = distance_3d(tx, ty, tz, cx, cy, cz)
        dist_list.append((d, bldg))

    dist_list.sort(key=lambda x: x[0])
    return dist_list[:top_n]
