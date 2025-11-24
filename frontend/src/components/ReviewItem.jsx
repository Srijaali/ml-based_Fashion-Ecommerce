export default function ReviewItem({ review }) {
  // Simple sentiment analysis based on rating
  const getSentiment = (rating) => {
    if (rating >= 4) return { label: "Positive", color: "bg-green-100 text-green-800" };
    if (rating >= 3) return { label: "Neutral", color: "bg-yellow-100 text-yellow-800" };
    return { label: "Negative", color: "bg-red-100 text-red-800" };
  };

  const sentiment = getSentiment(review.rating);

  return (
    <div className="border p-4 rounded mb-4">
      <div className="flex justify-between items-start">
        <div>
          <p className="font-bold">{review.customer_id}</p>
          <div className="flex items-center mt-1">
            <span className="mr-2">Rating: {review.rating} / 5</span>
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${sentiment.color}`}>
              {sentiment.label}
            </span>
          </div>
        </div>
        <p className="text-gray-500 text-sm">{new Date(review.created_at).toLocaleDateString()}</p>
      </div>
      <p className="mt-2">{review.review_text}</p>
    </div>
  );
}