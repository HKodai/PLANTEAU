import math
import numpy as np
from tqdm import tqdm
from pysolar.solar import get_altitude, get_azimuth
from datetime import datetime, timedelta, timezone
from visualizer import plot_sunlight
from pyproj import Transformer


def sun_direction(lat, lon, time_utc):
    alt_deg = get_altitude(lat, lon, time_utc)
    azi_deg = get_azimuth(lat, lon, time_utc)
    if alt_deg <= 0:
        return None  # 太陽が地平線下

    alt_rad = math.radians(alt_deg)
    azi_rad = math.radians(azi_deg)

    d_x = math.cos(alt_rad) * math.cos(azi_rad)
    d_y = math.cos(alt_rad) * math.sin(azi_rad)
    d_z = math.sin(alt_rad)

    # 正規化
    v = np.array([d_x, d_y, d_z], dtype=float)
    v_norm = np.linalg.norm(v)
    if v_norm < 1e-9:
        return None
    return v / v_norm


def ray_triangle_intersect(ray_origin, ray_dir, triangle):
    """Möller-Trumboreアルゴリズムによるレイ・三角形交差判定"""
    epsilon = 1e-7

    # 三角形の頂点
    v0, v1, v2 = triangle[0], triangle[1], triangle[2]

    edge1 = v1 - v0
    edge2 = v2 - v0
    h = np.cross(ray_dir, edge2)
    a = np.dot(edge1, h)

    if -epsilon < a < epsilon:
        return False  # レイが三角形と平行

    f = 1.0 / a
    s = ray_origin - v0
    u = f * np.dot(s, h)

    if u < 0.0 or u > 1.0:
        return False

    q = np.cross(s, edge1)
    v = f * np.dot(ray_dir, q)

    if v < 0.0 or u + v > 1.0:
        return False

    t = f * np.dot(edge2, q)

    return t > epsilon  # 交差点が前方にある場合のみTrue


def intersects(building, lat, lon, alt, sun_dir):
    """建物全体との交差判定"""
    # レイの始点（観測点）
    transformer = Transformer.from_crs(6697, 6677, always_xy=False)
    x, y = transformer.transform(lat, lon)
    ray_origin = np.array([x, y, alt])

    # 各ポリゴンについて
    for polygon in building:
        # ポリゴンを三角形に分割
        for i in range(1, len(polygon) - 1):
            triangle = np.array([polygon[0], polygon[i], polygon[i + 1]])
            if ray_triangle_intersect(ray_origin, sun_dir, triangle):
                return True
    return False


def calc_sunlight_hours(nearest, lat, lon, alt, debug=False):
    sunlight_hours = {}
    # 適当なうるう年を選択
    year = 2024
    for month in tqdm(range(1, 13)):
        for day in range(1, 32):
            err_days = [4, 6, 9, 11]
            if (month == 2 and day > 29) or (month in err_days and day > 30):
                break
            sunlight_hours[f"{month}/{day}"] = 0
            for hour in range(24):
                fmt = f"{year}-{month:02d}-{day:02d} {hour:02d}:00:00"
                # JSTからUTCへ変換
                jst = timezone(timedelta(hours=9), "JST")
                time_fmt = "%Y-%m-%d %H:%M:%S"
                time_jst = datetime.strptime(fmt, time_fmt).replace(tzinfo=jst)
                time_utc = time_jst.astimezone(timezone.utc)
                sun_dir = sun_direction(lat, lon, time_utc)
                if sun_dir is None:
                    continue

                blocked = False
                for _, building in nearest:
                    if intersects(building, lat, lon, alt, sun_dir):
                        blocked = True
                        break
                if not blocked:
                    sunlight_hours[f"{month}/{day}"] += 1

                if debug and (month, day, hour) in [
                    (1, 1, 8),
                    (1, 1, 12),
                    (1, 1, 16),
                ]:
                    plot_sunlight(nearest, lat, lon, alt, 6697, 6677, sun_dir)
    return sunlight_hours


if __name__ == "__main__":
    # デバッグ用
    import time
    from polygon import parse_citygml_lod1_solids, find_nearest_buildings

    # ======== 設定部分 ========
    gml = "data/bunkyo/udx/bldg/53394650_bldg_6697_op.gml"
    # 植物の緯度・経度・標高
    lat = 35.713887740033876
    lon = 139.76016861370172
    alt = 25
    # EPSGコード
    from_code = 6697
    to_code = 6677
    # 上位何件を取得するか
    top_n = 10
    # =========================

    # 1) CityGML (LOD1) をパースして 3D頂点リストを取得
    buildings = parse_citygml_lod1_solids(gml, from_code, to_code)

    # 2) 指定座標に近い建物トップNを取得
    nearest = find_nearest_buildings(
        buildings, lat, lon, alt, from_code, to_code, top_n
    )

    # 3) 1年分の日照時間を計算
    start = time.time()
    sunlight_hours = calc_sunlight_hours(nearest, lat, lon, alt, debug=True)
    elapsed_time = time.time() - start
    print(f"sunlight_hours: {sunlight_hours}")
    print(f"sum: {sum(sunlight_hours.values())}")
    print(f"elapsed_time: {elapsed_time}[s]")
