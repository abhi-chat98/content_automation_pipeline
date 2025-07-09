import requests
import urllib3
from tabulate import tabulate

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Replace with your site
BASE_URL = "https://qa.sfhawk.com"
API_ENDPOINT = f"{BASE_URL}/wp-json/wp/v2/pages"
params = {
    '_fields': 'id,title,template',
    'per_page': 100  # Increase if needed
}

pages_data = []

try:
    response = requests.get(API_ENDPOINT, params=params, verify=False)
    response.raise_for_status()
    pages = response.json()

    for page in pages:
        page_id = page["id"]
        title = page["title"]["rendered"]
        template = page.get("template", "default") or "default"
        pages_data.append([page_id, title, template])

    # Table formatting
    headers = ["Page ID", "Title", "Template"]
    print(tabulate(pages_data, headers=headers, tablefmt="grid"))

except requests.exceptions.RequestException as e:
    print(f"Error: {e}")
