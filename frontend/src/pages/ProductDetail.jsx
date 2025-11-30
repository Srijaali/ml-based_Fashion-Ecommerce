import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { articles, reviews as reviewsAPI } from "../api/api";
import { useApp } from "../context/AppContext";
import ReviewItem from "../components/ReviewItem";
import ProductCard from "../components/ProductCard";

export default function ProductDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user, addToCart, addToWishlist, isAuthenticated } = useApp();
  const [product, setProduct] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [relatedProducts, setRelatedProducts] = useState([]);
  const [similarProducts, setSimilarProducts] = useState([]);
  const [newReview, setNewReview] = useState({
    rating: 5,
    review_text: ""
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [isAddingToCart, setIsAddingToCart] = useState(false);
  const [isAddingToWishlist, setIsAddingToWishlist] = useState(false);
  const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  useEffect(() => {
    // Reset states when ID changes
    setProduct(null);
    setReviews([]);
    setRelatedProducts([]);
    setSimilarProducts([]);
    setError(null);

    // Fetch product data
    const fetchProductData = async () => {
      try {
        console.log("Fetching product with ID:", id);

        // Fetch product
        const productRes = await articles.getById(id);
        console.log("Product response:", productRes);
        setProduct(productRes.data);

        // Fetch reviews
        try {
          const reviewsRes = await reviewsAPI.getByArticle(id);
          console.log("Reviews response:", reviewsRes);
          setReviews(reviewsRes.data || []);
        } catch (err) {
          console.log("No reviews found");
          setReviews([]);
        }

        // Fetch related/similar products (just get some other products)
        const allProductsRes = await articles.getAll(0, 8);
        const allProducts = allProductsRes.data || [];
        setRelatedProducts(allProducts.slice(0, 4));
        setSimilarProducts(allProducts.slice(4, 8));

      } catch (err) {
        console.error("Error fetching product data:", err);
        setError("Failed to load product. Please try again.");
      }
    };

    if (id) {
      fetchProductData();
    }
  }, [id]);

  const handleReviewSubmit = async (e) => {
    e.preventDefault();

    if (!isAuthenticated) {
      alert('Please login to write a review');
      navigate('/login');
      return;
    }

    if (!newReview.review_text) return;

    setIsSubmitting(true);
    try {
      const reviewData = {
        customer_id: user.customer_id,
        article_id: id,
        rating: newReview.rating,
        review_text: newReview.review_text
      };

      await reviewsAPI.create(reviewData);

      // Reload reviews
      const reviewsRes = await reviewsAPI.getByArticle(id);
      setReviews(reviewsRes.data || []);

      // Reset form
      setNewReview({
        rating: 5,
        review_text: ""
      });

      alert('Review submitted successfully!');
    } catch (err) {
      console.error("Failed to submit review:", err);
      alert('Failed to submit review. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (error) {
    return (
      <div className="app-container py-12">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
          <h2 className="text-xl font-bold text-red-800 mb-2">Error</h2>
          <p className="text-red-600">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="mt-4 bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!product && !error) {
    return (
      <div className="app-container py-12">
        <div className="flex justify-center items-center">
          <div className="text-center">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 mb-4"></div>
            <p className="text-gray-600">Loading product details...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="app-container py-6 md:py-8">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
        {/* Product Image */}
        <div className="w-full">
          <div className="w-full aspect-square max-h-[70vh] bg-gray-100 rounded-xl overflow-hidden flex items-center justify-center relative">
            <img
              src={`${API_URL}/images/${product.image_path || 'placeholder.jpg'}`}
              alt={product.prod_name}
              className="absolute inset-0 w-full h-full object-contain"
              onError={(e) => {
                e.target.src = `${API_URL}/images/placeholder.jpg`;
              }}
            />
          </div>
        </div>

        {/* Product Details */}
        <div className="w-full">
          <h1 className="text-3xl md:text-4xl font-bold mb-4 text-gray-900">{product.prod_name}</h1>
          <p className="text-2xl font-semibold text-gray-900 mb-4">${product.price}</p>
          <p className="mb-2 text-gray-600">Stock: <span className="font-medium">{product.stock}</span></p>
          <p className="mb-2 text-gray-600">Category: <span className="font-medium">{product.product_group_name}</span></p>
          <p className="mb-2 text-gray-600">Color: <span className="font-medium">{product.colour_group_name}</span></p>
          <p className="mb-6 text-gray-600">Type: <span className="font-medium">{product.product_type_name}</span></p>
          <div className="flex flex-col sm:flex-row gap-4 mb-8">
            <button
              onClick={async () => {
                if (!isAuthenticated) {
                  alert('Please login to add items to cart');
                  navigate('/login');
                  return;
                }

                setIsAddingToCart(true);
                const result = await addToCart(product.article_id, 1);
                setIsAddingToCart(false);

                if (result.success) {
                  alert('Added to cart!');
                } else {
                  alert(result.error || 'Failed to add to cart');
                }
              }}
              disabled={isAddingToCart}
              className="bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isAddingToCart ? 'Adding to Cart...' : 'Add to Cart'}
            </button>
            <button
              onClick={async () => {
                if (!isAuthenticated) {
                  alert('Please login to add items to wishlist');
                  navigate('/login');
                  return;
                }

                setIsAddingToWishlist(true);
                const result = await addToWishlist(product.article_id);
                setIsAddingToWishlist(false);

                if (result.success) {
                  alert('Added to wishlist!');
                } else {
                  alert(result.error || 'Failed to add to wishlist');
                }
              }}
              disabled={isAddingToWishlist}
              className="bg-gray-200 text-black px-6 py-3 rounded-lg font-medium hover:bg-gray-300 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isAddingToWishlist ? 'Adding to Wishlist...' : 'Add to Wishlist'}
            </button>
            <button
              onClick={async () => {
                if (!isAuthenticated) {
                  alert('Please login to purchase');
                  navigate('/login');
                  return;
                }

                setIsAddingToCart(true);
                const result = await addToCart(product.article_id, 1);
                setIsAddingToCart(false);

                if (result.success) {
                  navigate('/cart');
                } else {
                  alert(result.error || 'Failed to add to cart');
                }
              }}
              disabled={isAddingToCart}
              className="bg-green-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isAddingToCart ? 'Adding to Cart...' : 'Buy Now'}
            </button>
          </div>

          {/* Product Description */}
          <div className="border-t border-gray-200 pt-6">
            <h3 className="text-lg font-semibold mb-2">Description</h3>
            <p className="text-gray-600">{product.detail_desc || "No description available for this product."}</p>
          </div>
        </div>
      </div>

      {/* Reviews Section */}
      <div className="mt-8">
        <h2 className="text-2xl font-bold mb-4 text-gray-900">Reviews</h2>

        {/* Review Submission Form */}
        <div className="border rounded-lg p-6 mb-8">
          <h3 className="text-xl font-semibold mb-4">Write a Review</h3>
          <form onSubmit={handleReviewSubmit}>


            <div className="mb-4">
              <label htmlFor="rating" className="block text-sm font-medium text-gray-700 mb-1">
                Rating
              </label>
              <select
                id="rating"
                value={newReview.rating}
                onChange={(e) => setNewReview({ ...newReview, rating: parseInt(e.target.value) })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {[1, 2, 3, 4, 5].map(num => (
                  <option key={num} value={num}>{num} Star{num > 1 ? 's' : ''}</option>
                ))}
              </select>
            </div>

            <div className="mb-4">
              <label htmlFor="review_text" className="block text-sm font-medium text-gray-700 mb-1">
                Review
              </label>
              <textarea
                id="review_text"
                value={newReview.review_text}
                onChange={(e) => setNewReview({ ...newReview, review_text: e.target.value })}
                rows={4}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
                placeholder="Share your experience with this product..."
              ></textarea>
            </div>

            <button
              type="submit"
              disabled={isSubmitting}
              className="bg-blue-600 text-white px-6 py-2 rounded-md font-medium hover:bg-blue-700 transition-colors disabled:opacity-50"
            >
              {isSubmitting ? "Submitting..." : "Submit Review"}
            </button>
          </form>
        </div>

        {/* Existing Reviews */}
        {reviews.length ? reviews.map(r => <ReviewItem key={r.review_id} review={r} />) : <p className="text-gray-600">No reviews yet. Be the first to review this product!</p>}
      </div>

      {/* You May Also Like Section */}
      {relatedProducts.length > 0 && (
        <div className="mt-12">
          <h2 className="text-2xl font-bold mb-6 text-gray-900">You May Also Like</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {relatedProducts.map(product => (
              <ProductCard key={product.article_id} product={product} />
            ))}
          </div>
        </div>
      )}

      {/* Similar Products Section */}
      {similarProducts.length > 0 && (
        <div className="mt-12">
          <h2 className="text-2xl font-bold mb-6 text-gray-900">Similar Products</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {similarProducts.map(product => (
              <ProductCard key={product.article_id} product={product} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}