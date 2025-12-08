# 🔗 FastAPI + React Full-Stack E-Commerce Integration

## 📖 Overview

This project is a complete full-stack e-commerce platform connecting a **FastAPI backend** with a **React frontend**. The backend handles a massive H&M dataset with advanced PostgreSQL functions, while the frontend provides a modern shopping experience.

---

## 🎯 What Has Been Completed

### ✅ Backend Integration Layer
- **Complete API wrapper** for all backend endpoints
- **Axios interceptors** for automatic JWT token injection
- **Auto-logout** on token expiration (401 responses)
- **Error handling** utilities

**File:** `frontend/src/api/api.js` (286 lines)

### ✅ Global State Management
- **React Context API** for app-wide state
- **Auto-sync** cart and wishlist with backend
- **Persistent authentication** via localStorage
- **User and admin** state management

**File:** `frontend/src/context/AppContext.jsx` (318 lines)

### ✅ Protected Routes
- **Customer-only routes** with auto-redirect
- **Admin-only routes** with admin token enforcement
- **Loading states** during authentication checks

**File:** `frontend/src/components/ProtectedRoute.jsx` (47 lines)

### ✅ Authentication Pages
- **Login page** with Customer/Admin toggle
- **Signup page** with complete registration form
- **Backend integration** with JWT tokens
- **Auto-navigation** after successful auth

**Files:**
- `frontend/src/pages/Login.jsx` (110 lines)
- `frontend/src/pages/Signup.jsx` (289 lines)

### ✅ Customer Pages (Integrated)
- **Home page** - Dynamic sections and products
- **Cart page** - Backend-synced shopping cart

**Files:**
- `frontend/src/pages/Home.jsx` (197 lines)
- `frontend/src/pages/Cart.jsx` (175 lines)

---

## 🚀 Quick Start

### Prerequisites
- Node.js 16+ 
- Python 3.8+
- PostgreSQL database
- Backend already running

### 1. Install Frontend Dependencies
```bash
cd frontend
npm install
```

### 2. Configure Environment
The `.env` file is already created with:
```env
REACT_APP_API_URL=http://localhost:8000
```

### 3. Start Frontend
```bash
npm start
```

The app will open at `http://localhost:3000`

### 4. Test Authentication
- **Customer Signup:** Create a new account
- **Customer Login:** Login with created account
- **Admin Login:** Toggle to admin and use admin credentials

---

## 📂 Project Structure

```
frontend/
├── src/
│   ├── api/
│   │   └── api.js                 # ✅ Complete API integration layer
│   ├── context/
│   │   └── AppContext.jsx         # ✅ Global state management
│   ├── components/
│   │   ├── ProtectedRoute.jsx     # ✅ Route guards
│   │   ├── Navbar.jsx
│   │   ├── Footer.jsx
│   │   ├── ProductCard.jsx
│   │   └── CartItem.jsx
│   ├── pages/
│   │   ├── Home.jsx               # ✅ Integrated
│   │   ├── Login.jsx              # ✅ Integrated
│   │   ├── Signup.jsx             # ✅ Integrated
│   │   ├── Cart.jsx               # ✅ Integrated
│   │   ├── Wishlist.jsx           # 🔄 To be integrated
│   │   ├── Checkout.jsx           # 🔄 To be integrated
│   │   ├── ProductListing.jsx     # 🔄 To be integrated
│   │   ├── ProductDetail.jsx      # 🔄 To be integrated
│   │   ├── Profile.jsx            # 🔄 To be integrated
│   │   ├── OrdersHistory.jsx      # 🔄 To be integrated
│   │   └── admin/
│   │       └── [admin pages]      # 🔄 To be integrated
│   ├── App.jsx                    # ✅ With AppProvider
│   └── index.js
├── .env                           # ✅ Created
└── package.json
```

---

## 🔑 Key Features

### 1. Automatic JWT Authentication
```javascript
// No need to manually add tokens - interceptor handles it!
import { articles } from '../api/api';

const products = await articles.getAll();  // Token auto-injected
```

### 2. Global State Access
```javascript
import { useApp } from '../context/AppContext';

function MyComponent() {
  const { 
    user,          // Current customer
    cartItems,     // Synced with backend
    addToCart      // Add item with one call
  } = useApp();
}
```

### 3. Protected Routes
```javascript
// In App.jsx - already configured
<Route path='/cart' element={
  <ProtectedRoute>
    <Cart />
  </ProtectedRoute>
} />
```

---

## 📋 Available API Functions

### Authentication
```javascript
import { customerAuth, adminAuth } from '../api/api';

// Customer
await customerAuth.signup(data);
await customerAuth.login({ email, password });
const user = await customerAuth.me();

// Admin
await adminAuth.login({ username_or_email, password });
const admin = await adminAuth.me();
const logs = await adminAuth.getLogs(100);
```

