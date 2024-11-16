import requests

headers = {
    "Content-Type": "application/json"
}

def get_closest_wines():
    url = "http://127.0.0.1:5000/get_closest_wines"
    payload = {
        "region": "champagne",
        "topnote": "herbaceous",
        "variety": "cabernet",
        "bottomnote": "herbaceous"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code != 200:
            print(f"Failed with status code {response.status_code}")
            print(f"Error message: {response.text}")
            return

        results = response.json()
        top = results["data"][0]
        print(f"PASS: get_closest_wines {top["wine_name"]} {top["similarity"]}" )

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    get_closest_wines()
