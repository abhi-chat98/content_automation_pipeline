import requests
from requests.auth import HTTPBasicAuth
import json

# === CONFIGURATION ===
WORDPRESS_URL = "https://qa.sfhawk.com"
POST_ID = 123  # Replace with the actual post ID of a "use-case" post
USERNAME = WORDPRESS_USERNAME
APP_PASSWORD = WORDPRESS_PASSWORD  # Use an Application Password, NOT your login

# === API Endpoint ===
API_ENDPOINT = f"{WORDPRESS_URL}/wp-json/wp/v2/use-case/{POST_ID}"

try:
    response = requests.get(
        API_ENDPOINT,
        auth=HTTPBasicAuth(USERNAME, APP_PASSWORD),
        headers={"Content-Type": "application/json"},
        verify=False  # Ignore SSL errors if needed
    )

    response.raise_for_status()
    data = response.json()

    # Check if 'meta' exists
    if "meta" in data:
        print("🔍 Meta fields for post:")
        print(json.dumps(data["meta"], indent=2))
    else:
        print("⚠️ No meta field returned. ACF fields may not be exposed in REST API.")

except requests.exceptions.RequestException as e:
    print(f"❌ Error fetching post meta: {e}")
