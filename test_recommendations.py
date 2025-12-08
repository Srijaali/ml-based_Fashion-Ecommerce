import requests
import json

BASE_URL = "http://localhost:8000"

print("=" * 80)
print("Testing Recommendations API")
print("=" * 80)

# Test 1: Health check
print("\n✓ Test 1: GET /recommendations/health")
try:
    response = requests.get(f"{BASE_URL}/recommendations/health")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")
except Exception as e:
    print(f"Error: {e}")

# Test 2: Get trending articles
print("\n✓ Test 2: GET /recommendations/trending?limit=5")
try:
    response = requests.get(f"{BASE_URL}/recommendations/trending?limit=5")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Trending items: {len(data['trending_items'])} items")
    for item in data['trending_items'][:3]:
        print(f"  - Article {item['article_id']}: score={item['score']:.2f}, rank={item['rank']}")
except Exception as e:
    print(f"Error: {e}")

# Test 3: Get item similarity
print("\n✓ Test 3: GET /recommendations/item-similar/835348011?limit=5")
try:
    response = requests.get(f"{BASE_URL}/recommendations/item-similar/835348011?limit=5")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Similar items: {len(data['similar_items'])} items")
    if data['similar_items']:
        for item in data['similar_items'][:3]:
            print(f"  - Article {item['article_id']}: score={item['score']:.4f}, rank={item['rank']}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 80)
print("Note: User recommendations test requires a valid customer from database")
print("=" * 80)
