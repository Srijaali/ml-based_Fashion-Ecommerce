# 🚀 FastAPI + React Integration - Complete Setup Guide

## ✅ WHAT HAS BEEN COMPLETED

### 1. **Complete API Integration Layer** (`frontend/src/api/api.js`)

A comprehensive API service layer with:
- ✅ Full CRUD operations for all backend endpoints
- ✅ JWT authentication with automatic token injection
- ✅ Auto-logout on token expiration (401 responses)
- ✅ Organized by domain (auth, articles, cart, orders, etc.)
- ✅ Error handling utilities

**Key Features:**
```javascript
// Automatic token injection via interceptor
// No need to manually add Authorization header
import { articles } from '../api/api';

const products = await articles.getAll();
```

### 2. **Global State Management** (`frontend/src/context/AppContext.jsx`)

Centralized application state using React Context:
- ✅ User authentication (customer & admin)
- ✅ Cart management with backend sync
- ✅ Wishlist management with backend sync
- ✅ Auto-load user data on app mount
- ✅ Persistent authentication via localStorage

**Usage:**
```javascript
import { useApp } from '../context/AppContext';

function MyComponent() {
  const { 
    user,           // Current logged-in customer
    admin,          // Current logged-in admin
    cartItems,      // Synced with backend
    wishlistItems,  // Synced with backend
    login,          // Customer login
    loginAdmin,     // Admin login
    addToCart,      // Add item to cart
    addToWishlist   // Add item to wishlist
  } = useApp();
}
```

### 3. **Protected Routes** (`frontend/src/components/ProtectedRoute.jsx`)

Secure routing with authentication checks:
- ✅ `ProtectedRoute` - for customer-only pages
- ✅ `ProtectedRouteAdmin` - for admin-only pages
- ✅ Auto-redirect to login if unauthenticated
- ✅ Loading states during auth check

**Already Applied To:**
- Cart, Wishlist, Checkout
- Profile, Settings, Orders
- Admin Dashboard (all routes)

### 4. **Updated Pages**

#### Authentication
- ✅ **Login.jsx** - Customer/Admin toggle, backend integration
- ✅ **Signup.jsx** - Full registration form with all required fields

#### Customer Pages
- ✅ **Home.jsx** - Sections API, featured products
- ✅ **Cart.jsx** - Backend cart sync, CRUD operations

---

## 📋 REMAINING PAGES TO UPDATE

### High Priority

#### 1. **Wishlist.jsx**
```javascript
// Update to use backend
import { useApp } from '../context/AppContext';

function Wishlist() {
  const { wishlistItems, removeFromWishlist, moveWishlistToCart } = useApp();
  // Replace localStorage logic with context methods
}
```

#### 2. **Checkout.jsx**
```javascript
import { useApp } from '../context/AppContext';
import { orders } from '../api/api';

function Checkout() {
  const { cartItems, clearCart, user } = useApp();
  
  const handlePlaceOrder = async (shippingAddress) => {
    // Option 1: Simple order from cart
    const response = await orders.create(shippingAddress);
    
    // Option 2: Order with items
    await orders.createWithItems({
      customer_id: user.customer_id,
      shipping_address: shippingAddress,
      payment_status: 'pending',
      items: cartItems.map(item => ({
        article_id: item.article_id,
        quantity: item.quantity
      }))
    });
    
    await clearCart();
    navigate('/orders');
  };
}
```

#### 3. **ProductListing.jsx**
```javascript
import { sections } from '../api/api';
import { useSearchParams } from 'react-router-dom';

function ProductListing() {
  const [searchParams] = useSearchParams();
  const section = searchParams.get('section') || 'women';
  const category = searchParams.get('category');
  
  useEffect(() => {
    if (category) {
      // Load category products
      sections.getCategoryProducts(section, category)
        .then(res => setProducts(res.data.products));
    } else {
      // Load section products
      sections.getSectionProducts(section)
        .then(res => setProducts(res.data.products));
    }
  }, [section, category]);
}
```

#### 4. **ProductDetail.jsx**
```javascript
import { articles, reviews } from '../api/api';
import { useApp } from '../context/AppContext';
import { useParams } from 'react-router-dom';

function ProductDetail() {
  const { id } = useParams();
  const { addToCart, addToWishlist } = useApp();
  const [product, setProduct] = useState(null);
  const [productReviews, setProductReviews] = useState([]);
  
  useEffect(() => {
    articles.getById(id).then(res => setProduct(res.data));
    reviews.getByArticle(id).then(res => setProductReviews(res.data));
  }, [id]);
  
  const handleAddToCart = async () => {
    const result = await addToCart(id, 1);
    if (result.success) {
      alert('Added to cart!');
    } else {
      alert(result.error);
    }
  };
}
```

