import axios from 'axios';

// ============================================
// BASE API CONFIGURATION
// ============================================
export const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Create axios instance
export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ============================================
// TOKEN MANAGEMENT
// ============================================
export const getToken = () => localStorage.getItem('token');
export const getAdminToken = () => localStorage.getItem('adminToken');
export const setToken = (token) => localStorage.setItem('token', token);
export const setAdminToken = (token) => localStorage.setItem('adminToken', token);
export const removeToken = () => localStorage.removeItem('token');
export const removeAdminToken = () => localStorage.removeItem('adminToken');

// ============================================
// ============================================
// AXIOS INTERCEPTORS
// ============================================

// Request interceptor - Attach JWT token
api.interceptors.request.use(
  (config) => {
    const token = getToken();
    const adminToken = getAdminToken();

    // Determine which token to use based on the request URL
    let authToken = null;

    // If requesting admin endpoints, use admin token
    if (config.url.startsWith('/admins/') || config.url.includes('/admins')) {
      authToken = adminToken;
    }
    // If requesting customer endpoints, use customer token
    else if (config.url.startsWith('/customers/') ||
      config.url.startsWith('/cart') ||
      config.url.startsWith('/wishlist') ||
      config.url.startsWith('/orders')) {
      authToken = token;
    }
    // For other endpoints, prefer admin token if available
    else {
      authToken = token || adminToken;
    }

    if (authToken) {
      config.headers.Authorization = `Bearer ${authToken}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

api.interceptors.response.use(
  (response) => response,
  (error) => {
    // If backend returns 401 Unauthorized
    if (error.response?.status === 401) {
      console.warn("🚫 Token expired or invalid — clearing auth…");

      // Remove BOTH tokens
      removeToken();
      removeAdminToken();

      // Remove stored user/admin data
      localStorage.removeItem("user");
      localStorage.removeItem("admin");

      // Only redirect if NOT already on login page
      const current = window.location.pathname;
      if (!current.includes("/login") && !current.includes("/admin/login")) {
        window.location.href = "/login";
      }
    }

    return Promise.reject(error);
  }
);


// ============================================
// AUTHENTICATION - CUSTOMER
// ============================================
export const customerAuth = {
  signup: (data) => api.post('/customers/auth/signup', data),
  login: (data) => api.post('/customers/auth/login', data),
  me: () => api.get('/customers/auth/me'),
  logout: () => {
    removeToken();
    localStorage.removeItem('user');
  },
};

// ============================================
// AUTHENTICATION - ADMIN
// ============================================
export const adminAuth = {
  login: (data) => api.post('/admins/login', data),
  me: () => api.get('/admins/me'),
  logout: () => {
    removeAdminToken();
    localStorage.removeItem('admin');
  },
  changePassword: (data) => api.post('/admins/change-password', data),
  createAdmin: (data) => api.post('/admins/', data),
  listAdmins: () => api.get('/admins/'),
  getLogs: (limit = 100) => api.get(`/admins/logs?limit=${limit}`),
};

// ============================================
// SECTIONS (Catalog Navigation)
// ============================================
export const sections = {
  getSections: () => api.get('/sections/'),
  getSectionProducts: (section, limit = 24, offset = 0) =>
    api.get(`/sections/${section}/products?limit=${limit}&offset=${offset}`),
  getSectionCategories: (section) => api.get(`/sections/${section}/categories`),
  getCategoryProducts: async (section, category, sort, limit, offset) =>
  axios.get(`${API_URL}/sections/${section}/${category}/products`, {
    params: {
      sort,
      limit,
      offset
    }
  }),
  getFilterOptions: (section, category) =>
    api.get(`/sections/${section}/${category}/filters`),
  filterAndSort: (section, category, data) =>
    api.post(`/sections/${section}/${category}/filter-sort`, data),
  getSectionProducts: async (section, limit, offset) =>
  axios.get(`${API_URL}/sections/${section}/products`, {
    params: { limit, offset }
  }),

};

// ============================================
// ARTICLES (Products)
// ============================================
export const articles = {
  getAll: (skip = 0, limit = 20) => api.get(`/articles?skip=${skip}&limit=${limit}`),
  getById: (id) => api.get(`/articles/${id}`),
  getByName: (name) => api.get(`/articles/by-name/${name}`),
  search: (query, skip = 0, limit = 50) => api.get(`/articles/search/${query}?skip=${skip}&limit=${limit}`),
  create: (data) => api.post('/articles/', data),
  update: (id, data) => api.put(`/articles/${id}`, data),
  delete: (id) => api.delete(`/articles/${id}`),

  // Analytics
  getPerformance: (id) => api.get(`/articles/${id}/performance`),
  getDemandTrend: (id) => api.get(`/articles/${id}/demand-trend`),
  getInventory: (id) => api.get(`/articles/${id}/inventory`),
  getFunnelMetrics: () => api.get('/articles/funnel-metrics'),
};

// Backward compatibility
export const fetchProducts = articles.getAll;
export const fetchProductById = articles.getById;
export const addProduct = articles.create;
export const updateProduct = articles.update;
export const deleteProduct = articles.delete;
export const fetchProductsWithSales = articles.getAll;  // Same as getAll for now
export const fetchRelatedProducts = (id, limit = 8) => articles.getAll(0, limit);  // Placeholder
export const fetchSimilarProducts = (id, limit = 8) => articles.getAll(0, limit);  // Placeholder
export const fetchTrendingProducts = (limit = 12) => articles.getAll(0, limit);  // Placeholder
export const updateProductPrice = (id, price) => articles.update(id, { price });
export const updateProductStock = (id, stock) => articles.update(id, { stock });

// ============================================
// CUSTOMERS
// ============================================
export const customers = {
  getAll: (skip = 0, limit = 100) => api.get(`/customers?skip=${skip}&limit=${limit}`),
  getById: (id) => api.get(`/customers/${id}`),
  create: (data) => api.post('/customers/', data),
  update: (id, data) => api.put(`/customers/${id}`, data),
  delete: (id) => api.delete(`/customers/${id}`),
  setActive: (id, active) => api.put(`/customers/${id}/active?active=${active}`),

  // Analytics
  getFeatures: (id) => api.get(`/customers/${id}/features`),
  getPurchaseFrequency: (id) => api.get(`/customers/${id}/purchase-frequency`),
  getCLV: (id) => api.get(`/customers/${id}/clv`),
  getRFM: (id) => api.get(`/customers/${id}/rfm`),
  getEvents: (id, skip = 0, limit = 100) =>
    api.get(`/customers/${id}/events?skip=${skip}&limit=${limit}`),
  getOrders: (id, skip = 0, limit = 100) =>
    api.get(`/customers/${id}/orders?skip=${skip}&limit=${limit}`),
};

// Backward compatibility
export const fetchCustomers = customers.getAll;
export const fetchCustomerById = customers.getById;
export const updateCustomer = customers.update;

// ============================================
// CART
// ============================================
export const cart = {
  get: () => api.get('/cart/'),
  getByCustomer: (customerId) => api.get(`/cart/customer/${customerId}`),
  add: (articleId, quantity = 1) => api.post('/cart/add', { article_id: articleId, quantity }),
  addItem: (data) => api.post('/cart/add-item', data),
  update: (cartId, data) => api.put(`/cart/${cartId}`, data),
  remove: (cartId) => api.delete(`/cart/${cartId}`),
  clear: (customerId) => api.delete(`/cart/clear/${customerId}`),
  getCount: (customerId) => api.get(`/cart/${customerId}/count`),
  getAll: (skip = 0, limit = 100) => api.get(`/cart/all?skip=${skip}&limit=${limit}`),
};

// ============================================
// WISHLIST
// ============================================
export const wishlist = {
  get: () => api.get('/wishlist/'),
  getByCustomer: (customerId) => api.get(`/wishlist/customer/${customerId}`),
  add: (articleId) => api.post('/wishlist/add', { article_id: articleId }),
  addItem: (data) => api.post('/wishlist/add-item', data),
  moveToCart: (wishlistId) => api.post(`/wishlist/move-to-cart/${wishlistId}`),
  remove: (wishlistId) => api.delete(`/wishlist/item/${wishlistId}`),
  clear: (customerId) => api.delete(`/wishlist/customer/${customerId}`),
};

// ============================================
// ORDERS
// ============================================
export const orders = {
  getMyOrders: () => api.get('/orders/my-orders'),
  create: (shippingAddress) => api.post(`/orders/create?shipping_address=${shippingAddress}`),
  createWithItems: (data) => api.post('/orders/create-with-items', data),
  getAll: (skip = 0, limit = 100) => api.get(`/orders?skip=${skip}&limit=${limit}`),
  getDetails: (orderId) => api.get(`/orders/${orderId}/details`),
  getByCustomer: (customerId, skip = 0, limit = 100) =>
    api.get(`/orders/customer/${customerId}?skip=${skip}&limit=${limit}`),
  filter: (params) => api.get('/orders/filter', { params }),
  updateStatus: (orderId, status) =>
    api.put(`/orders/${orderId}/status?payment_status=${status}`),
  updateAddress: (orderId, address) =>
    api.put(`/orders/${orderId}/address?new_address=${address}`),
  getDailySales: (skip = 0, limit = 50) =>
    api.get(`/orders/analytics/daily-sales?skip=${skip}&limit=${limit}`),
};

// Backward compatibility
export const fetchOrders = orders.getAll;
export const fetchOrderById = orders.getDetails;

// ============================================
// REVIEWS
// ============================================
export const reviews = {
  getAll: (skip = 0, limit = 100) => api.get(`/reviews?skip=${skip}&limit=${limit}`),
  getById: (id) => api.get(`/reviews/${id}`),
  getByArticle: (articleId) => api.get(`/reviews/article/${articleId}`),
  getByCustomer: (customerId) => api.get(`/reviews/customer/${customerId}`),
  create: (articleId, reviewText) =>
    api.post(`/reviews/create?article_id=${articleId}&review_text=${reviewText}`),
  createAuthenticated: (data) => api.post('/reviews/', data),
  update: (reviewId, data) => api.put(`/reviews/${reviewId}`, data),
  delete: (reviewId) => api.delete(`/reviews/${reviewId}`),
  getArticleStats: (articleId) => api.get(`/reviews/analytics/article/${articleId}`),
};

// Backward compatibility
export const fetchReviewsByProduct = reviews.getByArticle;
export const postReview = reviews.createAuthenticated;
export const fetchAllReviews = reviews.getAll;

// ============================================
// CATEGORIES
// ============================================
export const categories = {
  getAll: (limit = 100, offset = 0) => api.get(`/categories?limit=${limit}&offset=${offset}`),
  getById: (id) => api.get(`/categories/${id}`),
  create: (data) => api.post('/categories/', data),
  update: (id, data) => api.put(`/categories/${id}`, data),
  delete: (id) => api.delete(`/categories/${id}`),
};

// Backward compatibility
export const fetchCategories = categories.getAll;
export const createCategory = categories.create;
export const updateCategory = categories.update;
export const deleteCategory = categories.delete;

// ============================================
// EVENTS
// ============================================
export const events = {
  getAll: (limit = 100, offset = 0) => api.get(`/events?limit=${limit}&offset=${offset}`),
};

// Backward compatibility
export const fetchEvents = events.getAll;

// Contact Form (no backend endpoint - returns mock success)
export const submitContactForm = (formData) => Promise.resolve({ data: { message: 'Form submitted successfully' } });

// ============================================
// TRANSACTIONS
// ============================================
export const transactions = {
  delete: (id) => api.delete(`/transactions/${id}`),
};

// ============================================
// UTILITY FUNCTIONS
// ============================================
export const handleApiError = (error) => {
  if (error.response) {
    // Server responded with error
    return error.response.data?.detail || error.response.data?.message || 'An error occurred';
  } else if (error.request) {
    // Request made but no response
    return 'Network error. Please check your connection.';
  } else {
    // Something else happened
    return error.message || 'An unexpected error occurred';
  }
};

export default api;