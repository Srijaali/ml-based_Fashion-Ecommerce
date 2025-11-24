import { useEffect, useMemo, useState } from "react";
import { fetchProductsWithSales, deleteProduct, updateProductPrice, updateProductStock } from "../../api/api";

const statusLabel = stock => {
  if (stock > 50) return { label: "In Stock", color: "text-green-600 bg-green-50" };
  if (stock > 0) return { label: "Low Stock", color: "text-yellow-600 bg-yellow-50" };
  return { label: "Out of Stock", color: "text-red-600 bg-red-50" };
};

export default function ProductsView() {
  const [items, setItems] = useState([]);
  const [search, setSearch] = useState("");
  const [stockFilter, setStockFilter] = useState("all");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadProducts = () => {
    setLoading(true);
    fetchProductsWithSales(200, 0)
      .then(res => setItems(res.data || []))
      .catch(() => setError("Failed to load products"))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadProducts();
  }, []);

  const filteredItems = useMemo(() => {
    return items.filter(item => {
      const matchesSearch =
        !search ||
        (item.prod_name || "").toLowerCase().includes(search.toLowerCase()) ||
        (item.article_id || "").includes(search);

      let matchesStock = true;
      if (stockFilter === "low") matchesStock = (item.stock ?? 0) > 0 && (item.stock ?? 0) <= 50;
      if (stockFilter === "out") matchesStock = (item.stock ?? 0) === 0;
      if (stockFilter === "in") matchesStock = (item.stock ?? 0) > 50;

      return matchesSearch && matchesStock;
    });
  }, [items, search, stockFilter]);

  const handleDelete = async articleId => {
    if (!window.confirm("Delete this product?")) return;
    try {
      await deleteProduct(articleId);
      loadProducts();
    } catch (err) {
      alert(err.response?.data?.detail || "Failed to delete product");
    }
  };

  const handleQuickUpdate = async (articleId, field, value) => {
    try {
      if (field === "price") {
        await updateProductPrice(articleId, parseFloat(value));
      } else if (field === "stock") {
        await updateProductStock(articleId, parseInt(value, 10));
      }
      loadProducts();
    } catch (err) {
      alert(err.response?.data?.detail || `Failed to update ${field}`);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-semibold text-gray-900">Product Catalog</h2>
          <p className="text-gray-500 text-sm">Manage pricing, inventory, and catalog metadata</p>
        </div>
        <div className="flex flex-col md:flex-row gap-3">
          <input
            type="text"
            placeholder="Search by name or article ID"
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="px-3 py-2 border rounded-lg"
          />
          <select
            value={stockFilter}
            onChange={e => setStockFilter(e.target.value)}
            className="px-3 py-2 border rounded-lg"
          >
            <option value="all">All stock</option>
            <option value="in">In stock</option>
            <option value="low">Low stock</option>
            <option value="out">Out of stock</option>
          </select>
        </div>
      </div>

      <div className="bg-white rounded-xl border overflow-hidden shadow-sm">
        <table className="min-w-full text-sm">
          <thead className="bg-gray-50 text-left text-gray-600 uppercase text-xs tracking-wide">
            <tr>
              <th className="px-4 py-3">Article</th>
              <th className="px-4 py-3">Name</th>
              <th className="px-4 py-3">Category</th>
              <th className="px-4 py-3">Price</th>
              <th className="px-4 py-3">Stock</th>
              <th className="px-4 py-3">Sold</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3 text-right">Actions</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan="8" className="px-4 py-8 text-center text-gray-500">
                  Loading products...
                </td>
              </tr>
            ) : error ? (
              <tr>
                <td colSpan="8" className="px-4 py-8 text-center text-red-500">
                  {error}
                </td>
              </tr>
            ) : filteredItems.length ? (
              filteredItems.map(product => {
                const status = statusLabel(product.stock ?? 0);
                return (
                  <tr key={product.article_id} className="border-t">
                    <td className="px-4 py-3 font-mono text-xs text-gray-500">{product.article_id}</td>
                    <td className="px-4 py-3 text-gray-900">{product.prod_name || "—"}</td>
                    <td className="px-4 py-3 text-gray-600">{product.product_type_name || "—"}</td>
                    <td className="px-4 py-3">
                      <input
                        type="number"
                        className="w-24 border rounded px-2 py-1 text-right"
                        defaultValue={product.price}
                        onBlur={e => handleQuickUpdate(product.article_id, "price", e.target.value)}
                      />
                    </td>
                    <td className="px-4 py-3">
                      <input
                        type="number"
                        className="w-20 border rounded px-2 py-1 text-right"
                        defaultValue={product.stock}
                        onBlur={e => handleQuickUpdate(product.article_id, "stock", e.target.value)}
                      />
                    </td>
                    <td className="px-4 py-3 text-gray-600">{product.total_sold ?? 0}</td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-1 text-xs rounded-full font-medium ${status.color}`}>
                        {status.label}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-right space-x-2">
                      <button
                        onClick={() => handleDelete(product.article_id)}
                        className="text-red-600 hover:underline text-sm"
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                );
              })
            ) : (
              <tr>
                <td colSpan="8" className="px-4 py-8 text-center text-gray-500">
                  No products match the current filters.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