#### 5. **Profile.jsx**
```javascript
import { useApp } from '../context/AppContext';
import { customers } from '../api/api';

function Profile() {
  const { user } = useApp();
  const [rfm, setRfm] = useState(null);
  const [clv, setClv] = useState(null);
  
  useEffect(() => {
    if (user) {
      customers.getRFM(user.customer_id).then(res => setRfm(res.data));
      customers.getCLV(user.customer_id).then(res => setClv(res.data));
    }
  }, [user]);
  
  return (
    <div>
      <h1>Welcome, {user?.first_name}</h1>
      <div>RFM Score: {rfm?.rfm_score}</div>
      <div>Customer Lifetime Value: ${clv?.clv}</div>
    </div>
  );
}
```

#### 6. **OrdersHistory.jsx**
```javascript
import { orders } from '../api/api';

function OrdersHistory() {
  const [myOrders, setMyOrders] = useState([]);
  
  useEffect(() => {
    orders.getMyOrders()
      .then(res => setMyOrders(res.data))
      .catch(err => console.error(err));
  }, []);
}
```

### Medium Priority

#### 7. **Reviews.jsx**
```javascript
import { reviews } from '../api/api';
import { useApp } from '../context/AppContext';

function Reviews() {
  const { user } = useApp();
  
  const handleSubmitReview = async (articleId, text) => {
    if (!user) {
      alert('Please login to review');
      return;
    }
    
    const result = await reviews.createAuthenticated({
      customer_id: user.customer_id,
      article_id: articleId,
      review_text: text
    });
  };
}
```

#### 8. **SearchResults.jsx**
```javascript
import { sections, articles } from '../api/api';
import { useSearchParams } from 'react-router-dom';

function SearchResults() {
  const [searchParams] = useSearchParams();
  const query = searchParams.get('q');
  
  useEffect(() => {
    // Use filter/sort or search endpoint
    articles.getAll()
      .then(res => {
        // Filter by query on frontend or use backend search
        const filtered = res.data.filter(p => 
          p.prod_name.toLowerCase().includes(query.toLowerCase())
        );
        setResults(filtered);
      });
  }, [query]);
}
```

---

## 🔧 ADMIN DASHBOARD PAGES

All admin pages need to connect to backend. They automatically use admin token via interceptor.

### 1. **DashboardOverview.jsx**
```javascript
import { orders, customers, articles } from '../api/api';

function DashboardOverview() {
  useEffect(() => {
    // Load stats
    orders.getDailySales().then(res => setSales(res.data));
    customers.getAll(0, 10).then(res => setRecentCustomers(res.data));
    orders.getAll(0, 10).then(res => setRecentOrders(res.data));
  }, []);
}
```

### 2. **ProductsView.jsx**
```javascript
import { articles } from '../api/api';

function ProductsView() {
  const [products, setProducts] = useState([]);
  
  useEffect(() => {
    articles.getAll().then(res => setProducts(res.data));
  }, []);
  
  const handleDelete = async (id) => {
    await articles.delete(id);
    // Reload products
  };
}
```

### 3. **ProductAdd.jsx**
```javascript
import { articles } from '../api/api';

function ProductAdd() {
  const handleSubmit = async (formData) => {
    await articles.create(formData);
    navigate('/admin/products');
  };
}
```

### 4. **ProductPrice.jsx & ProductStock.jsx**
```javascript
import { articles } from '../api/api';

function ProductPrice() {
  const handleUpdatePrice = async (id, newPrice) => {
    await articles.update(id, { price: newPrice });
  };
}
```

### 5. **OrdersView.jsx**
```javascript
import { orders } from '../api/api';

function OrdersView() {
  const [allOrders, setAllOrders] = useState([]);
  
  useEffect(() => {
    orders.getAll().then(res => setAllOrders(res.data));
  }, []);
  
  const updateStatus = async (orderId, status) => {
    await orders.updateStatus(orderId, status);
  };
}
```

### 6. **ReviewsView.jsx**
```javascript
import { reviews } from '../api/api';

function ReviewsView() {
  const [allReviews, setAllReviews] = useState([]);
  
  useEffect(() => {
    reviews.getAll().then(res => setAllReviews(res.data));
  }, []);
  
  const handleDelete = async (reviewId) => {
    await reviews.delete(reviewId); // Admin can delete any review
  };
}
```

### 7. **CategoriesView.jsx**
```javascript
import { categories } from '../api/api';

function CategoriesView() {
  const handleCreate = async (data) => {
    await categories.create(data);
  };
  
  const handleUpdate = async (id, data) => {
    await categories.update(id, data);
  };
}
```

### 8. **LogsView.jsx**
```javascript
import { adminAuth } from '../api/api';

function LogsView() {
  const [logs, setLogs] = useState([]);
  
  useEffect(() => {
    adminAuth.getLogs(200).then(res => setLogs(res.data));
  }, []);
}
```

