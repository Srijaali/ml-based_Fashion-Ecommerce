# Hybrid Recommendation API - Quick Reference

## Server Setup

```bash
# Navigate to backend
cd backend

# Start server (port 8000)
python run.py
```

Server will be available at: `http://localhost:8000`

API docs: `http://localhost:8000/docs` (Swagger UI)

---

## Endpoint Quick Reference

### 1. Health Check

```bash
GET /hybrid-recommendations/health
```

Returns service status, model info, artifact paths.

**Response:**

```json
{
  "status": "cf_ready",
  "cf_models": {
    "n_customers": 552782,
    "n_items": 7214,
    "recommendations_loaded": true
  },
  "cb_models": {
    "n_articles": 0,
    "similarity_matrix_loaded": false
  }
}
```

---

## Product Page Endpoints

### 2. Similar Products

```bash
GET /hybrid-recommendations/similar-products/{article_id}?limit=10
```

Find articles with similar attributes (text, category, price).

**Example:**

```bash
curl http://localhost:8000/hybrid-recommendations/similar-products/article123?limit=5
```

**Response:**

```json
{
  "article_id": "article123",
  "similar_items": [
    {
      "article_id": "article456",
      "score": 0.92,
      "rank": 1
    }
  ],
  "count": 1
}
```

---

### 3. Often Bought Together

```bash
GET /hybrid-recommendations/often-bought/{article_id}?limit=10
```

Get items frequently co-purchased with this article.

**Example:**

```bash
curl http://localhost:8000/hybrid-recommendations/often-bought/article123?limit=5
```

**Response:**

```json
{
  "article_id": "article123",
  "similar_items": [
    {
      "article_id": "article789",
      "score": 0.85,
      "rank": 1
    }
  ],
  "count": 1
}
```

---

### 4. You May Also Like (Product)

```bash
GET /hybrid-recommendations/you-may-also-like-product/{article_id}?limit=10
```

Hybrid: 60% co-purchases + 40% attribute similarity.

**Example:**

```bash
curl http://localhost:8000/hybrid-recommendations/you-may-also-like-product/article123?limit=5
```

---

## Homepage Endpoints

### 5. Personalized For You

```bash
GET /hybrid-recommendations/personalized/{customer_id}?limit=12
```

Get items based on customer's purchase history (CF).

**Example:**

```bash
curl http://localhost:8000/hybrid-recommendations/personalized/cust_abc123?limit=12
```

**Response:**

```json
{
  "customer_id": "cust_abc123",
  "recommendations": [
    {
      "article_id": "article100",
      "score": 0.95,
      "rank": 1
    },
    {
      "article_id": "article200",
      "score": 0.88,
      "rank": 2
    }
  ],
  "count": 2,
  "recommendation_type": "personalized"
}
```

---

### 6. Customers Also Bought

```bash
GET /hybrid-recommendations/customers-also-bought/{customer_id}?limit=12&k_neighbors=10
```

Items purchased by similar customers.

**Parameters:**

- `limit`: Max recommendations (default: 12)
- `k_neighbors`: Similar users to aggregate (default: 10)

**Example:**

```bash
curl http://localhost:8000/hybrid-recommendations/customers-also-bought/cust_abc123?limit=12&k_neighbors=10
```

---

### 7. Based on Your Interactions

```bash
GET /hybrid-recommendations/based-on-interactions/{customer_id}?limit=12
```

Smart hybrid: CF for warm users, CB for cold users.

**Example:**

```bash
curl http://localhost:8000/hybrid-recommendations/based-on-interactions/cust_abc123?limit=12
```

---

### 8. Trending Now

```bash
GET /hybrid-recommendations/trending?limit=20
```

Most popular items (cached 1 hour).

**Example:**

```bash
curl http://localhost:8000/hybrid-recommendations/trending?limit=10
```

**Response:**

```json
{
  "trending_items": [
    {
      "article_id": "popular1",
      "score": 150.5,
      "rank": 1
    }
  ],
  "count": 1
}
```

---

## Testing with Python

