import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { fetchProductById, fetchReviewsByProduct, fetchRelatedProducts, fetchSimilarProducts, postReview } from "../api/api";
import ReviewItem from "../components/ReviewItem";
import ProductCard from "../components/ProductCard";

export default function ProductDetail() {
  const { id } = useParams();
  const [product, setProduct] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [relatedProducts, setRelatedProducts] = useState([]);
  const [similarProducts, setSimilarProducts] = useState([]);
  const [newReview, setNewReview] = useState({
    customer_id: "",
    rating: 5,
    review_text: ""
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);

  // Demo product data
  const demoProducts = {
    "108775015": {
      article_id: "108775015",
      prod_name: "Black Minimal Jacket",
      product_code: 123456,
      product_type_name: "Jacket",
      product_group_name: "Outerwear",
      graphical_appearance_name: "Solid",
      colour_group_name: "Black",
      department_name: "Menswear",
      index_name: "Mens Outerwear",
      index_group_name: "Menswear",
      section_name: "Mens Jackets",
      garment_group_name: "Jacket",
      detail_desc: "A sleek black jacket with minimalist design. Perfect for any occasion.",
      price: 129.99,
      stock: 15,
      category_id: 1,
      image: "product1.png"
    },
    "108775016": {
      article_id: "108775016",
      prod_name: "Grey Urban Hoodie",
      product_code: 123457,
      product_type_name: "Hoodie",
      product_group_name: "Knitwear",
      graphical_appearance_name: "Solid",
      colour_group_name: "Grey",
      department_name: "Menswear",
      index_name: "Mens Knitwear",
      index_group_name: "Menswear",
      section_name: "Mens Hoodies",
      garment_group_name: "Hoodie",
      detail_desc: "Comfortable grey hoodie for everyday wear. Soft fabric and perfect fit.",
      price: 79.99,
      stock: 22,
      category_id: 2,
      image: "product2.png"
    },
    "108775017": {
      article_id: "108775017",
      prod_name: "Olive Overshirt",
      product_code: 123458,
      product_type_name: "Shirt",
      product_group_name: "Shirts",
      graphical_appearance_name: "Solid",
      colour_group_name: "Green",
      department_name: "Womenswear",
      index_name: "Womens Shirts",
      index_group_name: "Womenswear",
      section_name: "Womens Tops",
      garment_group_name: "Shirt",
      detail_desc: "Stylish olive overshirt for women. Versatile piece that goes with everything.",
      price: 89.99,
      stock: 18,
      category_id: 3,
      image: "product3.png"
    },
    "108775018": {
      article_id: "108775018",
      prod_name: "Classic Denim Jacket",
      product_code: 123459,
      product_type_name: "Jacket",
      product_group_name: "Jeans",
      graphical_appearance_name: "Denim",
      colour_group_name: "Blue",
      department_name: "Womenswear",
      index_name: "Womens Outerwear",
      index_group_name: "Womenswear",
      section_name: "Womens Jackets",
      garment_group_name: "Jacket",
      detail_desc: "Timeless denim jacket that never goes out of style. Perfect layering piece.",
      price: 99.99,
      stock: 12,
      category_id: 1,
      image: "product4.png"
    }
  };

  // Demo reviews data
  const demoReviews = [
    {
      review_id: 1,
      customer_id: "Customer123",
      article_id: id,
      rating: 5,
      review_text: "Absolutely love this product! Great quality and fits perfectly.",
      created_at: "2023-05-15T10:30:00Z"
    },
    {
      review_id: 2,
      customer_id: "User456",
      article_id: id,
      rating: 4,
      review_text: "Very satisfied with my purchase. Would recommend to others.",
      created_at: "2023-06-22T14:15:00Z"
    },
    {
      review_id: 3,
      customer_id: "Buyer789",
      article_id: id,
      rating: 3,
      review_text: "Good product overall, but shipping took longer than expected.",
      created_at: "2023-07-10T09:45:00Z"
    }
  ];

  // Demo related products
  const demoRelatedProducts = [
    {
      article_id: "108775020",
      prod_name: "Black Slim Jeans",
      product_type_name: "Trousers",
      product_group_name: "Jeans",
      price: 69.99,
      stock: 25,
      image: "product5.png"
    },
    {
      article_id: "108775021",
      prod_name: "White Cotton Shirt",
      product_type_name: "Shirt",
      product_group_name: "Shirts",
      price: 49.99,
      stock: 30,
      image: "product6.png"
    },
    {
      article_id: "108775022",
      prod_name: "Brown Leather Belt",
      product_type_name: "Belts",
      product_group_name: "Accessories",
      price: 39.99,
      stock: 15,
      image: "product7.png"
    },
    {
      article_id: "108775023",
      prod_name: "Black Sneakers",
      product_type_name: "Shoes",
      product_group_name: "Footwear",
      price: 89.99,
      stock: 20,
      image: "product8.png"
    }
  ];

  // Demo similar products
  const demoSimilarProducts = [
    {
      article_id: "108775024",
      prod_name: "Navy Blue Jacket",
      product_type_name: "Jacket",
      product_group_name: "Outerwear",
      price: 119.99,
      stock: 18,
      image: "product1.png"
    },
    {
      article_id: "108775025",
      prod_name: "Charcoal Grey Jacket",
      product_type_name: "Jacket",
      product_group_name: "Outerwear",
      price: 124.99,
      stock: 12,
      image: "product4.png"
    },
    {
      article_id: "108775026",
      prod_name: "Burgundy Hoodie",
      product_type_name: "Hoodie",
      product_group_name: "Knitwear",
      price: 74.99,
      stock: 22,
      image: "product2.png"
    },
    {
      article_id: "108775027",
      prod_name: "Khaki Chinos",
      product_type_name: "Trousers",
      product_group_name: "Trousers",
      price: 59.99,
      stock: 28,
      image: "product3.png"
    }
  ];

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
        
        // Try to fetch from API first
        try {
          const productRes = await fetchProductById(id);
          console.log("Product response:", productRes);
          setProduct(productRes.data);
          
          // Fetch reviews
          const reviewsRes = await fetchReviewsByProduct(id);
          console.log("Reviews response:", reviewsRes);
          setReviews(reviewsRes.data || []);
          
          // Fetch related products
          const relatedRes = await fetchRelatedProducts(id);
          console.log("Related products response:", relatedRes);
          setRelatedProducts(relatedRes.data || []);
          
          // Fetch similar products
          const similarRes = await fetchSimilarProducts(id);
          console.log("Similar products response:", similarRes);
          setSimilarProducts(similarRes.data || []);
        } catch (apiError) {
          // If API fails, use demo data
          console.log("API failed, using demo data");
          const demoProduct = demoProducts[id] || Object.values(demoProducts)[0];
          setProduct(demoProduct);
          setReviews(demoReviews);
          setRelatedProducts(demoRelatedProducts);
          setSimilarProducts(demoSimilarProducts);
        }
      } catch (err) {
        console.error("Error fetching product data:", err);
        // Use demo data as fallback
        const demoProduct = demoProducts[id] || Object.values(demoProducts)[0];
        setProduct(demoProduct);
        setReviews(demoReviews);
        setRelatedProducts(demoRelatedProducts);
        setSimilarProducts(demoSimilarProducts);
      }
    };

    if (id) {
      fetchProductData();
    }
  }, [id]);

  const handleReviewSubmit = async (e) => {
    e.preventDefault();
    if (!newReview.customer_id || !newReview.review_text) return;
    
    setIsSubmitting(true);
    try {
      const reviewData = {
        ...newReview,
        article_id: id
      };
      
      await postReview(reviewData);
      
      // Add the new review to the list
      const newReviewWithId = {
        ...reviewData,
        review_id: Date.now(), // Simple ID for demo
        created_at: new Date().toISOString()
      };
      
      setReviews(prev => [...prev, newReviewWithId]);
      
      // Reset form
      setNewReview({
        customer_id: "",
        rating: 5,
        review_text: ""
      });
    } catch (err) {
      console.error("Failed to submit review:", err);
      // For demo purposes, still add the review even if API fails
      const newReviewWithId = {
        ...newReview,
        review_id: Date.now(),
        article_id: id,
        created_at: new Date().toISOString()
      };
      
      setReviews(prev => [...prev, newReviewWithId]);
      
      // Reset form
      setNewReview({
        customer_id: "",
        rating: 5,
        review_text: ""
      });
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
              src={`/products/${product.image || 'placeholder.jpg'}`}
              alt={product.prod_name}
              className="absolute inset-0 w-full h-full object-contain"
              onError={(e) => {
                e.target.src = '/products/placeholder.jpg';
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
            <button className="bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors">
              Add to Cart
            </button>
            <button className="bg-gray-200 text-black px-6 py-3 rounded-lg font-medium hover:bg-gray-300 transition-colors">
              Add to Wishlist
            </button>
            {/* Buy Now Button */}
            <button 
              onClick={() => {
                // Add to cart and navigate to cart page
                // In a real implementation, you would:
                // 1. Add product to cart (using localStorage or API)
                // 2. Navigate to cart page
                const cart = JSON.parse(localStorage.getItem('cart') || '[]');
                const existingItem = cart.find(item => item.article_id === product.article_id);
                
                if (existingItem) {
                  existingItem.quantity += 1;
                } else {
                  cart.push({
                    ...product,
                    quantity: 1
                  });
                }
                
                localStorage.setItem('cart', JSON.stringify(cart));
                window.location.href = '/cart'; // Navigate to cart page
              }}
              className="bg-green-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-green-700 transition-colors"
            >
              Buy Now
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
              <label htmlFor="customer_id" className="block text-sm font-medium text-gray-700 mb-1">
                Your Name
              </label>
              <input
                type="text"
                id="customer_id"
                value={newReview.customer_id}
                onChange={(e) => setNewReview({...newReview, customer_id: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
                placeholder="Enter your name"
              />
            </div>
            
            <div className="mb-4">
              <label htmlFor="rating" className="block text-sm font-medium text-gray-700 mb-1">
                Rating
              </label>
              <select
                id="rating"
                value={newReview.rating}
                onChange={(e) => setNewReview({...newReview, rating: parseInt(e.target.value)})}
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
                onChange={(e) => setNewReview({...newReview, review_text: e.target.value})}
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