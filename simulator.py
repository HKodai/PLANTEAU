import time
import pandas as pd
from tqdm import tqdm
from datetime import timedelta
from polygon import parse_citygml_lod1_solids, find_nearest_buildings
from solar import calc_sunlight_hours
from plant import Gingko


def simulate(
    gml, lat, lon, alt, from_code, to_code, top_n, start_date, days, initial_height
):
    t = time.time()
    print("start simulation.")

    # 1) パースして 3D頂点リストを取得
    print("parsing citygml...")
    buildings = parse_citygml_lod1_solids(gml, from_code, to_code)
    print(f"parsed citygml in {time.time() - t:.2f} sec.")
    t = time.time()

    # 2) 指定座標に近い建物トップNを取得
    print(f"finding nearest {top_n} buildings...")
    nearest = find_nearest_buildings(
        buildings, lat, lon, alt, from_code, to_code, top_n
    )
    print(f"found nearest buildings in {time.time() - t:.2f} sec.")
    t = time.time()

    # 3) 1年分の日照時間を計算
    print("calculating sunlight hours...")
    sunlight_hours = calc_sunlight_hours(nearest, lat, lon, alt)
    print(f"calculated sunlight hours in {time.time() - t:.2f} sec.")
    t = time.time()

    # 4) 生育シミュレーション
    print("simulating plant growth...")
    gingko = Gingko(initial_height)
    df = pd.DataFrame(columns=["date", "height", "color", "fall"])
    for d in tqdm(range(days)):
        date = start_date + timedelta(days=d)
        month = date.month
        day = date.day
        sunlight = sunlight_hours[f"{month}/{day}"]
        gingko.grow(sunlight)
        color = gingko.color(month)
        fall = gingko.fall(month)
        df.loc[d] = [date, gingko.height, color, fall]
    print(f"simulated plant growth in {time.time() - t:.2f} sec.")

    return df


if __name__ == "__main__":
    # ======== 設定部分 ========
    # CityGMLファイルのパス
    gml = "data/bunkyo/udx/bldg/53394650_bldg_6697_op.gml"
    # 植物の緯度・経度・標高
    lat = 35.713887740033876
    lon = 139.76016861370172
    alt = 25
    # EPSGコード
    from_code = 6697
    to_code = 6677
    # 上位何件を取得するか
    top_n = 20
    # シミュレーション
    start = pd.to_datetime("2025-01-18")
    days = 3650
    initial_height = 0.5
    # ==========================

    df = simulate(
        gml, lat, lon, alt, from_code, to_code, top_n, start, days, initial_height
    )
    df.to_csv("result.csv", index=False)
