import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import CartItem from "../components/CartItem";
import { api } from "../api/api";

export default function Cart() {
  const [cartItems, setCartItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    // First check localStorage for items added via "Buy Now"
    const localCart = JSON.parse(localStorage.getItem('cart') || '[]');
    
    if (localCart.length > 0) {
      // Convert local cart items to the format expected by CartItem component
      const formattedItems = localCart.map((item, index) => ({
        order_item_id: `local_${index}_${item.article_id}`,
        article_id: item.article_id,
        prod_name: item.prod_name,
        unit_price: item.price,
        quantity: item.quantity,
        image: item.image
      }));
      
      setCartItems(formattedItems);
      setLoading(false);
    } else {
      // Fetch cart items for current user from API
      setLoading(true);
      api.get("/order_items?limit=50")
        .then(res => {
          setCartItems(res.data || []);
          setLoading(false);
        })
        .catch(err => {
          console.error(err);
          setLoading(false);
        });
    }
  }, []);

  const removeItem = (id) => {
    // Check if it's a local item
    if (id.startsWith('local_')) {
      const localCart = JSON.parse(localStorage.getItem('cart') || '[]');
      const itemIndex = localCart.findIndex((_, index) => `local_${index}_${localCart[index].article_id}` === id);
      
      if (itemIndex !== -1) {
        localCart.splice(itemIndex, 1);
        localStorage.setItem('cart', JSON.stringify(localCart));
        setCartItems(cartItems.filter(item => item.order_item_id !== id));
      }
    } else {
      api.delete(`/order_items/${id}`)
        .then(() => setCartItems(cartItems.filter(item => item.order_item_id !== id)))
        .catch(err => console.error(err));
    }
  };

  const updateQuantity = (id, newQuantity) => {
    if (newQuantity < 1) {
      removeItem(id);
      return;
    }
    
    // Check if it's a local item
    if (id.startsWith('local_')) {
      const localCart = JSON.parse(localStorage.getItem('cart') || '[]');
      const itemIndex = localCart.findIndex((_, index) => `local_${index}_${localCart[index].article_id}` === id);
      
      if (itemIndex !== -1) {
        localCart[itemIndex].quantity = newQuantity;
        localStorage.setItem('cart', JSON.stringify(localCart));
        setCartItems(cartItems.map(item => 
          item.order_item_id === id ? { ...item, quantity: newQuantity } : item
        ));
      }
    } else {
      api.put(`/order_items/${id}`, { quantity: newQuantity })
        .then(() => {
          setCartItems(cartItems.map(item => 
            item.order_item_id === id ? { ...item, quantity: newQuantity } : item
          ));
        })
        .catch(err => console.error(err));
    }
  };

  const subtotal = cartItems.reduce((sum, item) => sum + (item.unit_price || 0) * item.quantity, 0);
  const tax = subtotal * 0.1; // 10% tax
  const shipping = subtotal > 100 ? 0 : 10; // Free shipping over $100
  const total = subtotal + tax + shipping;

  const handleCheckout = () => {
    if (cartItems.length > 0) {
      // If we have local cart items, we might want to save them to the database
      // For now, we'll just navigate to checkout
      navigate('/checkout');
    }
  };

  if (loading) {
    return (
      <div className="app-container py-12 min-h-[60vh] flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mb-4"></div>
          <p className="text-gray-600">Loading your cart...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="app-container py-8 md:py-12 min-h-[60vh]">
      <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-8">Shopping Cart</h1>

      {cartItems.length === 0 ? (
        <div className="text-center py-16">
          <div className="max-w-md mx-auto">
            <svg
              className="mx-auto h-24 w-24 text-gray-300 mb-6"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.5}
                d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"
              />
            </svg>
            <h2 className="text-2xl font-semibold text-gray-900 mb-2">Your cart is empty</h2>
            <p className="text-gray-600 mb-8">Looks like you haven't added anything to your cart yet.</p>
            <button
              onClick={() => navigate('/products')}
              className="btn-soft px-6 py-3 text-base"
            >
              Continue Shopping
            </button>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 md:gap-8">
          {/* Cart Items */}
          <div className="md:col-span-2 space-y-4">
            {cartItems.map(item => (
              <CartItem
                key={item.order_item_id}
                item={item}
                onRemove={removeItem}
                onUpdateQuantity={updateQuantity}
              />
            ))}
          </div>

          {/* Order Summary */}
          <div className="md:col-span-1">
            <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6 sticky top-4">
              <h2 className="text-xl font-semibold text-gray-900 mb-6">Order Summary</h2>
              
              <div className="space-y-4 mb-6">
                <div className="flex justify-between text-gray-600">
                  <span>Subtotal</span>
                  <span>${subtotal.toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-gray-600">
                  <span>Tax</span>
                  <span>${tax.toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-gray-600">
                  <span>Shipping</span>
                  <span className={shipping === 0 ? "text-green-600" : ""}>
                    {shipping === 0 ? "Free" : `$${shipping.toFixed(2)}`}
                  </span>
                </div>
                {subtotal < 100 && (
                  <p className="text-sm text-gray-500">
                    Add ${(100 - subtotal).toFixed(2)} more for free shipping!
                  </p>
                )}
                <div className="border-t border-gray-200 pt-4">
                  <div className="flex justify-between text-lg font-semibold text-gray-900">
                    <span>Total</span>
                    <span>${total.toFixed(2)}</span>
                  </div>
                </div>
              </div>

              <button
                onClick={handleCheckout}
                className="w-full bg-gray-900 text-white py-3 px-6 rounded-lg font-medium hover:bg-gray-800 transition-colors duration-200 mb-4"
              >
                Proceed to Checkout
              </button>
              
              <button
                onClick={() => navigate('/products')}
                className="w-full bg-gray-100 text-gray-900 py-3 px-6 rounded-lg font-medium hover:bg-gray-200 transition-colors duration-200"
              >
                Continue Shopping
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}