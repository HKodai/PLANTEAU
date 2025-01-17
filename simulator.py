import numpy as np
from pyproj import Transformer
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import random
from polygon import parse_citygml_lod1_solids, find_nearest_buildings


def plot_3d_building(ax, building, facecolor=(0.5, 0.5, 1.0), alpha=0.5):
    """
    指定した building ([poly1, poly2, ...]) を
    Poly3DCollection で3D描画する。
    facecolor, alpha などを引数で調整可能。
    """
    poly3d_list = []
    for poly in building:
        # polyは Nx3 のnumpy配列 -> (x,y,z) を順番に取り出してリスト化
        verts = poly.tolist()
        # Polygonを閉じるために先頭頂点を末尾に追加 (なくても可)
        if not np.allclose(verts[0], verts[-1]):
            verts.append(verts[0])
        poly3d_list.append(verts)

    # Poly3DCollectionへ一括登録
    collection = Poly3DCollection(
        poly3d_list, facecolor=facecolor, edgecolor="k", linewidths=0.5, alpha=alpha
    )
    ax.add_collection3d(collection)


def plot_buildings_3d(
    nearest_buildings, target_lat, target_lon, target_alt, from_code, to_code
):
    transformer = Transformer.from_crs(from_code, to_code, always_xy=False)
    tx, ty = transformer.transform(target_lat, target_lon)
    tz = target_alt

    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")

    # 各建物を描画（建物ごとにランダムな色をつける例）
    for dist, building in nearest_buildings:
        # 適当な色 (R,G,B) をランダムで割り当て
        color = (random.random(), random.random(), random.random())
        plot_3d_building(ax, building, facecolor=color, alpha=1.0)

    # ターゲット点を赤い三角形で表示
    ax.scatter(tx, ty, tz, color="red", marker="^", s=80, label="Target")

    # 軸ラベル
    ax.set_xlabel("X [m]")
    ax.set_ylabel("Y [m]")
    ax.set_zlabel("Z [m]")
    ax.set_title("Nearest Buildings (3D)")

    # y軸を反転
    ax.invert_yaxis()

    ax.legend()
    plt.show()


if __name__ == "__main__":
    # ======== 設定部分 ========
    citygml_file = "data/bunkyo/udx/bldg/53394650_bldg_6697_op.gml"

    # ターゲットの緯度・経度・標高 (標高は仮に0mとする)
    target_lat = 35.713887740033876
    target_lon = 139.76016861370172
    target_alt = 25  # 必要に応じて指定

    from_code = 6697
    to_code = 6677

    # 上位何件を取得するか
    top_n = 10
    # =========================

    # 1) CityGML (LOD1) をパースして 3D頂点リストを取得
    buildings = parse_citygml_lod1_solids(citygml_file, from_code, to_code)

    # 2) 指定座標に近い建物トップNを取得
    nearest = find_nearest_buildings(
        buildings, target_lat, target_lon, target_alt, from_code, to_code, top_n
    )

    # 3) 3D描画 (Poly3DCollection)
    plot_buildings_3d(nearest, target_lat, target_lon, target_alt, from_code, to_code)
