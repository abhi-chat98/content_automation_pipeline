import requests
import urllib3
from tabulate import tabulate

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# === CONFIGURATION ===
BASE_URL = "https://qa.sfhawk.com"
API_ENDPOINT = f"{BASE_URL}/wp-json/wp/v2/posts"  # 🔁 this is the key change
params = {
    "_fields": "id,slug,title,template,status,link",
    "per_page": 100,
    "page": 1
}

all_posts = []

print(f"📰 Fetching posts from: {API_ENDPOINT}\n")

while True:
    try:
        response = requests.get(API_ENDPOINT, params=params, verify=False)
        response.raise_for_status()
        posts = response.json()

        if not posts:
            break

        for post in posts:
            all_posts.append([
                post["id"],
                post["slug"],
                post["title"]["rendered"],
                post.get("template", "default") or "default",
                post["status"],
                post["link"]
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
print(tabulate(all_posts, headers=headers, tablefmt="grid"))
