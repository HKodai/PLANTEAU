import requests

url = "http://127.0.0.1:5000/simulate"
data = {
    "lat": 35.713887740033876,
    "lon": 139.76016861370172,
    "alt": 25,
    "start": "2025-01-18",
    "days": 3650,
    "initial_height": 0.5,
}

response = requests.post(url, json=data)

if response.status_code == 200:
    print("Response:", response.json())
else:
    print("Error:", response.status_code, response.text)
