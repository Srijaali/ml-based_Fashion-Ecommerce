import { useMemo, useState } from "react";
import DashboardOverview from "./admin/DashboardOverview";
import ProductsView from "./admin/ProductsView";
import ProductAdd from "./admin/ProductAdd";
import ProductStock from "./admin/ProductStock";
import ProductPrice from "./admin/ProductPrice";
import CategoriesView from "./admin/CategoriesView";
import OrdersView from "./admin/OrdersView";
import CustomersView from "./admin/CustomersView";
import ReviewsView from "./admin/ReviewsView";
import AnalyticsView from "./admin/AnalyticsView";
import EventsView from "./admin/EventsView";
import LogsView from "./admin/LogsView";
import SettingsView from "./admin/SettingsView";

const navStructure = [
  {
    label: "Dashboard",
    items: [{ id: "dashboard", title: "Overview" }]
  },
  {
    label: "Products",
    items: [
      { id: "products-view", title: "View Products" },
      { id: "products-add", title: "Add Product" },
      { id: "products-stock", title: "Update Stock" },
      { id: "products-price", title: "Update Price" }
    ]
  },
  {
    label: "Operations",
    items: [
      { id: "categories", title: "Categories" },
      { id: "orders", title: "Orders" },
      { id: "customers", title: "Customers" },
      { id: "reviews", title: "Reviews" },
      { id: "events", title: "Events" }
    ]
  },
  {
    label: "Analytics",
    items: [
      { id: "analytics", title: "ML Analytics" },
      { id: "logs", title: "Admin Logs" },
      { id: "settings", title: "Settings" }
    ]
  }
];

const componentMap = {
  dashboard: DashboardOverview,
  "products-view": ProductsView,
  "products-add": ProductAdd,
  "products-stock": ProductStock,
  "products-price": ProductPrice,
  categories: CategoriesView,
  orders: OrdersView,
  customers: CustomersView,
  reviews: ReviewsView,
  analytics: AnalyticsView,
  events: EventsView,
  logs: LogsView,
  settings: SettingsView
};

export default function AdminDashboard() {
  const [activeSection, setActiveSection] = useState("dashboard");
  const [collapsed, setCollapsed] = useState(false);
  const isAdmin = typeof window !== "undefined" ? localStorage.getItem("isAdmin") === "true" : false;
  const visibleNav = useMemo(() => {
    return navStructure
      .map(section => ({
        ...section,
        items: section.items.filter(item => item.id !== "settings" || isAdmin)
      }))
      .filter(section => section.items.length);
  }, [isAdmin]);
  const ActiveComponent = useMemo(() => componentMap[activeSection] || DashboardOverview, [activeSection]);

  if (!isAdmin) {
    return (
      <div className="p-10 text-center">
        <p className="text-xl text-gray-600">You must be an administrator to view this page.</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex bg-gray-100">
      <aside className={`bg-white border-r shadow-sm transition-all ${collapsed ? "w-20" : "w-72"}`}>
        <div className="px-6 py-5 border-b flex items-center justify-between">
          <div>
            <p className="text-xs uppercase text-gray-500 tracking-wide">Admin Panel</p>
            <h1 className="text-2xl font-semibold text-gray-900">LAYR</h1>
          </div>
          <button
            onClick={() => setCollapsed(prev => !prev)}
            className="text-gray-500 hover:text-gray-900"
          >
            {collapsed ? "»" : "«"}
          </button>
        </div>
        <nav className="p-4 space-y-6 overflow-y-auto h-[calc(100vh-80px)]">
          {visibleNav.map(section => (
            <div key={section.label}>
              {!collapsed && <p className="text-xs uppercase text-gray-400 mb-2">{section.label}</p>}
              <div className="space-y-1">
                {section.items.map(item => (
                  <button
                    key={item.id}
                    onClick={() => setActiveSection(item.id)}
                    className={`w-full text-left px-3 py-2 rounded-lg text-sm font-medium ${
                      activeSection === item.id ? "bg-gray-900 text-white" : "text-gray-700 hover:bg-gray-100"
                    }`}
                    title={collapsed ? item.title : undefined}
                  >
                    {collapsed ? item.title.charAt(0) : item.title}
                  </button>
                ))}
              </div>
            </div>
          ))}
          <button
            onClick={() => {
              localStorage.removeItem("isAdmin");
              localStorage.removeItem("adminLoggedIn");
              window.dispatchEvent(new Event('admin-status-changed'));
              window.location.href = "/login";
            }}
            className="w-full text-left px-3 py-2 rounded-lg text-sm font-medium text-red-600 hover:bg-red-50"
            title={collapsed ? "Logout" : undefined}
          >
            Logout
          </button>
        </nav>
      </aside>

      <main className="flex-1 p-6">
        <ActiveComponent />
      </main>
    </div>
  );
}

