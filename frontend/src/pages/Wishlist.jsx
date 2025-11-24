import { useEffect, useState } from "react";
import ProductCard from "../components/ProductCard";
import { api } from "../api/api";

export default function Wishlist() {
  const [wishlist, setWishlist] = useState([]);

  useEffect(() => {
    // Fetch wishlist items from backend (could be Events with type 'wishlist')
    api.get("/events?event_type=wishlist&limit=50")
      .then(res => setWishlist(res.data))
      .catch(err => console.error(err));
  }, []);

  return (
    <div className="app-container py-6 md:py-8">
      <h1 className="text-3xl md:text-4xl font-bold mb-8 text-gray-900">Wishlist</h1>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {wishlist.length ? wishlist.map(item => (
          <ProductCard key={item.article_id} product={item} />
        )) : (
          <div className="col-span-full text-center py-12">
            <p className="text-gray-600 text-lg">Your wishlist is empty.</p>
          </div>
        )}
      </div>
    </div>
  );
}
