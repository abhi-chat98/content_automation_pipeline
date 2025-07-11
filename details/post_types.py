import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

WP_SITE = "https://qa.sfhawk.com"  # Replace this with your actual site
API_ENDPOINT = f"{WP_SITE}/wp-json/wp/v2/types"

try:
    response = requests.get(API_ENDPOINT, verify=False)
    response.raise_for_status()

    print("Available post types:\n")
    for slug, info in response.json().items():
        print(f"{slug} -> {info['name']}")
except requests.exceptions.RequestException as e:
    print("Error:", e)