### 9. **CustomersView.jsx**
```javascript
import { customers } from '../api/api';

function CustomersView() {
  const [allCustomers, setAllCustomers] = useState([]);
  
  useEffect(() => {
    customers.getAll().then(res => setAllCustomers(res.data));
  }, []);
}
```

---

## 🎯 ENVIRONMENT SETUP

### 1. Create `.env` file in `frontend/` directory:
```env
REACT_APP_API_URL=http://localhost:8000
```

### 2. Start Backend:
```bash
cd backend/app
uvicorn main:app --reload
```

### 3. Start Frontend:
```bash
cd frontend
npm start
```

---

## 📝 KEY PATTERNS

### Pattern 1: Load Data on Mount
```javascript
useEffect(() => {
  articles.getAll()
    .then(res => setProducts(res.data))
    .catch(err => console.error(err));
}, []);
```

### Pattern 2: Use Context for Cart/Wishlist
```javascript
const { addToCart, cartItems } = useApp();

const handleAdd = async (productId) => {
  const result = await addToCart(productId, 1);
  if (result.success) {
    alert('Added!');
  }
};
```

### Pattern 3: Protected Operations
```javascript
const { user } = useApp();

if (!user) {
  alert('Please login first');
  return;
}

// Proceed with operation
```

### Pattern 4: Error Handling
```javascript
try {
  const response = await orders.create(address);
  alert('Order placed successfully!');
} catch (error) {
  alert(error.response?.data?.detail || 'Something went wrong');
}
```

---

## 🔐 AUTHENTICATION FLOWS

### Customer Login
```javascript
const { login } = useApp();

const result = await login(email, password);
if (result.success) {
  navigate('/profile');
} else {
  setError(result.error);
}
```

### Admin Login
```javascript
const { loginAdmin } = useApp();

const result = await loginAdmin(username, password);
if (result.success) {
  navigate('/admin');
} else {
  setError(result.error);
}
```

### Check Auth Status
```javascript
const { user, admin, isAuthenticated, isAdmin } = useApp();

if (isAuthenticated) {
  // Show customer features
}

if (isAdmin) {
  // Show admin features
}
```

---

## ✅ TESTING CHECKLIST

### Backend Setup
- [ ] Backend running on `http://localhost:8000`
- [ ] Can access Swagger docs at `/docs`
- [ ] Admin account created
- [ ] Database populated with test data

### Frontend Setup
- [ ] Environment variable set
- [ ] Dependencies installed (`npm install`)
- [ ] Context provider wrapping App
- [ ] Protected routes configured

### Authentication
- [ ] Customer signup works
- [ ] Customer login works
- [ ] Admin login works
- [ ] Token persists on page refresh
- [ ] Auto-logout on token expiration
- [ ] Redirect to login when accessing protected routes

### Cart & Wishlist
- [ ] Add to cart works
- [ ] Remove from cart works
- [ ] Update cart quantity works
- [ ] Cart syncs across tabs/refresh
- [ ] Wishlist operations work similarly

### Orders
- [ ] Checkout creates order
- [ ] Order appears in history
- [ ] Cart cleared after checkout

### Admin
- [ ] Admin can view all orders
- [ ] Admin can update order status
- [ ] Admin can CRUD products
- [ ] Admin can view logs

---

## 🚀 DEPLOYMENT NOTES

### Environment Variables
Production `.env`:
```env
REACT_APP_API_URL=https://your-backend-domain.com
```

### Build
```bash
npm run build
```

### CORS
Ensure backend allows frontend domain in CORS settings:
```python
# backend/app/main.py
origins = [
    "http://localhost:3000",
    "https://your-frontend-domain.com"
]
```

---

## 📞 QUICK REFERENCE

### Available API Modules
- `customerAuth` - signup, login, me, logout
- `adminAuth` - login, me, logs, changePassword
- `sections` - getSections, getSectionProducts, etc.
- `articles` - CRUD operations for products
- `cart` - add, remove, update, get
- `wishlist` - add, remove, moveToCart
- `orders` - create, getMyOrders, getDetails
- `reviews` - CRUD operations
- `customers` - CRUD + analytics (RFM, CLV)
- `categories` - CRUD operations

### Context Methods
- `login(email, password)` - Customer login
- `loginAdmin(username, password)` - Admin login
- `signup(data)` - Customer signup
- `logout()` - Customer logout
- `logoutAdmin()` - Admin logout
- `addToCart(articleId, quantity)` - Add to cart
- `removeFromCart(cartId)` - Remove from cart
- `updateCartItem(cartId, quantity)` - Update quantity
- `addToWishlist(articleId)` - Add to wishlist
- `removeFromWishlist(wishlistId)` - Remove from wishlist

---

## 🎉 YOU'RE READY!

The foundation is complete. Now you can:
1. Update remaining customer pages following the patterns above
2. Connect admin dashboard pages
3. Test the full flow
4. Deploy to production

**All the hard work of setting up authentication, interceptors, state management, and API layer is DONE!** ✨
