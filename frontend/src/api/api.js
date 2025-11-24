import axios from 'axios';
// Use relative path for API - this will work when deployed
const API_URL = '/api';

export const api = axios.create({ baseURL: API_URL });

// Products
export const fetchProducts = (limit=50, offset=0) => api.get(`/articles?limit=${limit}&offset=${offset}`);
export const fetchProductById = (id) => api.get(`/articles/${id}`);
export const fetchProductsWithSales = (limit=50, offset=0) => api.get(`/articles-sales?limit=${limit}&offset=${offset}`);
export const addProduct = (product) => api.post(`/articles`, product);
export const updateProduct = (id, product) => api.put(`/articles/${id}`, product);
export const deleteProduct = (id) => api.delete(`/articles/${id}`);
export const updateProductPrice = (id, price) => api.patch(`/articles/${id}/price`, { price });
export const updateProductStock = (id, stock) => api.patch(`/articles/${id}/stock`, { stock });

// Related Products
export const fetchRelatedProducts = (id, limit=8) => api.get(`/articles/${id}/related?limit=${limit}`);
export const fetchSimilarProducts = (id, limit=8) => api.get(`/articles/${id}/similar?limit=${limit}`);
export const fetchTrendingProducts = (limit=12) => api.get(`/articles/trending?limit=${limit}`);

// Customers
export const fetchCustomers = (limit=50, offset=0) => api.get(`/customers?limit=${limit}&offset=${offset}`);
export const fetchCustomerById = (id) => api.get(`/customers/${id}`);
export const updateCustomer = (id, customer) => api.put(`/customers/${id}`, customer);

// Orders
export const fetchOrders = (limit=50, offset=0) => api.get(`/orders?limit=${limit}&offset=${offset}`);
export const fetchOrderById = (id) => api.get(`/orders/${id}`);

// Reviews
export const fetchReviewsByProduct = (productId) => api.get(`/reviews?article_id=${productId}`);
export const postReview = (review) => api.post(`/reviews`, review);
export const fetchAllReviews = (limit=50, offset=0) => api.get(`/reviews?limit=${limit}&offset=${offset}`);

// Contact Form
export const submitContactForm = (formData) => api.post(`/contact/submit`, formData);

// Categories
export const fetchCategories = (limit=100, offset=0) => api.get(`/categories?limit=${limit}&offset=${offset}`);
export const createCategory = (category) => api.post(`/categories`, category);
export const updateCategory = (id, category) => api.put(`/categories/${id}`, category);
export const deleteCategory = (id) => api.delete(`/categories/${id}`);

// Events
export const fetchEvents = (limit=100, offset=0) => api.get(`/events?limit=${limit}&offset=${offset}`);

// Transactions, wishlist, cart can be added similarly