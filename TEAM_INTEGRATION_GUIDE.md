# Hybrid Recommendation System - Integration Guide for Backend & Frontend Teams

## Table of Contents
1. [Quick Start](#quick-start)
2. [For Backend Teams](#for-backend-teams)
3. [For Frontend Teams](#for-frontend-teams)
4. [API Endpoints Reference](#api-endpoints-reference)
5. [Integration Examples](#integration-examples)
6. [Common Patterns](#common-patterns)
7. [Error Handling](#error-handling)
8. [Performance Considerations](#performance-considerations)

---

## Quick Start

### Server Status
The recommendation system is currently running on:
- **Host:** `http://localhost:8000`
- **Prefix:** `/hybrid-recommendations`
- **Documentation:** `http://localhost:8000/docs` (interactive Swagger UI)

### System Status Check
```bash
curl http://localhost:8000/hybrid-recommendations/health
```

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

## For Backend Teams

### Overview
The recommendation system provides a REST API that your backend should call to:
- Fetch personalized recommendations for users
- Get product similarity suggestions
- Retrieve trending items
- Support feature recommendations on product pages

### Architecture Integration

```
Your Backend Service
        ↓
Calls Recommendation API
        ↓
HybridRecommendationService
        ↓
Returns Recommendations
        ↓
Your Backend ← Format & send to Frontend
```

### Implementation Approach

#### Option 1: Direct API Calls (Recommended for HTTP clients)

```python
import requests
from typing import List, Dict

class RecommendationClient:
    """Client for calling recommendation endpoints"""
    
    BASE_URL = "http://localhost:8000/hybrid-recommendations"
    
    @staticmethod
    def get_personalized(customer_id: str, limit: int = 12) -> List[Dict]:
        """Get personalized recommendations for a customer"""
        response = requests.get(
            f"{RecommendationClient.BASE_URL}/personalized/{customer_id}",
            params={"limit": limit}
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get("recommendations", [])
        elif response.status_code == 404:
            # Customer not found, fallback to trending
            return RecommendationClient.get_trending(limit)
        else:
            raise Exception(f"API Error: {response.status_code}")
    
    @staticmethod
    def get_similar_products(article_id: str, limit: int = 10) -> List[Dict]:
        """Get similar products for a given article"""
        response = requests.get(
            f"{RecommendationClient.BASE_URL}/similar-products/{article_id}",
            params={"limit": limit}
        )
        return response.json().get("similar_items", [])
    
    @staticmethod
    def get_trending(limit: int = 20) -> List[Dict]:
        """Get trending items"""
        response = requests.get(
            f"{RecommendationClient.BASE_URL}/trending",
            params={"limit": limit}
        )
        return response.json().get("trending_items", [])
```

#### Option 2: In-Process Service (For high-frequency calls)

If you're running the backend in the same process, you can import the service directly:

```python
from app.services.hybrid_recommendation_service import HybridRecommendationService

# Initialize once at startup
recommendation_service = HybridRecommendationService(
    cf_model_dir="data/recommendations",
    cb_model_dir="data/content_based_model"
)

# Use in your endpoints
def get_user_recs(customer_id: str):
    recs = recommendation_service.get_personalized_cf(customer_id, limit=12)
    return {"recommendations": recs}
```

### Backend Implementation Patterns

#### Pattern 1: Wrapping Recommendations in Product Response

```python
from fastapi import APIRouter, Depends

router = APIRouter()

@router.get("/products/{article_id}")
def get_product_with_recommendations(article_id: str):
    """Get product details with 'You May Also Like' recommendations"""
    
    # Get product details
    product = db.query(Product).filter(Product.id == article_id).first()
    
    if not product:
        raise HTTPException(status_code=404)
    
    # Get recommendations from hybrid system
    similar_products = RecommendationClient.get_similar_products(article_id, limit=5)
    often_bought = RecommendationClient.get_often_bought(article_id, limit=5)
    
    return {
        "product": product,
        "recommendations": {
            "similar": similar_products,
            "often_bought_together": often_bought
        }
    }
```

#### Pattern 2: User Feed with Recommendations

```python
@router.get("/users/{customer_id}/feed")
def get_user_feed(customer_id: str):
    """Get user's personalized feed"""
    
    # Verify user exists
    user = db.query(Customer).filter(Customer.id == customer_id).first()
    if not user:
        raise HTTPException(status_code=404)
    
    # Get recommendations
    recs = RecommendationClient.get_personalized(customer_id, limit=20)
    
    # Optionally: Load full product details
    article_ids = [rec['article_id'] for rec in recs]
    products = db.query(Product).filter(Product.id.in_(article_ids)).all()
    
    return {
        "customer_id": customer_id,
        "items": products,
        "recommendation_count": len(recs)
    }
```

#### Pattern 3: Homepage Recommendations

```python
@router.get("/homepage/recommendations")
def get_homepage_recommendations(customer_id: str = None):
    """Get recommendations for homepage"""
    
    if customer_id:
        # User logged in - get personalized
        recs = RecommendationClient.get_personalized(customer_id, limit=12)
    else:
        # Anonymous user - get trending
        recs = RecommendationClient.get_trending(limit=12)
    
    # Load full product data
    article_ids = [rec['article_id'] for rec in recs]
    products = db.query(Product).filter(Product.id.in_(article_ids)).all()
    
    return {
        "recommendations": products,
        "count": len(products)
    }
```

### Caching Strategy for Backend

```python
from functools import lru_cache
from datetime import datetime, timedelta

class CachedRecommendationClient:
    """Recommendation client with local caching"""
    
    def __init__(self, cache_ttl_minutes=60):
        self.cache = {}
        self.cache_ttl = timedelta(minutes=cache_ttl_minutes)
    
    def get_personalized(self, customer_id: str, limit: int = 12):
        """Get personalized recs with caching"""
        cache_key = f"personalized_{customer_id}_{limit}"
        
        # Check cache
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if datetime.now() - timestamp < self.cache_ttl:
                return cached_data
        
        # Fetch fresh
        recs = RecommendationClient.get_personalized(customer_id, limit)
        self.cache[cache_key] = (recs, datetime.now())
        return recs
    
    def clear_user_cache(self, customer_id: str):
        """Clear cached recommendations for a user after purchase"""
        keys_to_delete = [k for k in self.cache.keys() if customer_id in k]
        for key in keys_to_delete:
            del self.cache[key]
```

### Error Handling in Backend

```python
import logging

logger = logging.getLogger(__name__)

def safe_get_recommendations(endpoint: str, **params):
    """Safely get recommendations with fallback"""
    try:
        response = requests.get(endpoint, params=params, timeout=5)
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            logger.warning(f"Not found: {endpoint}")
            return None
        else:
            logger.error(f"API error {response.status_code}: {response.text}")
            return None
            
    except requests.Timeout:
        logger.error(f"Recommendation API timeout: {endpoint}")
        return None
    except Exception as e:
        logger.error(f"Recommendation API error: {str(e)}")
        return None

# Usage
recs = safe_get_recommendations(
    "http://localhost:8000/hybrid-recommendations/personalized/{customer_id}",
    limit=12
)

if recs:
    # Use recommendations
    return recs
else:
    # Fallback to default behavior
    return get_trending_fallback()
```

---

## For Frontend Teams

### Overview
The recommendation system provides recommendations that should be displayed in specific places:
- Product pages: "Similar Products", "Often Bought Together", "You May Also Like"
- Homepage/Feed: "Personalized For You", "Customers Also Bought", "Based on Your Interactions"
- Global: "Trending Now"

### Integration Points

#### Point 1: Product Page
Display 3 recommendation sections:

```html
<!-- Product Details -->
<div class="product-detail">
  <h1>{{ product.name }}</h1>
  <p>{{ product.description }}</p>
  
  <!-- Section 1: Similar Products (Content-Based) -->
  <section class="recommendations">
    <h3>Similar Products</h3>
    <div class="product-grid">
      <article v-for="item in similarProducts" :key="item.article_id">
        <img :src="`/images/${item.image}`" />
        <h4>{{ item.name }}</h4>
        <p class="price">{{ item.price }}</p>
        <button @click="addToCart(item)">Add to Cart</button>
      </article>
    </div>
  </section>
  
  <!-- Section 2: Often Bought Together (Behavioral) -->
  <section class="recommendations">
    <h3>Customers Often Buy Together</h3>
    <div class="product-grid">
      <article v-for="item in oftenBought" :key="item.article_id">
        <img :src="`/images/${item.image}`" />
        <h4>{{ item.name }}</h4>
        <p class="price">{{ item.price }}</p>
        <button @click="addToCart(item)">Add to Cart</button>
      </article>
    </div>
  </section>
  
  <!-- Section 3: You May Also Like (Hybrid) -->
  <section class="recommendations">
    <h3>You May Also Like</h3>
    <div class="product-grid">
      <article v-for="item in youMayAlsoLike" :key="item.article_id">
        <img :src="`/images/${item.image}`" />
        <h4>{{ item.name }}</h4>
        <p class="price">{{ item.price }}</p>
        <button @click="addToCart(item)">Add to Cart</button>
      </article>
    </div>
  </section>
</div>
```

Vue.js Implementation:

```vue
<script setup>
import { ref, onMounted } from 'vue'

const props = defineProps({
  articleId: String
})

const similarProducts = ref([])
const oftenBought = ref([])
const youMayAlsoLike = ref([])
const loading = ref(false)
const error = ref(null)

onMounted(async () => {
  await loadRecommendations()
})

async function loadRecommendations() {
  loading.value = true
  error.value = null
  
  try {
    // Fetch all 3 recommendations in parallel
    const [similar, often, hybrid] = await Promise.all([
      fetch(`/api/hybrid-recommendations/similar-products/${props.articleId}?limit=5`),
      fetch(`/api/hybrid-recommendations/often-bought/${props.articleId}?limit=5`),
      fetch(`/api/hybrid-recommendations/you-may-also-like-product/${props.articleId}?limit=5`)
    ])
    
    similarProducts.value = (await similar.json()).similar_items
    oftenBought.value = (await often.json()).similar_items
    youMayAlsoLike.value = (await hybrid.json()).similar_items
    
  } catch (err) {
    error.value = "Failed to load recommendations"
    console.error(err)
  } finally {
    loading.value = false
  }
}

function addToCart(item) {
  // Your cart logic
  console.log("Added to cart:", item)
}
</script>
```

#### Point 2: Homepage/Feed

```vue
<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const sections = ref({
  personalized: [],
  customersAlsoBought: [],
  basedOnInteractions: [],
  trending: []
})

onMounted(async () => {
  if (auth.isLoggedIn) {
    // Load all personalized sections
    await Promise.all([
      loadPersonalized(),
      loadCustomersAlsoBought(),
      loadBasedOnInteractions()
    ])
  } else {
    // Anonymous user - just trending
    await loadTrending()
  }
})

async function loadPersonalized() {
  try {
    const res = await fetch(
      `/api/hybrid-recommendations/personalized/${auth.customerId}?limit=12`
    )
    sections.value.personalized = (await res.json()).recommendations
  } catch (err) {
    console.error("Failed to load personalized:", err)
  }
}

async function loadCustomersAlsoBought() {
  try {
    const res = await fetch(
      `/api/hybrid-recommendations/customers-also-bought/${auth.customerId}?limit=10`
    )
    sections.value.customersAlsoBought = (await res.json()).recommendations
  } catch (err) {
    console.error("Failed to load customers also bought:", err)
  }
}

async function loadBasedOnInteractions() {
  try {
    const res = await fetch(
      `/api/hybrid-recommendations/based-on-interactions/${auth.customerId}?limit=12`
    )
    sections.value.basedOnInteractions = (await res.json()).recommendations
  } catch (err) {
    console.error("Failed to load based on interactions:", err)
  }
}

async function loadTrending() {
  try {
    const res = await fetch(
      `/api/hybrid-recommendations/trending?limit=20`
    )
    sections.value.trending = (await res.json()).trending_items
  } catch (err) {
    console.error("Failed to load trending:", err)
  }
}
</script>

<template>
  <div class="homepage">
    <!-- Personalized Section (if logged in) -->
    <section v-if="auth.isLoggedIn && sections.personalized.length" class="recommendations">
      <h2>Personalized For You</h2>
      <ProductCarousel :items="sections.personalized" />
    </section>
    
    <!-- Customers Also Bought -->
    <section v-if="auth.isLoggedIn && sections.customersAlsoBought.length" class="recommendations">
      <h2>Customers Also Bought</h2>
      <ProductCarousel :items="sections.customersAlsoBought" />
    </section>
    
    <!-- Based on Your Interactions (Hybrid) -->
    <section v-if="auth.isLoggedIn && sections.basedOnInteractions.length" class="recommendations">
      <h2>Based on Your Interactions</h2>
      <ProductCarousel :items="sections.basedOnInteractions" />
    </section>
    
    <!-- Trending (always show) -->
    <section v-if="sections.trending.length" class="recommendations">
      <h2>Trending Now</h2>
      <ProductCarousel :items="sections.trending" />
    </section>
  </div>
</template>
```

### JavaScript/React Implementation

```javascript
import { useState, useEffect } from 'react'

function ProductRecommendations({ articleId }) {
  const [recs, setRecs] = useState({
    similar: [],
    often: [],
    hybrid: []
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchRecs = async () => {
      try {
        const [similar, often, hybrid] = await Promise.all([
          fetch(`/api/hybrid-recommendations/similar-products/${articleId}`),
          fetch(`/api/hybrid-recommendations/often-bought/${articleId}`),
          fetch(`/api/hybrid-recommendations/you-may-also-like-product/${articleId}`)
        ])

        setRecs({
          similar: (await similar.json()).similar_items,
          often: (await often.json()).similar_items,
          hybrid: (await hybrid.json()).similar_items
        })
      } catch (err) {
        console.error('Failed to load recommendations:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchRecs()
  }, [articleId])

  if (loading) return <div>Loading recommendations...</div>

  return (
    <div className="recommendations">
      <RecommendationSection title="Similar Products" items={recs.similar} />
      <RecommendationSection title="Often Bought Together" items={recs.often} />
      <RecommendationSection title="You May Also Like" items={recs.hybrid} />
    </div>
  )
}

function RecommendationSection({ title, items }) {
  if (items.length === 0) return null

  return (
    <section className="recommendation-section">
      <h3>{title}</h3>
      <div className="product-grid">
        {items.map(item => (
          <ProductCard key={item.article_id} item={item} />
        ))}
      </div>
    </section>
  )
}
```

### API Service Layer (Best Practice)

```typescript
// api/recommendations.ts
const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000'

interface RecommendationItem {
  article_id: string
  score: number
  rank: number
}

interface RecommendationResponse {
  similar_items?: RecommendationItem[]
  recommendations?: RecommendationItem[]
  trending_items?: RecommendationItem[]
  count: number
}

export const recommendationAPI = {
  async getSimilarProducts(articleId: string, limit: number = 10): Promise<RecommendationItem[]> {
    const res = await fetch(
      `${API_BASE}/hybrid-recommendations/similar-products/${articleId}?limit=${limit}`
    )
    const data: RecommendationResponse = await res.json()
    return data.similar_items || []
  },

  async getOftenBought(articleId: string, limit: number = 10): Promise<RecommendationItem[]> {
    const res = await fetch(
      `${API_BASE}/hybrid-recommendations/often-bought/${articleId}?limit=${limit}`
    )
    const data: RecommendationResponse = await res.json()
    return data.similar_items || []
  },

  async getPersonalized(customerId: string, limit: number = 12): Promise<RecommendationItem[]> {
    const res = await fetch(
      `${API_BASE}/hybrid-recommendations/personalized/${customerId}?limit=${limit}`
    )
    if (res.status === 404) {
      // Fallback to trending
      return this.getTrending(limit)
    }
    const data: RecommendationResponse = await res.json()
    return data.recommendations || []
  },

  async getTrending(limit: number = 20): Promise<RecommendationItem[]> {
    const res = await fetch(
      `${API_BASE}/hybrid-recommendations/trending?limit=${limit}`
    )
    const data: RecommendationResponse = await res.json()
    return data.trending_items || []
  }
}
```

---

## API Endpoints Reference

### Health Check
```
GET /hybrid-recommendations/health
```

Returns service status and model information.

**Response:**
```json
{
  "status": "cf_ready",
  "cf_models": {
    "recommendations_loaded": true,
    "n_recommendations": 196308,
    "n_customers": 552782,
    "n_items": 7214,
    "user_factors_shape": [552782, 100],
    "item_factors_shape": [7214, 100]
  },
  "cb_models": {
    "similarity_matrix_loaded": false,
    "n_articles": 0
  }
}
```

### Similar Products (Content-Based)
```
GET /hybrid-recommendations/similar-products/{article_id}?limit=10
```

**Parameters:**
- `article_id` (path): Product ID
- `limit` (query): Max items (1-50, default: 10)

**Response:**
```json
{
  "article_id": "item123",
  "similar_items": [
    {
      "article_id": "item456",
      "score": 0.92,
      "rank": 1
    }
  ],
  "count": 5,
  "generated_at": "2025-12-09T15:30:00"
}
```

### Often Bought Together
```
GET /hybrid-recommendations/often-bought/{article_id}?limit=10
```

**Parameters:**
- `article_id` (path): Product ID
- `limit` (query): Max items (1-50, default: 10)

**Response:**
```json
{
  "article_id": "item123",
  "similar_items": [
    {
      "article_id": "item789",
      "score": 0.85,
      "rank": 1
    }
  ],
  "count": 5
}
```

### You May Also Like (Product)
```
GET /hybrid-recommendations/you-may-also-like-product/{article_id}?limit=10
```

**Parameters:**
- `article_id` (path): Product ID
- `limit` (query): Max items (1-50, default: 10)

**Response:** Same as above

### Personalized
```
GET /hybrid-recommendations/personalized/{customer_id}?limit=12
```

**Parameters:**
- `customer_id` (path): Customer ID
- `limit` (query): Max items (1-50, default: 12)

**Response:**
```json
{
  "customer_id": "cust_123",
  "recommendations": [
    {
      "article_id": "item456",
      "score": 0.95,
      "rank": 1
    }
  ],
  "count": 12,
  "recommendation_type": "personalized",
  "generated_at": "2025-12-09T15:30:00"
}
```

**Error Response (404):**
```json
{
  "detail": "Customer cust_unknown not found"
}
```

### Customers Also Bought
```
GET /hybrid-recommendations/customers-also-bought/{customer_id}?limit=12&k_neighbors=10
```

**Parameters:**
- `customer_id` (path): Customer ID
- `limit` (query): Max items (1-50, default: 12)
- `k_neighbors` (query): Similar users to aggregate (1-50, default: 10)

**Response:** Same structure as Personalized

### Based on Your Interactions (Hybrid)
```
GET /hybrid-recommendations/based-on-interactions/{customer_id}?limit=12
```

**Parameters:**
- `customer_id` (path): Customer ID
- `limit` (query): Max items (1-50, default: 12)

**Response:** Same structure as Personalized

### Trending
```
GET /hybrid-recommendations/trending?limit=20
```

**Parameters:**
- `limit` (query): Max items (1-100, default: 20)

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
  "count": 20,
  "generated_at": "2025-12-09T15:30:00"
}
```

---

## Integration Examples

### Example 1: E-Commerce Product Page

**Backend (Python/FastAPI):**
```python
from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session

router = APIRouter()

@router.get("/products/{article_id}")
def get_product_page(article_id: str, db: Session):
    # Get product
    product = db.query(Product).filter(Product.article_id == article_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Get recommendations
    similar = requests.get(
        f"http://localhost:8000/hybrid-recommendations/similar-products/{article_id}",
        params={"limit": 5}
    ).json()
    
    often_bought = requests.get(
        f"http://localhost:8000/hybrid-recommendations/often-bought/{article_id}",
        params={"limit": 5}
    ).json()
    
    return {
        "product": product,
        "recommendations": {
            "similar_products": similar.get("similar_items", []),
            "often_bought_together": often_bought.get("similar_items", [])
        }
    }
```

**Frontend (React):**
```jsx
function ProductPage({ articleId }) {
  const [product, setProduct] = useState(null)
  const [recs, setRecs] = useState({})

  useEffect(() => {
    fetch(`/api/products/${articleId}`)
      .then(r => r.json())
      .then(data => {
        setProduct(data.product)
        setRecs(data.recommendations)
      })
  }, [articleId])

  return (
    <div>
      <ProductDetails product={product} />
      <RecommendationCarousel 
        title="Similar Products" 
        items={recs.similar_products} 
      />
      <RecommendationCarousel 
        title="Often Bought Together" 
        items={recs.often_bought_together} 
      />
    </div>
  )
}
```

### Example 2: Homepage Feed with Personalization

**Backend:**
```python
@router.get("/homepage")
def get_homepage(customer_id: str = None):
    response = {}
    
    if customer_id:
        # Personalized
        pers = requests.get(
            f"http://localhost:8000/hybrid-recommendations/personalized/{customer_id}",
            params={"limit": 12}
        ).json()
        response["personalized"] = pers.get("recommendations", [])
    
    # Always include trending
    trend = requests.get(
        "http://localhost:8000/hybrid-recommendations/trending",
        params={"limit": 20}
    ).json()
    response["trending"] = trend.get("trending_items", [])
    
    return response
```

### Example 3: Search Results with "You May Like"

```python
@router.get("/search")
def search_products(q: str, customer_id: str = None):
    # Perform search
    results = db.query(Product).filter(
        Product.name.contains(q)
    ).limit(20).all()
    
    # If few results, supplement with recommendations
    if len(results) < 20 and customer_id:
        recs = requests.get(
            f"http://localhost:8000/hybrid-recommendations/based-on-interactions/{customer_id}",
            params={"limit": 20 - len(results)}
        ).json()
        
        rec_ids = [r['article_id'] for r in recs.get("recommendations", [])]
        supplement = db.query(Product).filter(Product.article_id.in_(rec_ids)).all()
        results.extend(supplement)
    
    return {"results": results, "count": len(results)}
```

---

## Common Patterns

### Pattern: Fallback to Trending for Missing Data

```typescript
async function getRecommendations(customerId: string): Promise<Item[]> {
  try {
    const res = await fetch(`/api/recommendations/personalized/${customerId}`)
    
    if (res.status === 404) {
      // Customer not found - use trending
      return getTrendingItems()
    }
    
    if (res.status === 503) {
      // Service down - use cache or fallback
      return getCachedRecommendations(customerId) || getTrendingItems()
    }
    
    const data = await res.json()
    return data.recommendations
    
  } catch (error) {
    console.error('Error fetching recommendations:', error)
    return getTrendingItems()
  }
}
```

### Pattern: Combine Multiple Recommendation Types

```javascript
async function getCompleteRecommendations(articleId, customerId) {
  const [similar, often, hybrid] = await Promise.all([
    fetch(`/api/recommendations/similar-products/${articleId}`),
    fetch(`/api/recommendations/often-bought/${articleId}`),
    fetch(`/api/recommendations/you-may-also-like-product/${articleId}`)
  ])

  return {
    byAttribute: (await similar.json()).similar_items,
    byBehavior: (await often.json()).similar_items,
    hybrid: (await hybrid.json()).similar_items
  }
}
```

### Pattern: Load with Proper Error States

```vue
<template>
  <div class="recommendations-section">
    <div v-if="loading" class="loading">Loading...</div>
    <div v-else-if="error" class="error">
      <p>{{ error }}</p>
      <button @click="retry">Retry</button>
    </div>
    <div v-else-if="items.length === 0" class="empty">
      No recommendations available
    </div>
    <div v-else class="items-grid">
      <ProductCard v-for="item in items" :key="item.article_id" :item="item" />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps(['endpoint'])
const items = ref([])
const loading = ref(false)
const error = ref(null)

async function load() {
  loading.value = true
  error.value = null
  
  try {
    const res = await fetch(props.endpoint)
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    
    const data = await res.json()
    items.value = data.similar_items || data.recommendations || data.trending_items || []
    
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

function retry() {
  load()
}

load()
</script>
```

---

## Error Handling

### HTTP Status Codes

| Code | Meaning | Action |
|------|---------|--------|
| 200 | Success | Use recommendations |
| 404 | Not Found | Use trending/fallback |
| 503 | Service Unavailable | Retry or use cache |
| 500 | Server Error | Log and fallback |

### Timeout Handling

```python
import requests

try:
    response = requests.get(
        "http://localhost:8000/hybrid-recommendations/trending",
        timeout=5  # 5 second timeout
    )
except requests.Timeout:
    # Use fallback or cached recommendations
    use_fallback_recommendations()
```

### Empty Results Handling

```javascript
// All endpoints return empty lists gracefully - never error
// Check count field
if (data.count === 0) {
  // No recommendations for this context
  // Show alternative content or trending
}
```

---

## Performance Considerations

### Caching Strategies

```python
# Client-side caching (1 hour for trending, 10 min for personalized)
CACHE_CONFIG = {
    'trending': 3600,      # 1 hour
    'personalized': 600,   # 10 minutes
    'similar': 3600,       # 1 hour (stable for a product)
}

# Server-side caching (already implemented)
# - Trending: 1-hour server cache
# - Others: No server cache (always fresh)
```

### Batch Loading

```javascript
// Load multiple recommendations in parallel
async function loadAllSections() {
  const requests = [
    fetch('/api/recommendations/personalized/{id}?limit=12'),
    fetch('/api/recommendations/customers-also-bought/{id}?limit=10'),
    fetch('/api/recommendations/based-on-interactions/{id}?limit=12'),
    fetch('/api/recommendations/trending?limit=20')
  ]
  
  const responses = await Promise.all(requests)
  return Promise.all(responses.map(r => r.json()))
}
```

### Lazy Loading

```vue
<template>
  <div class="sections">
    <RecommendationSection 
      v-for="section in sections" 
      :key="section.id"
      v-intersection-observer="{ threshold: 0.1 }"
      @visible="loadSection(section)"
      :items="section.items"
    />
  </div>
</template>

<script setup>
const sections = ref([
  { id: 'personalized', items: [] },
  { id: 'trending', items: [] }
])

function loadSection(section) {
  if (section.items.length > 0) return // Already loaded
  
  fetch(`/api/recommendations/${section.id}`)
    .then(r => r.json())
    .then(data => {
      section.items = data.recommendations || data.trending_items || []
    })
}
</script>
```

### Pagination/Infinite Scroll

```javascript
// Note: API doesn't support pagination offset, use limit parameter
// To implement pagination: fetch with higher limit and cache client-side

let allItems = []

async function loadMore() {
  if (allItems.length === 0) {
    // First load - get more than we'll show
    const res = await fetch('/api/recommendations/trending?limit=50')
    allItems = (await res.json()).trending_items
  }
  
  // Return next batch
  return allItems.splice(0, 10)
}
```

---

## Summary

### For Backend Teams
1. Import `RecommendationClient` in your services
2. Call appropriate endpoints based on context
3. Implement caching for performance
4. Handle 404/503 errors with fallbacks
5. Format responses for frontend

### For Frontend Teams
1. Load recommendations asynchronously
2. Display in appropriate sections
3. Use lazy loading for better UX
4. Handle loading/error states
5. Cache responses client-side

### Key Endpoints
- **Product Page:** similar-products, often-bought, you-may-also-like-product
- **Homepage:** personalized, customers-also-bought, based-on-interactions, trending

### Remember
- All recommendations are optional (empty arrays are valid)
- Fallback to trending for any errors
- System works best with CF models loaded
- CB models will improve coverage further

---

**For Questions or Issues:** Check `/api/hybrid-recommendations/health` endpoint for service status
