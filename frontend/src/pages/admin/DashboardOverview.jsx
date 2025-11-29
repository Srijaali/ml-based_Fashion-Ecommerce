import { useEffect, useMemo, useState } from "react";
import { orders, articles, customers } from "../../api/api";

const metricCards = [
  { key: "revenueToday", label: "Revenue (Today)" },
  { key: "revenueMonth", label: "Revenue (This Month)" },
  { key: "totalOrders", label: "Total Orders" },
  { key: "totalCustomers", label: "Total Customers" },
  { key: "lowStock", label: "Low Stock Items" },
  { key: "newReviews", label: "New Reviews" }
];

export default function DashboardOverview() {
  const [orders, setOrders] = useState([]);
  const [products, setProducts] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let mounted = true;
    setLoading(true);
    Promise.all([
      orders.getAll(0, 100),
      articles.getAll(0, 100),
      customers.getAll(0, 100)
    ])
      .then(([ordersRes, productsRes, customersRes]) => {
        if (!mounted) return;
        setOrders(ordersRes.data || []);
        setProducts(productsRes.data || []);
        setCustomers(customersRes.data || []);
      })
      .catch(() => {
        if (!mounted) return;
        setError("Failed to load dashboard data");
      })
      .finally(() => mounted && setLoading(false));

    return () => {
      mounted = false;
    };
  }, []);

  const metrics = useMemo(() => {
    const now = new Date();
    const today = now.toISOString().slice(0, 10);
    const currentMonth = now.getMonth();
    const currentYear = now.getFullYear();

    const revenueToday = orders
      .filter(order => (order.order_date || "").startsWith(today))
      .reduce((sum, order) => sum + (order.total_amount || 0), 0);

    const revenueMonth = orders
      .filter(order => {
        const date = new Date(order.order_date);
        return date.getMonth() === currentMonth && date.getFullYear() === currentYear;
      })
      .reduce((sum, order) => sum + (order.total_amount || 0), 0);

    const lowStock = products.filter(p => (p.stock ?? 0) < 25).length;

    return {
      revenueToday,
      revenueMonth,
      totalOrders: orders.length,
      totalCustomers: customers.length,
      lowStock,
      newReviews: 0 // Placeholder until review feed is wired
    };
  }, [orders, products, customers]);

  const trendData = useMemo(() => {
    const daily = {};
    orders.forEach(order => {
      const day = (order.order_date || "").slice(0, 10);
      if (!day) return;
      daily[day] = (daily[day] || 0) + (order.total_amount || 0);
    });
    return Object.entries(daily)
      .sort(([a], [b]) => (a < b ? -1 : 1))
      .slice(-7);
  }, [orders]);

  if (loading) {
    return <div className="p-6 bg-white rounded-xl border">Loading dashboard...</div>;
  }

  if (error) {
    return <div className="p-6 bg-red-50 border border-red-200 text-red-700 rounded-xl">{error}</div>;
  }

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-3 xl:grid-cols-6 gap-4">
        {metricCards.map(card => (
          <div key={card.key} className="bg-white rounded-xl border p-4 shadow-sm">
            <p className="text-sm text-gray-500">{card.label}</p>
            <p className="text-2xl font-semibold mt-2">
              {card.key.includes("Revenue") ? `$${metrics[card.key]?.toFixed(2) ?? "0.00"}` : metrics[card.key] ?? 0}
            </p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl border p-6 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-lg text-gray-900">Daily Revenue (7d)</h3>
            <span className="text-sm text-gray-500">Based on orders data</span>
          </div>
          <div className="space-y-3">
            {trendData.length ? (
              trendData.map(([day, amount]) => (
                <div key={day} className="flex items-center justify-between text-sm">
                  <span className="text-gray-600">{day}</span>
                  <span className="font-semibold">${amount.toFixed(2)}</span>
                </div>
              ))
            ) : (
              <p className="text-gray-500 text-sm">Not enough data to display trend.</p>
            )}
          </div>
        </div>

        <div className="bg-white rounded-xl border p-6 shadow-sm">
          <h3 className="font-semibold text-lg text-gray-900 mb-4">Top Performing Products</h3>
          <div className="space-y-4">
            {products
              .slice(0, 5)
              .map(product => (
                <div key={product.article_id} className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-gray-800">{product.prod_name || "Unnamed product"}</p>
                    <p className="text-sm text-gray-500">Stock: {product.stock ?? 0}</p>
                  </div>
                  <span className="font-semibold text-brand-600">${product.price?.toFixed(2) ?? "0.00"}</span>
                </div>
              ))}
          </div>
        </div>
      </div>
    </div>
  );
}

