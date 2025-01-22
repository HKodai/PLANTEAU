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
    tree_types = data.get("tree_types")
    positions = data.get("positions")
    initial_heights = data.get("initial_heights")
    top_n = data.get("top_n", 10)
    start = pd.to_datetime(data.get("start"))
    days = data.get("days")

    # シミュレーション実行
    timeline = simulate(
        dir, tree_types, positions, initial_heights, from_code, to_code, top_n, start, days)
    return jsonify({"timeline": timeline.to_dict(orient="records")})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