### Catalog Navigation
```javascript
import { sections, articles } from '../api/api';

// Get all sections (Men, Women, Kids, etc.)
const sections = await sections.getSections();

// Get products by section
const products = await sections.getSectionProducts('women', 24, 0);

// Get categories within section
const categories = await sections.getSectionCategories('men');

// Get products by category
const items = await sections.getCategoryProducts('women', 'Dresses', 'popular');

// Filter and sort
const filtered = await sections.filterAndSort('women', 'Tops', {
  price_min: 10,
  price_max: 100,
  sort_option: 'price_asc'
});
```

### Cart Management
```javascript
import { cart } from '../api/api';
// OR use context methods
const { addToCart, removeFromCart } = useApp();

// Via context (recommended)
await addToCart(articleId, quantity);
await removeFromCart(cartId);
await updateCartItem(cartId, newQuantity);
await clearCart();

// Direct API calls
await cart.get();
await cart.addItem({ customer_id, article_id, quantity });
await cart.update(cartId, { quantity });
await cart.remove(cartId);
```

### Wishlist Management
```javascript
import { wishlist } from '../api/api';

await wishlist.add(articleId);
await wishlist.get();
await wishlist.moveToCart(wishlistId);
await wishlist.remove(wishlistId);
```

### Orders
```javascript
import { orders } from '../api/api';

// Create order from cart
await orders.create(shippingAddress);

// Create order with specific items
await orders.createWithItems({
  customer_id,
  shipping_address,
  payment_status: 'pending',
  items: [{ article_id, quantity }]
});

// Get customer orders
const myOrders = await orders.getMyOrders();

// Get order details
const details = await orders.getDetails(orderId);

// Admin: Update order status
await orders.updateStatus(orderId, 'completed');
```

### Reviews
```javascript
import { reviews } from '../api/api';

// Get reviews for product
const productReviews = await reviews.getByArticle(articleId);

// Create review
await reviews.createAuthenticated({
  customer_id,
  article_id,
  review_text: 'Great product!'
});

// Update review
await reviews.update(reviewId, { review_text: 'Updated review' });

// Delete review
await reviews.delete(reviewId);

// Get article stats
const stats = await reviews.getArticleStats(articleId);
```

### Customer Analytics
```javascript
import { customers } from '../api/api';

// Get RFM score
const rfm = await customers.getRFM(customerId);

// Get Customer Lifetime Value
const clv = await customers.getCLV(customerId);

// Get purchase frequency
const freq = await customers.getPurchaseFrequency(customerId);

// Get customer features
const features = await customers.getFeatures(customerId);
```

---

## 🎨 Integration Patterns

### Pattern 1: Load Data on Mount
```javascript
import { articles } from '../api/api';

function ProductListing() {
  const [products, setProducts] = useState([]);
  
  useEffect(() => {
    articles.getAll()
      .then(res => setProducts(res.data))
      .catch(err => console.error(err));
  }, []);
  
  return <div>{/* Render products */}</div>;
}
```

### Pattern 2: Use Context for Cart Operations
```javascript
import { useApp } from '../context/AppContext';

function ProductCard({ product }) {
  const { addToCart } = useApp();
  
  const handleAddToCart = async () => {
    const result = await addToCart(product.article_id, 1);
    
    if (result.success) {
      alert('Added to cart!');
    } else {
      alert(result.error);
    }
  };
  
  return (
    <div>
      <button onClick={handleAddToCart}>Add to Cart</button>
    </div>
  );
}
```

### Pattern 3: Protected Operations
```javascript
import { useApp } from '../context/AppContext';
import { useNavigate } from 'react-router-dom';

function Component() {
  const { user } = useApp();
  const navigate = useNavigate();
  
  const handleAction = () => {
    if (!user) {
      navigate('/login');
      return;
    }
    
    // Proceed with authenticated action
  };
}
```

### Pattern 4: Error Handling
```javascript
import { handleApiError } from '../api/api';

try {
  const response = await orders.create(address);
  alert('Success!');
} catch (error) {
  const message = handleApiError(error);
  alert(message);
}
```

---

## 🔐 Authentication Flow

### Customer Authentication
```
1. User fills login form
2. Click "Login" button
3. `login(email, password)` called from context
4. Backend validates credentials
5. Backend returns JWT token
6. Token saved in localStorage
7. `customerAuth.me()` called to get user data
8. User data saved in context
9. Cart and wishlist auto-loaded
10. Redirect to /profile
```

### Admin Authentication
```
1. Toggle to "Admin" mode
2. Enter username/email + password
3. `loginAdmin(username, password)` called
4. Backend validates admin credentials
5. Backend returns JWT token
6. Admin token saved separately
7. `adminAuth.me()` called to get admin data
8. Admin data saved in context
9. Redirect to /admin
```

### Token Auto-Injection
```
Every API request →
Request Interceptor →
Check for token →
Add Authorization: Bearer {token} →
Send to backend
```

### Auto-Logout
```
API request returns 401 →
Response Interceptor →
Remove tokens from localStorage →
Clear user/admin state →
Redirect to /login
```

---

## 📊 Backend Endpoints Used

