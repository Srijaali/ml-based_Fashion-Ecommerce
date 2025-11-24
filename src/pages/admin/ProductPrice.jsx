import { useEffect, useState } from "react";
import { fetchProductsWithSales, updateProductPrice } from "../../api/api";

export default function ProductPrice() {
  const [products, setProducts] = useState([]);
  const [changes, setChanges] = useState({});
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const load = () => {
    setLoading(true);
    fetchProductsWithSales(150, 0)
      .then(res => setProducts(res.data || []))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    load();
  }, []);

  const handleChange = (id, value) => {
    setChanges(prev => ({ ...prev, [id]: value }));
    setMessage("");
  };

  const handleUpdate = async articleId => {
    const value = parseFloat(changes[articleId]);
    if (Number.isNaN(value) || value <= 0) {
      alert("Enter a valid price");
      return;
    }
    try {
      await updateProductPrice(articleId, value);
      setMessage("Price updated!");
      setChanges(prev => ({ ...prev, [articleId]: "" }));
      load();
    } catch (err) {
      alert(err.response?.data?.detail || "Failed to update price");
    }
  };

  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-2xl font-semibold text-gray-900">Update Price</h2>
        <p className="text-gray-500">Adjust pricing and keep catalog values in sync.</p>
        {message && <p className="text-green-600 mt-2">{message}</p>}
      </div>

      <div className="bg-white border rounded-xl overflow-hidden shadow-sm">
        <table className="min-w-full text-sm">
          <thead className="bg-gray-50 text-left text-gray-600 uppercase text-xs tracking-wide">
            <tr>
              <th className="px-4 py-3">Article</th>
              <th className="px-4 py-3">Name</th>
              <th className="px-4 py-3">Current Price</th>
              <th className="px-4 py-3">New Price</th>
              <th className="px-4 py-3 text-right">Action</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan="5" className="px-4 py-8 text-center text-gray-500">
                  Loading pricing...
                </td>
              </tr>
            ) : (
              products.map(product => (
                <tr key={product.article_id} className="border-t">
                  <td className="px-4 py-3 font-mono text-xs text-gray-500">{product.article_id}</td>
                  <td className="px-4 py-3">{product.prod_name || "—"}</td>
                  <td className="px-4 py-3 text-gray-800">${product.price?.toFixed(2) ?? "0.00"}</td>
                  <td className="px-4 py-3">
                    <input
                      type="number"
                      step="0.01"
                      value={changes[product.article_id] ?? ""}
                      onChange={e => handleChange(product.article_id, e.target.value)}
                      className="border rounded px-3 py-2 w-32"
                    />
                  </td>
                  <td className="px-4 py-3 text-right">
                    <button
                      onClick={() => handleUpdate(product.article_id)}
                      className="bg-gray-900 text-white px-4 py-2 rounded-lg text-sm disabled:opacity-50"
                      disabled={!changes[product.article_id]}
                    >
                      Update
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

