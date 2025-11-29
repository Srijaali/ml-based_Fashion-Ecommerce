import { Link, useNavigate } from "react-router-dom";
import { useApp } from "../context/AppContext";
import SettingsIcon from "./SettingsIcon";
import { useState } from "react";

export default function ProductCard({ product, isAdmin }) {
  const navigate = useNavigate();
  const { addToCart, addToWishlist, isAuthenticated } = useApp();
  const [isAddingToCart, setIsAddingToCart] = useState(false);
  const [isAddingToWishlist, setIsAddingToWishlist] = useState(false);

  // Handle demo products that might not have all fields
  const productId = product.article_id || product.id || product.productId || '108775015';
  const productName = product.prod_name || product.name || 'Product Name';
  const productPrice = product.price || product.Price || 0;
  const productImage = product.image_path || product.Image || 'placeholder.jpg';



  return (
    <div className="group">
      <Link to={`/products/${productId}`} className="block">
        <div className="bg-white border border-gray-100 rounded-xl p-4 transition-all duration-300 group-hover:shadow-lg">

          {/* Image box */}
          <div className="w-full aspect-[4/3] bg-gray-50 rounded-lg overflow-hidden flex items-center justify-center relative">
            <img
              src={`/images/${productImage}`}
              alt={productName}
              className="absolute inset-0 w-full h-full object-contain transition-transform duration-300 group-hover:scale-110"
              onError={(e) => {
                console.log("Failed to load image:", `/images/${productImage}`);
                e.target.src = "/images/placeholder.jpg";
              }}
            />
          </div>

          {/* Product text */}
          <div className="mt-4 text-center">
            <h4 className="text-sm font-medium text-gray-800">
              {productName}
            </h4>

            <p className="text-gray-500 text-sm mt-1">
              ${productPrice.toFixed(2)}
            </p>
          </div>

          {isAdmin && (
            <button className="settings-btn">
              <SettingsIcon />
            </button>
          )}
        </div>
      </Link>
      
      {/* Action Buttons */}
      <div className="mt-2 flex gap-2">
        {/* Add to Cart */}
        <button 
          onClick={async (e) => {
            e.stopPropagation();
            e.preventDefault();
            
            if (!isAuthenticated) {
              alert('Please login to add items to cart');
              navigate('/login');
              return;
            }
            
            setIsAddingToCart(true);
            const result = await addToCart(productId, 1);
            setIsAddingToCart(false);
            
            if (result.success) {
              alert('Added to cart!');
            } else {
              alert(result.error || 'Failed to add to cart');
            }
          }}
          disabled={isAddingToCart}
          className="flex-1 bg-blue-600 text-white py-2 rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isAddingToCart ? 'Adding...' : 'Add to Cart'}
        </button>
        
        {/* Add to Wishlist */}
        <button 
          onClick={async (e) => {
            e.stopPropagation();
            e.preventDefault();
            
            if (!isAuthenticated) {
              alert('Please login to add items to wishlist');
              navigate('/login');
              return;
            }
            
            setIsAddingToWishlist(true);
            const result = await addToWishlist(productId);
            setIsAddingToWishlist(false);
            
            if (result.success) {
              alert('Added to wishlist!');
            } else {
              alert(result.error || 'Failed to add to wishlist');
            }
          }}
          disabled={isAddingToWishlist}
          className="px-3 bg-gray-200 text-gray-700 py-2 rounded-lg text-sm font-medium hover:bg-gray-300 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          title="Add to Wishlist"
        >
          {isAddingToWishlist ? '...' : '♡'}
        </button>
        
        {/* Buy Now */}
        <button 
          onClick={async (e) => {
            e.stopPropagation();
            e.preventDefault();
            
            if (!isAuthenticated) {
              alert('Please login to purchase');
              navigate('/login');
              return;
            }
            
            setIsAddingToCart(true);
            const result = await addToCart(productId, 1);
            setIsAddingToCart(false);
            
            if (result.success) {
              navigate('/cart');
            } else {
              alert(result.error || 'Failed to add to cart');
            }
          }}
          disabled={isAddingToCart}
          className="flex-1 bg-green-600 text-white py-2 rounded-lg text-sm font-medium hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isAddingToCart ? 'Adding...' : 'Buy Now'}
        </button>
      </div>
    </div>
  );
}