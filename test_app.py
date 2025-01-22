import requests

url = "http://127.0.0.1:5000/simulate"
data = {
    "tree_types": ["Gingko", "Cherry"],
    "positions": [[35.713887740033876, 139.76016861370172, 25], [35.713887740033876, 139.76016861370172, 25]],
    "initial_heights": [0.5, 0.5],
    "start": "2025-01-18",
    "days": 365,
}

response = requests.post(url, json=data)

if response.status_code == 200:
    print("Response:", response.json())
else:
    print("Error:", response.status_code, response.text)
