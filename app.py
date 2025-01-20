from flask import Flask, request, jsonify
import pandas as pd
from simulator import simulate

app = Flask(__name__)


@app.route("/simulate", methods=["POST"])
def run_simulation():
    dir = "data/13100_tokyo23-ku_2020_citygml_4_2_op/udx/bldg/"
    from_code = 6697
    to_code = 6677
    data = request.json
    lat = data.get("lat")
    lon = data.get("lon")
    alt = data.get("alt")
    top_n = data.get("top_n", 20)
    start = pd.to_datetime(data.get("start"))
    days = data.get("days")
    initial_height = data.get("initial_height")

    # シミュレーション実行
    df = simulate(
        dir, lat, lon, alt, from_code, to_code, top_n, start, days, initial_height
    )
    heights = df["height"].tolist()
    return jsonify({"heights": heights})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