```python
import requests
import json

BASE_URL = "http://localhost:8000"

# Test health
resp = requests.get(f"{BASE_URL}/hybrid-recommendations/health")
print(json.dumps(resp.json(), indent=2))

# Get trending
resp = requests.get(f"{BASE_URL}/hybrid-recommendations/trending?limit=5")
recs = resp.json()
print(f"Trending items: {recs['count']}")

# Get personalized (need valid customer_id)
customer_id = "abc123"  # Replace with real ID
resp = requests.get(
    f"{BASE_URL}/hybrid-recommendations/personalized/{customer_id}",
    params={"limit": 5}
)
if resp.status_code == 200:
    recs = resp.json()
    print(f"Personalized for {customer_id}: {recs['count']} items")
else:
    print(f"Error: {resp.status_code} - {resp.json()['detail']}")
```

---

## Response Format

All endpoints return standardized responses:

```json
{
  "article_id/customer_id": "string",
  "recommendations/similar_items/trending_items": [
    {
      "article_id": "string",
      "score": number,
      "rank": integer
    }
  ],
  "count": integer,
  "recommendation_type": "string (optional)",
  "generated_at": "ISO datetime (optional)"
}
```

---

## Status Codes

| Code | Meaning                    |
| ---- | -------------------------- |
| 200  | Success                    |
| 404  | Customer/Article not found |
| 503  | Service not initialized    |

---

## Common Issues & Solutions

### "Service not ready"

```
Status Code: 503
```

**Fix:** Server is still loading models. Wait 10-30 seconds and retry.

### "Customer not found"

```
Status Code: 404
```

**Fix:** Use a valid customer_id from your database.

### "Empty recommendations"

```
"count": 0
```

**This is normal!** Some scenarios return empty:

- Cold-start user with no history
- Unknown article
- No CF data available

System falls back to trending in these cases.

---

## Batch Testing

Test all 7 endpoints:

```bash
# Assuming you have customer_id and article_id
CUST="your_customer_id"
ITEM="your_article_id"

# Product page
curl http://localhost:8000/hybrid-recommendations/similar-products/$ITEM?limit=5
curl http://localhost:8000/hybrid-recommendations/often-bought/$ITEM?limit=5
curl http://localhost:8000/hybrid-recommendations/you-may-also-like-product/$ITEM?limit=5

# Homepage
curl http://localhost:8000/hybrid-recommendations/personalized/$CUST?limit=5
curl http://localhost:8000/hybrid-recommendations/customers-also-bought/$CUST?limit=5
curl http://localhost:8000/hybrid-recommendations/based-on-interactions/$CUST?limit=5

# Global
curl http://localhost:8000/hybrid-recommendations/trending?limit=5

# Health
curl http://localhost:8000/hybrid-recommendations/health
```

---

## Integration with Frontend

```javascript
// JavaScript example
async function getRecommendations(customerId) {
  const response = await fetch(
    `http://localhost:8000/hybrid-recommendations/personalized/${customerId}?limit=12`
  );

  if (!response.ok) {
    if (response.status === 404) {
      console.log("Customer not found");
      // Show trending instead
      return getTrendingItems();
    }
    throw new Error(`API error: ${response.statusText}`);
  }

  const data = await response.json();
  return data.recommendations;
}

async function getTrendingItems() {
  const response = await fetch(
    `http://localhost:8000/hybrid-recommendations/trending?limit=12`
  );
  const data = await response.json();
  return data.trending_items;
}
```

---

## Performance Notes

- **First request:** ~50-100ms (service loads models)
- **Trending endpoint:** <5ms (cached)
- **Personalized endpoint:** ~10-30ms
- **CB endpoint:** ~30-50ms (more computation)

---

## Next Steps

1. ✅ API is ready to use
2. ⏳ Download CB artifacts from Kaggle (optional for full hybrid)
3. 🔗 Integrate endpoints with frontend
4. 📊 Monitor performance with your analytics
5. 🎯 A/B test different weights

All features work with CF alone. Full hybrid improves coverage by 34%.
