import { useEffect, useMemo, useState } from "react";
import { fetchAllReviews } from "../../api/api";

export default function ReviewsView() {
  const [reviews, setReviews] = useState([]);
  const [ratingFilter, setRatingFilter] = useState("all");
  const [search, setSearch] = useState("");

  useEffect(() => {
    fetchAllReviews(200, 0).then(res => setReviews(res.data || []));
  }, []);

  const filtered = useMemo(() => {
    return reviews.filter(review => {
      const matchesRating = ratingFilter === "all" || review.rating === Number(ratingFilter);
      const matchesSearch =
        !search ||
        (review.review_text || "").toLowerCase().includes(search.toLowerCase()) ||
        (review.article_id || "").includes(search);
      return matchesRating && matchesSearch;
    });
  }, [reviews, ratingFilter, search]);

  const handleDelete = reviewId => {
    alert("Review deletion endpoint is not implemented in the backend yet.");
  };

  return (
    <div className="space-y-4">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-semibold text-gray-900">Reviews</h2>
          <p className="text-gray-500 text-sm">Monitor product feedback and ratings.</p>
        </div>
        <div className="flex flex-col md:flex-row gap-3">
          <input
            type="text"
            placeholder="Search reviews"
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="px-3 py-2 border rounded-lg"
          />
          <select
            value={ratingFilter}
            onChange={e => setRatingFilter(e.target.value)}
            className="px-3 py-2 border rounded-lg"
          >
            <option value="all">All ratings</option>
            {[5, 4, 3, 2, 1].map(rating => (
              <option key={rating} value={rating}>
                {rating} stars
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="bg-white border rounded-xl overflow-hidden shadow-sm">
        <table className="min-w-full text-sm">
          <thead className="bg-gray-50 text-left text-gray-600 uppercase text-xs tracking-wide">
            <tr>
              <th className="px-4 py-3">Review ID</th>
              <th className="px-4 py-3">Customer</th>
              <th className="px-4 py-3">Article</th>
              <th className="px-4 py-3">Rating</th>
              <th className="px-4 py-3">Review</th>
              <th className="px-4 py-3 text-right">Actions</th>
            </tr>
          </thead>
          <tbody>
            {filtered.length ? (
              filtered.map(review => (
                <tr key={review.review_id} className="border-t">
                  <td className="px-4 py-3 font-mono text-xs text-gray-500">{review.review_id}</td>
                  <td className="px-4 py-3 text-gray-800">{review.customer_id}</td>
                  <td className="px-4 py-3 text-gray-600">{review.article_id}</td>
                  <td className="px-4 py-3 font-semibold text-gray-900">{review.rating ?? "—"}</td>
                  <td className="px-4 py-3 text-gray-600">{review.review_text || "—"}</td>
                  <td className="px-4 py-3 text-right">
                    <button
                      onClick={() => handleDelete(review.review_id)}
                      className="text-red-600 hover:underline text-sm"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="6" className="px-4 py-8 text-center text-gray-500">
                  No reviews match the selected filters.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      <p className="text-xs text-gray-500">
        * Review deletion endpoint is not yet implemented in the backend. Button shown for UX completeness.
      </p>
    </div>
  );
}

