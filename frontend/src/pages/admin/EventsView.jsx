import { useEffect, useMemo, useState } from "react";
import { fetchEvents } from "../../api/api";

const typeColors = {
  view: "bg-gray-100 text-gray-700",
  click: "bg-blue-50 text-blue-700",
  wishlist: "bg-pink-50 text-pink-700",
  add_to_cart: "bg-yellow-50 text-yellow-700",
  purchase: "bg-green-50 text-green-700"
};

export default function EventsView() {
  const [events, setEvents] = useState([]);
  const [typeFilter, setTypeFilter] = useState("all");

  useEffect(() => {
    fetchEvents(200, 0).then(res => setEvents(res.data || []));
  }, []);

  const filtered = useMemo(
    () => events.filter(event => typeFilter === "all" || event.event_type === typeFilter),
    [events, typeFilter]
  );

  const funnel = useMemo(() => {
    const counts = { view: 0, click: 0, add_to_cart: 0, purchase: 0 };
    events.forEach(event => {
      if (counts[event.event_type] !== undefined) counts[event.event_type] += 1;
    });
    return counts;
  }, [events]);

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-semibold text-gray-900">Event Stream</h2>
          <p className="text-gray-500 text-sm">Monitor the customer journey across the funnel.</p>
        </div>
        <select
          value={typeFilter}
          onChange={e => setTypeFilter(e.target.value)}
          className="px-3 py-2 border rounded-lg w-full md:w-48"
        >
          <option value="all">All events</option>
          <option value="view">View</option>
          <option value="click">Click</option>
          <option value="wishlist">Wishlist</option>
          <option value="add_to_cart">Add to cart</option>
          <option value="purchase">Purchase</option>
        </select>
      </div>

      <div className="bg-white border rounded-xl p-6 shadow-sm">
        <h3 className="font-semibold text-gray-900 mb-4">Funnel Snapshot</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {Object.entries(funnel).map(([stage, count]) => (
            <div key={stage} className="bg-gray-50 rounded-lg p-4 text-center">
              <p className="text-sm uppercase text-gray-500">{stage.replace(/_/g, " ")}</p>
              <p className="text-2xl font-semibold text-gray-900">{count}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="bg-white border rounded-xl overflow-hidden shadow-sm">
        <table className="min-w-full text-sm">
          <thead className="bg-gray-50 text-left text-gray-600 uppercase text-xs tracking-wide">
            <tr>
              <th className="px-4 py-3">Event ID</th>
              <th className="px-4 py-3">Customer</th>
              <th className="px-4 py-3">Article</th>
              <th className="px-4 py-3">Type</th>
              <th className="px-4 py-3">Timestamp</th>
            </tr>
          </thead>
          <tbody>
            {filtered.length ? (
              filtered.map(event => (
                <tr key={event.event_id} className="border-t">
                  <td className="px-4 py-3 font-mono text-xs text-gray-500">{event.event_id}</td>
                  <td className="px-4 py-3 text-gray-800">{event.customer_id || "—"}</td>
                  <td className="px-4 py-3 text-gray-600">{event.article_id || "—"}</td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-1 text-xs rounded-full font-medium ${typeColors[event.event_type] || "bg-gray-100 text-gray-700"}`}>
                      {event.event_type}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-gray-600">
                    {event.created_at ? new Date(event.created_at).toLocaleString() : "—"}
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="5" className="px-4 py-8 text-center text-gray-500">
                  No events for the selected filter.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

