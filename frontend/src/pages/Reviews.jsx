import { useEffect, useState } from "react";
import { fetchReviewsByProduct, postReview } from "../api/api";
import ReviewItem from "../components/ReviewItem";

export default function Reviews({ productId }) {
  const [reviews, setReviews] = useState([]);
  const [text, setText] = useState("");
  const [rating, setRating] = useState(5);

  useEffect(() => {
    fetchReviewsByProduct(productId).then(res => setReviews(res.data))
      .catch(err => console.error(err));
  }, [productId]);

  const handleSubmit = (e) => {
    e.preventDefault();
    postReview({ productId, customer_id: "C101", review_text: text, rating })
      .then(res => setReviews([...reviews, { review_id: Date.now(), customer_id: "C101", review_text: text, rating, created_at: new Date() }]))
      .catch(err => console.error(err));
    setText("");
  };

  return (
    <div className="p-6">
      <h2 className="text-xl font-bold mb-2">Reviews</h2>
      {reviews.length ? reviews.map(r => <ReviewItem key={r.review_id} review={r} />) : <p>No reviews yet.</p>}
      <form onSubmit={handleSubmit} className="mt-4 space-y-2">
        <textarea value={text} onChange={e=>setText(e.target.value)} placeholder="Write your review..." className="w-full border p-2 rounded"/>
        <select value={rating} onChange={e=>setRating(e.target.value)} className="border p-2 rounded">
          {[5,4,3,2,1].map(n => <option key={n} value={n}>{n}</option>)}
        </select>
        <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded">Submit Review</button>
      </form>
    </div>
  );
}
