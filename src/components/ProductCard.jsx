import { Link } from "react-router-dom";
import SettingsIcon from "./SettingsIcon"; // Adjust path as needed

export default function ProductCard({ product, isAdmin }) {
  console.log("ProductCard received:", product); // Debug

  // Handle demo products that might not have all fields
  const productId = product.article_id || product.id || product.productId || '108775015';
  const productName = product.prod_name || product.name || 'Product Name';
  const productPrice = product.price || product.Price || 0;
  const productImage = product.image || product.Image || 'placeholder.jpg';

  return (
    <div className="group">
      <Link to={`/products/${productId}`} className="block">
        <div className="bg-white border border-gray-100 rounded-xl p-4 transition-all duration-300 group-hover:shadow-lg">

          {/* Image box */}
          <div className="w-full aspect-[4/3] bg-gray-50 rounded-lg overflow-hidden flex items-center justify-center relative">
            <img
              src={`/products/${productImage}`}
              alt={productName}
              className="absolute inset-0 w-full h-full object-contain transition-transform duration-300 group-hover:scale-110"
              onError={(e) => {
                console.log("Failed to load image:", `/products/${productImage}`);
                e.target.src = "/products/placeholder.jpg";
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
      
      {/* Buy Now Button */}
      <div className="mt-2">
        <button 
          onClick={(e) => {
            e.stopPropagation();
            // Add to cart and navigate to cart page
            const cart = JSON.parse(localStorage.getItem('cart') || '[]');
            
            // Handle demo products that might not have all fields
            const cartItem = {
              article_id: productId,
              prod_name: productName,
              price: productPrice,
              image: productImage,
              quantity: 1
            };
            
            const existingItem = cart.find(item => item.article_id === productId);
            
            if (existingItem) {
              existingItem.quantity += 1;
            } else {
              cart.push(cartItem);
            }
            
            localStorage.setItem('cart', JSON.stringify(cart));
            window.location.href = '/cart'; // Navigate to cart page
          }}
          className="w-full bg-green-600 text-white py-2 rounded-lg text-sm font-medium hover:bg-green-700 transition-colors"
        >
          Buy Now
        </button>
      </div>
    </div>
  );
}