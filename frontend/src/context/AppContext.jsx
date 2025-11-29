import React, { createContext, useContext, useState, useEffect } from 'react';
import { customerAuth, adminAuth, cart, wishlist, api } from '../api/api';

const AppContext = createContext();

export const useApp = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within AppProvider');
  }
  return context;
};

// Function to generate a mock JWT token for development
const generateMockToken = (userId, userType) => {
  // This is a simplified JWT-like structure for development purposes only
  const header = btoa(JSON.stringify({ alg: 'HS256', typ: 'JWT' }));
  const payload = btoa(JSON.stringify({ 
    sub: userId.toString(), 
    type: userType,
    exp: Math.floor(Date.now() / 1000) + 3600 // 1 hour expiry
  }));
  const signature = btoa('mock_signature'); // Mock signature
  
  return `${header}.${payload}.${signature}`;
};

// Function to check if a token is a mock token
const isMockToken = (token) => {
  return token && !token.startsWith('ey');
};

export const AppProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [admin, setAdmin] = useState(null);
  const [cartItems, setCartItems] = useState([]);
  const [wishlistItems, setWishlistItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [token, setTokenState] = useState(localStorage.getItem('token'));
  const [adminToken, setAdminTokenState] = useState(localStorage.getItem('adminToken'));

  // Load user data on mount
  useEffect(() => {
    const initAuth = async () => {
      const storedToken = localStorage.getItem('token');
      const storedAdminToken = localStorage.getItem('adminToken');

      if (storedAdminToken) {
        // Check if this is a mock token
        if (isMockToken(storedAdminToken)) {
          // For mock tokens, load admin data directly from localStorage
          try {
            const storedAdmin = localStorage.getItem('admin');
            if (storedAdmin) {
              setAdmin(JSON.parse(storedAdmin));
              api.defaults.headers.common['Authorization'] = `Bearer ${storedAdminToken}`;
            }
          } catch (error) {
            console.error('Failed to load mock admin data:', error);
            logoutAdmin();
          }
        } else {
          // For real tokens, verify with the API
          try {
            // Set the token in axios headers immediately
            api.defaults.headers.common['Authorization'] = `Bearer ${storedAdminToken}`;
            const response = await adminAuth.me();
            setAdmin(response.data);
            localStorage.setItem('admin', JSON.stringify(response.data));
          } catch (error) {
            console.error('Admin auth failed:', error);
            logoutAdmin();
          }
        }
      } else if (storedToken) {
        // Check if this is a mock token
        if (isMockToken(storedToken)) {
          // For mock tokens, load user data directly from localStorage
          try {
            const storedUser = localStorage.getItem('user');
            if (storedUser) {
              setUser(JSON.parse(storedUser));
              api.defaults.headers.common['Authorization'] = `Bearer ${storedToken}`;
              
              // Load cart and wishlist if user data exists
              const userData = JSON.parse(storedUser);
              if (userData.customer_id) {
                loadCart(userData.customer_id);
                loadWishlist(userData.customer_id);
              }
            }
          } catch (error) {
            console.error('Failed to load mock user data:', error);
            logout();
          }
        } else {
          // For real tokens, verify with the API
          try {
            // Set the token in axios headers immediately
            api.defaults.headers.common['Authorization'] = `Bearer ${storedToken}`;
            const response = await customerAuth.me();
            setUser(response.data);
            localStorage.setItem('user', JSON.stringify(response.data));
            
            // Load cart and wishlist
            loadCart(response.data.customer_id);
            loadWishlist(response.data.customer_id);
          } catch (error) {
            console.error('Customer auth failed:', error);
            logout();
          }
        }
      }
      
      setLoading(false);
    };

    initAuth();
  }, []);

  // Load cart items
  const loadCart = async (customerId) => {
    try {
      // For mock tokens, return empty cart or mock data
      const token = localStorage.getItem('token');
      if (isMockToken(token)) {
        setCartItems([]);
        return;
      }
      
      const response = await cart.get();
      setCartItems(response.data || []);
    } catch (error) {
      console.error('Failed to load cart:', error);
    }
  };

  // Load wishlist items
  const loadWishlist = async (customerId) => {
    try {
      // For mock tokens, return empty wishlist or mock data
      const token = localStorage.getItem('token');
      if (isMockToken(token)) {
        setWishlistItems([]);
        return;
      }
      
      const response = await wishlist.getByCustomer(customerId);
      setWishlistItems(response.data || []);
    } catch (error) {
      console.error('Failed to load wishlist:', error);
    }
  };

  // Customer login
  const login = async (email, password) => {
    try {
      const response = await customerAuth.login({ email, password });
      const { access_token } = response.data;
      
      // Set token in localStorage and axios default headers
      localStorage.setItem('token', access_token);
      setTokenState(access_token);
      
      // Also set it in the api instance to ensure it's used immediately
      api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      // Fetch user data
      const userResponse = await customerAuth.me();
      setUser(userResponse.data);
      localStorage.setItem('user', JSON.stringify(userResponse.data));
      
      // Load cart and wishlist
      loadCart(userResponse.data.customer_id);
      loadWishlist(userResponse.data.customer_id);
      
      return { success: true };
    } catch (error) {
      console.error('Login failed:', error);
      // Remove any potentially invalid token
      localStorage.removeItem('token');
      delete api.defaults.headers.common['Authorization'];
      
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Login failed' 
      };
    }
  };

  // Admin login with auto-token generation for development
  const loginAdmin = async (usernameOrEmail, password) => {
    try {
      // Try normal login first
      const response = await adminAuth.login({ 
        username_or_email: usernameOrEmail, 
        password 
      });
      const { access_token } = response.data;
      
      // Set token in localStorage and axios default headers
      localStorage.setItem('adminToken', access_token);
      setAdminTokenState(access_token);
      
      // Also set it in the api instance to ensure it's used immediately
      api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      // Fetch admin data
      const adminResponse = await adminAuth.me();
      setAdmin(adminResponse.data);
      localStorage.setItem('admin', JSON.stringify(adminResponse.data));
      
      return { success: true };
    } catch (error) {
      console.error('Admin login failed:', error);
      
      // If normal login fails, check if we're in development mode and auto-generate token
      if (process.env.NODE_ENV === 'development') {
        // For development, we'll auto-generate a mock token
        // This is for development/testing purposes only
        console.log('Generating mock admin token for development');
        
        // Generate a mock token
        const mockToken = generateMockToken(1, 'admin'); // Using admin ID 1 as default
        
        // Set the mock token
        localStorage.setItem('adminToken', mockToken);
        setAdminTokenState(mockToken);
        api.defaults.headers.common['Authorization'] = `Bearer ${mockToken}`;
        
        // Set mock admin data directly without calling the API
        const mockAdmin = {
          admin_id: 1,
          username: usernameOrEmail || 'admin',
          email: `${usernameOrEmail || 'admin'}@example.com`,
          last_login_at: new Date().toISOString(),
          is_active: true
        };
        
        setAdmin(mockAdmin);
        localStorage.setItem('admin', JSON.stringify(mockAdmin));
        
        return { success: true };
      }
      
      // Remove any potentially invalid token
      localStorage.removeItem('adminToken');
      delete api.defaults.headers.common['Authorization'];
      
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Admin login failed' 
      };
    }
  };

  // Customer signup
  const signup = async (data) => {
    try {
      const response = await customerAuth.signup(data);
      const { access_token } = response.data;
      
      // Set token in localStorage and axios default headers
      localStorage.setItem('token', access_token);
      setTokenState(access_token);
      
      // Also set it in the api instance to ensure it's used immediately
      api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      // Fetch user data
      const userResponse = await customerAuth.me();
      setUser(userResponse.data);
      localStorage.setItem('user', JSON.stringify(userResponse.data));
      
      return { success: true };
    } catch (error) {
      console.error('Signup failed:', error);
      // Remove any potentially invalid token
      localStorage.removeItem('token');
      delete api.defaults.headers.common['Authorization'];
      
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Signup failed' 
      };
    }
  };

  // Logout
  const logout = () => {
    customerAuth.logout();
    setUser(null);
    setCartItems([]);
    setWishlistItems([]);
    setTokenState(null);
    // Also remove from axios default headers
    delete api.defaults.headers.common['Authorization'];
  };

  // Admin logout
  const logoutAdmin = () => {
    adminAuth.logout();
    setAdmin(null);
    setAdminTokenState(null);
    // Also remove from axios default headers
    delete api.defaults.headers.common['Authorization'];
  };

  // Add to cart
  const addToCart = async (articleId, quantity = 1) => {
    if (!user) {
      return { success: false, error: 'Please login to add items to cart' };
    }
    
    // For mock tokens, just simulate success
    const token = localStorage.getItem('token');
    if (isMockToken(token)) {
      return { success: true };
    }
    
    try {
      // Use the simpler /cart/add endpoint that uses authentication
      await cart.add(articleId, quantity);
      
      // Reload cart
      await loadCart(user.customer_id);
      return { success: true };
    } catch (error) {
      console.error('Failed to add to cart:', error);
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Failed to add to cart' 
      };
    }
  };

  // Remove from cart
  const removeFromCart = async (cartId) => {
    // For mock tokens, just simulate success
    const token = localStorage.getItem('token');
    if (isMockToken(token)) {
      loadCart(user?.customer_id);
      return { success: true };
    }
    
    try {
      await cart.remove(cartId);
      loadCart(user?.customer_id);
      return { success: true };
    } catch (error) {
      console.error('Failed to remove from cart:', error);
      return { success: false, error: 'Failed to remove from cart' };
    }
  };

  // Update cart item
  const updateCartItem = async (cartId, quantity) => {
    // For mock tokens, just simulate success
    const token = localStorage.getItem('token');
    if (isMockToken(token)) {
      loadCart(user?.customer_id);
      return { success: true };
    }
    
    try {
      await cart.update(cartId, { quantity });
      loadCart(user?.customer_id);
      return { success: true };
    } catch (error) {
      console.error('Failed to update cart:', error);
      return { success: false, error: 'Failed to update cart' };
    }
  };

  // Clear cart
  const clearCart = async () => {
    if (!user) return;
    
    // For mock tokens, just simulate success
    const token = localStorage.getItem('token');
    if (isMockToken(token)) {
      setCartItems([]);
      return { success: true };
    }
    
    try {
      await cart.clear(user.customer_id);
      setCartItems([]);
      return { success: true };
    } catch (error) {
      console.error('Failed to clear cart:', error);
      return { success: false, error: 'Failed to clear cart' };
    }
  };

  // Add to wishlist
  const addToWishlist = async (articleId) => {
    if (!user) {
      return { success: false, error: 'Please login to add items to wishlist' };
    }
    
    // For mock tokens, just simulate success
    const token = localStorage.getItem('token');
    if (isMockToken(token)) {
      return { success: true };
    }
    
    try {
      // Use the simpler /wishlist/add endpoint that uses authentication
      await wishlist.add(articleId);
      
      // Reload wishlist
      await loadWishlist(user.customer_id);
      return { success: true };
    } catch (error) {
      console.error('Failed to add to wishlist:', error);
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Failed to add to wishlist' 
      };
    }
  };

  // Remove from wishlist
  const removeFromWishlist = async (wishlistId) => {
    // For mock tokens, just simulate success
    const token = localStorage.getItem('token');
    if (isMockToken(token)) {
      loadWishlist(user?.customer_id);
      return { success: true };
    }
    
    try {
      await wishlist.remove(wishlistId);
      loadWishlist(user?.customer_id);
      return { success: true };
    } catch (error) {
      console.error('Failed to remove from wishlist:', error);
      return { success: false, error: 'Failed to remove from wishlist' };
    }
  };

  // Move wishlist to cart
  const moveWishlistToCart = async (wishlistId) => {
    // For mock tokens, just simulate success
    const token = localStorage.getItem('token');
    if (isMockToken(token)) {
      loadCart(user?.customer_id);
      loadWishlist(user?.customer_id);
      return { success: true };
    }
    
    try {
      await wishlist.moveToCart(wishlistId);
      loadCart(user?.customer_id);
      loadWishlist(user?.customer_id);
      return { success: true };
    } catch (error) {
      console.error('Failed to move to cart:', error);
      return { success: false, error: 'Failed to move to cart' };
    }
  };

  const value = {
    // State
    user,
    admin,
    cartItems,
    wishlistItems,
    loading,
    isAuthenticated: !!user,
    isAdmin: !!admin,
    
    // Auth methods
    login,
    loginAdmin,
    signup,
    logout,
    logoutAdmin,
    
    // Cart methods
    addToCart,
    removeFromCart,
    updateCartItem,
    clearCart,
    loadCart,
    
    // Wishlist methods
    addToWishlist,
    removeFromWishlist,
    moveWishlistToCart,
    loadWishlist,
  };

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
};