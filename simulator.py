import time
import pandas as pd
from tqdm import tqdm
from datetime import timedelta
from polygon import parse_citygml_lod1_solids, find_nearest_buildings
from solar import calc_sunlight_hours
from plant import Gingko, Cherry
from multiprocessing import Pool


def process_sunlight(args):
    nearest, lat, lon, alt = args
    return calc_sunlight_hours(nearest, lat, lon, alt)

def simulate(
    dir, tree_types, positions, initial_heights, from_code, to_code, top_n, start_date, days
):
    t = time.time()
    print("start simulation.")
    num_trees = len(tree_types)
    # 植物の重心
    lat = sum([pos[0] for pos in positions]) / len(positions)
    lon = sum([pos[1] for pos in positions]) / len(positions)
    alt = sum([pos[2] for pos in positions]) / len(positions)

    # 1) パースして 3D頂点リストを取得
    print("parsing citygml...")
    buildings = parse_citygml_lod1_solids(dir, lat, lon, from_code, to_code)
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
    process_args = [(nearest, pos[0], pos[1], pos[2]) for pos in positions]
    with Pool() as pool:
        list_sunlight_hours = list(tqdm(
            pool.imap(process_sunlight, process_args),
            total=len(process_args)
        ))
    print(f"calculated sunlight hours in {time.time() - t:.2f} sec.")
    t = time.time()

    # 4) 生育シミュレーション
    print("simulating plant growth...")
    trees = []
    for i in range(num_trees):
        if tree_types[i] == "Gingko":
            trees.append(Gingko(initial_heights[i]))
        if tree_types[i] == "Cherry":
            trees.append(Cherry(initial_heights[i]))
    timeline = pd.DataFrame(columns=["date", "heights", "states"])
    for d in range(days):
        date = start_date + timedelta(days=d)
        month = date.month
        day = date.day
        heights = []
        states = []
        for i in range(num_trees):
            sunlight = list_sunlight_hours[i][f"{month}/{day}"]
            trees[i].grow(sunlight)
            heights.append(trees[i].height)
            states.append(trees[i].state(month))
        timeline.loc[d] = [date, heights, states]
    print(f"simulated plant growth in {time.time() - t:.2f} sec.")

    return timeline


if __name__ == "__main__":
    # ======== 設定部分 ========
    # CityGMLファイルのパス
    dir = "data/13100_tokyo23-ku_2020_citygml_4_2_op/udx/bldg/"
    # 植物の緯度・経度・標高
    lat = 35.713887740033876
    lon = 139.76016861370172
    alt = 25
    tree_types = ["Gingko"]
    positions = [(lat, lon, alt)]
    initial_heights = [0.5]
    # EPSGコード
    from_code = 6697
    to_code = 6677
    # 上位何件を取得するか
    top_n = 1
    # シミュレーション
    start = pd.to_datetime("2025-01-18")
    days = 5
    # ==========================

    timeline = simulate(dir, tree_types, positions, initial_heights, from_code, to_code, top_n, start, days)
    print(timeline)
