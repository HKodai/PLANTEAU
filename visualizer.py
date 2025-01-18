import numpy as np
from pyproj import Transformer
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import random


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


def plot_sunlight(
    nearest_buildings, target_lat, target_lon, target_alt, from_code, to_code, sun_dir
):
    transformer = Transformer.from_crs(from_code, to_code, always_xy=False)
    tx, ty = transformer.transform(target_lat, target_lon)
    tz = target_alt

    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")

    # 各建物を描画（建物ごとにランダムな色をつける例）
    for _, building in nearest_buildings:
        # 適当な色 (R,G,B) をランダムで割り当て
        color = (random.random(), random.random(), random.random())
        plot_3d_building(ax, building, facecolor=color, alpha=1.0)

    # ターゲット点を赤い三角形で表示
    ax.scatter(tx, ty, tz, color="red", marker="^", s=80, label="Target")

    # 太陽方向を矢印で表示
    sun_dir *= 100  # 矢印の長さを調整
    ax.quiver(
        tx, ty, tz, sun_dir[0], sun_dir[1], sun_dir[2], color="orange", label="Sun"
    )

    # 軸ラベル
    ax.set_xlabel("X [m]")
    ax.set_ylabel("Y [m]")
    ax.set_zlabel("Z [m]")
    ax.set_title("Nearest Buildings (3D)")

    # z軸を反転
    ax.invert_zaxis()
    # xy平面を上から見る
    ax.view_init(elev=-90, azim=0)

    ax.legend()
    plt.show()