### Customer Endpoints
- `POST /customers/auth/signup` - Register new customer
- `POST /customers/auth/login` - Customer login
- `GET /customers/auth/me` - Get current customer
- `GET /customers/{id}/rfm` - RFM analytics
- `GET /customers/{id}/clv` - Lifetime value
- `GET /customers/{id}/orders` - Customer orders

### Admin Endpoints
- `POST /admins/login` - Admin login
- `GET /admins/me` - Get current admin
- `GET /admins/logs` - Activity logs
- `PUT /admins/articles/{id}` - Update product
- `DELETE /admins/reviews/{id}` - Delete review

### Catalog Endpoints
- `GET /sections/` - Get all sections
- `GET /sections/{section}/products` - Section products
- `GET /sections/{section}/categories` - Section categories
- `GET /sections/{section}/{category}/products` - Category products
- `POST /sections/{section}/{category}/filter-sort` - Filter/sort

### Cart & Wishlist
- `GET /cart/` - Get customer cart
- `POST /cart/add-item` - Add to cart
- `PUT /cart/{cart_id}` - Update cart item
- `DELETE /cart/{cart_id}` - Remove from cart
- `GET /wishlist/` - Get customer wishlist
- `POST /wishlist/add-item` - Add to wishlist
- `DELETE /wishlist/item/{id}` - Remove from wishlist

### Orders
- `GET /orders/my-orders` - Customer's orders
- `POST /orders/create` - Create from cart
- `POST /orders/create-with-items` - Create with items
- `GET /orders/{id}/details` - Order details
- `PUT /orders/{id}/status` - Update status (admin)

### Reviews
- `GET /reviews/article/{id}` - Product reviews
- `POST /reviews/` - Create review
- `PUT /reviews/{id}` - Update review
- `DELETE /reviews/{id}` - Delete review

---

## 🧪 Testing

### Test Customer Flow
1. Go to `/signup`
2. Fill in all required fields
3. Submit form
4. Should auto-login and redirect to `/profile`
5. Navigate to `/products`
6. Click on a product
7. Add to cart
8. Go to `/cart`
9. Verify item appears
10. Update quantity
11. Proceed to checkout

### Test Admin Flow
1. Go to `/login`
2. Toggle to "Admin"
3. Enter admin credentials
4. Should redirect to `/admin`
5. View dashboard statistics
6. Manage products
7. View orders
8. View logs

### Test Protected Routes
1. Logout (if logged in)
2. Try to access `/cart`
3. Should redirect to `/login`
4. Login as customer
5. `/cart` should now be accessible
6. Try to access `/admin`
7. Should redirect (not authorized)

---

## 🐛 Troubleshooting

### Issue: Network Error
**Solution:** Ensure backend is running on http://localhost:8000

### Issue: 401 Unauthorized
**Solution:** Token expired, login again

### Issue: CORS Error
**Solution:** Check backend CORS configuration allows `http://localhost:3000`

### Issue: Empty Cart/Wishlist
**Solution:** User must be logged in to see cart/wishlist

### Issue: Components Not Updating
**Solution:** Ensure you're using context methods (addToCart, etc.) not direct API calls

---

## 📈 Next Steps

### High Priority Pages to Integrate
1. **Wishlist.jsx** - Replace localStorage with backend
2. **Checkout.jsx** - Create orders from cart
3. **ProductListing.jsx** - Section/category filtering
4. **ProductDetail.jsx** - Product info + add to cart
5. **Profile.jsx** - Customer info + analytics
6. **OrdersHistory.jsx** - List customer orders

### Admin Dashboard Pages
1. **DashboardOverview.jsx** - Stats and charts
2. **ProductsView.jsx** - Product management
3. **ProductAdd.jsx** - Create products
4. **ProductPrice/Stock.jsx** - Update pricing/stock
5. **OrdersView.jsx** - Order management
6. **ReviewsView.jsx** - Review moderation
7. **LogsView.jsx** - Activity monitoring

### Enhancements
- Toast notifications (react-toastify)
- Loading skeletons
- Image uploads
- Advanced search
- Pagination
- WebSocket real-time updates

---

## 📚 Documentation

- **INTEGRATION_STATUS.md** - Detailed integration status
- **SETUP_GUIDE.md** - Complete setup and usage guide
- **INTEGRATION_SUMMARY.md** - High-level overview
- **INTEGRATION_README.md** - This file

---

## 🎉 Success!

**You now have a production-ready foundation with:**
✅ Complete API integration  
✅ Global state management  
✅ JWT authentication  
✅ Protected routes  
✅ Working cart system  
✅ Clean architecture  

**The hard work is done - now connect the remaining pages following the same patterns!** 🚀

---

## 📞 Quick Reference

### Important URLs
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- Swagger Docs: http://localhost:8000/docs

### Key Files
- API Layer: `src/api/api.js`
- Global State: `src/context/AppContext.jsx`
- Protected Routes: `src/components/ProtectedRoute.jsx`
- App Config: `src/App.jsx`

### Environment
- API URL: Set in `frontend/.env`
- Tokens: Stored in localStorage
- State: Managed by AppContext

---

**Happy Coding! 🎊**
