// components/ProductCard.jsx

import { Link, useNavigate } from "react-router-dom";
import { useApp } from "../context/AppContext";
import SettingsIcon from "./SettingsIcon";
import { useState } from "react";
import { API_URL } from "../api/api";

export default function ProductCard({ product, isAdmin }) {
  const navigate = useNavigate();
  const { addToCart, addToWishlist, isAuthenticated } = useApp();
  const [isAddingToCart, setIsAddingToCart] = useState(false);
  const [isAddingToWishlist, setIsAddingToWishlist] = useState(false);

  const productId =
    product.article_id ||
    product.id ||
    product.productId ||
    "108775015";

  const productName =
    product.prod_name ||
    product.name ||
    "Product Name";

  const imagePath =
    product.image_path
      ? `${API_URL}/images/${product.image_path}`
      : `${API_URL}/images/placeholder.jpg`;

  return (
    <div className="product-card border p-4 rounded-lg shadow-md bg-white">
      <Link to={`/products/${productId}`} className="block relative">

        {isAdmin && (
          <button className="absolute top-2 right-2 z-20 bg-white p-2 rounded-full shadow">
            <SettingsIcon />
          </button>
        )}

        {/* Product Image */}
        <div className="w-full h-64 overflow-hidden rounded-lg bg-gray-100">
          <img
            src={imagePath}
            alt={productName}
            className="w-full h-full object-cover"
            onError={(e) => {
              e.target.src = `${API_URL}/images/placeholder.jpg`;
            }}
          />
        </div>

        {/* Product Name + Price */}
        <div className="mt-2">
          <h2 className="text-lg font-semibold">{productName}</h2>
          <p className="text-gray-700">Rs {product.price}</p>
        </div>
      </Link>

      {/* Action Buttons */}
      <div className="mt-3 flex gap-2">

        {/* Add to Cart */}
        <button
          onClick={async (e) => {
            e.preventDefault();
            if (!isAuthenticated) {
              navigate("/login");
              return;
            }
            setIsAddingToCart(true);
            const result = await addToCart(productId, 1);
            setIsAddingToCart(false);
            alert(result.success ? "Added to cart!" : result.error);
          }}
          disabled={isAddingToCart}
          className="flex-1 bg-blue-600 text-white py-2 rounded-lg"
        >
          {isAddingToCart ? "Adding..." : "Add to Cart"}
        </button>

        {/* Add to Wishlist */}
        <button
          onClick={async (e) => {
            e.preventDefault();
            if (!isAuthenticated) {
              navigate("/login");
              return;
            }
            setIsAddingToWishlist(true);
            const result = await addToWishlist(productId);
            setIsAddingToWishlist(false);
            alert(result.success ? "Added to wishlist!" : result.error);
          }}
          disabled={isAddingToWishlist}
          className="px-3 bg-gray-200 text-gray-700 py-2 rounded-lg"
        >
          {isAddingToWishlist ? "…" : "♡"}
        </button>

        {/* Buy Now */}
        <button
          onClick={async (e) => {
            e.preventDefault();
            if (!isAuthenticated) {
              navigate("/login");
              return;
            }
            setIsAddingToCart(true);
            const result = await addToCart(productId, 1);
            setIsAddingToCart(false);
            if (result.success) navigate("/cart");
            else alert(result.error);
          }}
          className="flex-1 bg-green-600 text-white py-2 rounded-lg"
        >
          Buy Now
        </button>
      </div>
    </div>
  );
}
