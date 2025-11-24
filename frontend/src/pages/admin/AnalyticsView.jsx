import { useEffect, useState } from "react";
import { fetchOrders, fetchProducts } from "../../api/api";

export default function AnalyticsView() {
  const [orders, setOrders] = useState([]);
  const [products, setProducts] = useState([]);

  useEffect(() => {
    fetchOrders(500, 0).then(res => setOrders(res.data || []));
    fetchProducts(200, 0).then(res => setProducts(res.data || []));
  }, []);

  const monthlyRevenue = aggregateMonthlyRevenue(orders);
  const topProducts = [...products]
    .sort((a, b) => (b.stock ?? 0) - (a.stock ?? 0))
    .slice(0, 10);

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-semibold text-gray-900">Analytics & ML Insights</h2>

      <section className="bg-white border rounded-xl p-6 shadow-sm">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Sales Analytics</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <AnalyticsCard title="Monthly Revenue (sample)">
            <ChartList data={monthlyRevenue} labelKey="month" valueKey="total" prefix="$" />
          </AnalyticsCard>
          <AnalyticsCard title="Top Inventory (proxy for high demand)">
            <ChartList data={topProducts.map(p => ({ label: p.prod_name || "Product", value: p.stock ?? 0 }))} />
          </AnalyticsCard>
        </div>
      </section>

      <section className="bg-white border rounded-xl p-6 shadow-sm">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Customer Segmentation (Mock)</h3>
        <p className="text-sm text-gray-500 mb-4">
          Placeholder visualization until clustering API is available. Replace with actual scatter plot from ML service.
        </p>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            { label: "Champions", count: 42, color: "bg-green-50 text-green-700" },
            { label: "Loyal", count: 67, color: "bg-blue-50 text-blue-700" },
            { label: "At Risk", count: 28, color: "bg-yellow-50 text-yellow-700" },
            { label: "Lost", count: 15, color: "bg-red-50 text-red-700" }
          ].map(segment => (
            <div key={segment.label} className={`rounded-lg p-4 ${segment.color}`}>
              <p className="text-sm font-medium">{segment.label}</p>
              <p className="text-2xl font-semibold mt-2">{segment.count}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="bg-white border rounded-xl p-6 shadow-sm">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Recommendation Insights (Mock)</h3>
        <p className="text-sm text-gray-500 mb-4">
          Connect this section to your recommendation engine once the API is available.
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-medium text-gray-800 mb-2">Frequently Bought Together</h4>
            <ul className="text-sm text-gray-600 list-disc pl-5 space-y-1">
              <li>Denim Jacket + Graphic Tee</li>
              <li>Sports Hoodie + Training Pants</li>
              <li>Classic Sneakers + Everyday Socks</li>
            </ul>
          </div>
          <div>
            <h4 className="font-medium text-gray-800 mb-2">Trending Now</h4>
            <ul className="text-sm text-gray-600 list-disc pl-5 space-y-1">
              <li>EcoLine Windbreaker</li>
              <li>Minimalist Sneakers</li>
              <li>Utility Cargo Pants</li>
            </ul>
          </div>
        </div>
      </section>
    </div>
  );
}

function aggregateMonthlyRevenue(orders) {
  const map = {};
  orders.forEach(order => {
    if (!order.order_date) return;
    const date = new Date(order.order_date);
    if (Number.isNaN(date.getTime())) return;
    const key = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}`;
    map[key] = (map[key] || 0) + (order.total_amount || 0);
  });
  return Object.entries(map)
    .sort(([a], [b]) => (a < b ? -1 : 1))
    .map(([month, total]) => ({ month, total: total.toFixed(2) }))
    .slice(-6);
}

function AnalyticsCard({ title, children }) {
  return (
    <div className="border rounded-lg p-4">
      <h4 className="font-medium text-gray-800 mb-3">{title}</h4>
      {children}
    </div>
  );
}

function ChartList({ data, labelKey = "label", valueKey = "value", prefix = "" }) {
  if (!data.length) return <p className="text-sm text-gray-500">No data available.</p>;
  return (
    <div className="space-y-2">
      {data.map(item => (
        <div key={item[labelKey]} className="flex items-center justify-between text-sm">
          <span className="text-gray-600">{item[labelKey]}</span>
          <span className="font-semibold text-gray-900">
            {prefix}
            {item[valueKey]}
          </span>
        </div>
      ))}
    </div>
  );
}

