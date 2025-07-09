import requests
import urllib3
from tabulate import tabulate

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# === CONFIG ===
BASE_URL = "https://qa.sfhawk.com"
API_ENDPOINT = f"{BASE_URL}/wp-json/wp/v2/pages"
params = {
    "_fields": "id,slug,title,template,status,link",
    "per_page": 100,
    "page": 1
}

all_pages = []

print(f"📄 Fetching pages from: {API_ENDPOINT}\n")

while True:
    try:
        response = requests.get(API_ENDPOINT, params=params, verify=False)
        response.raise_for_status()
        pages = response.json()

        if not pages:
            break

        for page in pages:
            all_pages.append([
                page["id"],
                page["slug"],
                page["title"]["rendered"],
                page.get("template", "default") or "default",
                page["status"],
                page["link"]
            ])

        if 'X-WP-TotalPages' in response.headers:
            total_pages = int(response.headers['X-WP-TotalPages'])
            if params["page"] >= total_pages:
                break
            params["page"] += 1
        else:
            break

    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        break

# === Output as table ===
headers = ["ID", "Slug", "Title", "Template", "Status", "Link"]
print(tabulate(all_pages, headers=headers, tablefmt="grid"))
