import ProductCard from "../components/ProductCard";
import { fetchProducts, fetchProductsWithSales } from "../api/api";
import { useEffect, useState } from "react";
import { useLocation } from "react-router-dom";

export default function ProductListing() {
  const [items, setItems] = useState([]);
  const [isAdmin, setIsAdmin] = useState(false);
  const [sortBy, setSortBy] = useState("default"); // default, price-low, price-high, latest
  const location = useLocation();

  // Get query parameters
  const queryParams = new URLSearchParams(location.search);
  const category = queryParams.get("category");
  const subcategory = queryParams.get("subcategory");
  const gender = queryParams.get("gender");

  useEffect(() => {
    const adminStatus = localStorage.getItem('isAdmin') === 'true';
    setIsAdmin(adminStatus);

    if (adminStatus) {
      // Load products with sales data for admin
      fetchProductsWithSales(100, 0).then(res => setItems(res.data ?? [])).catch(() => setItems([]));
    } else {
      // Load regular products for customers
      fetchProducts(100, 0).then(res => {
        let products = res.data ?? [];
        
        // Filter by category if specified
        if (category) {
          if (category === "kids") {
            products = products.filter(p => 
              p.index_group_name && 
              p.index_group_name.toLowerCase().includes("children")
            );
            
            // Filter by subcategory if specified
            if (subcategory) {
              if (subcategory === "hoodies") {
                products = products.filter(p => 
                  p.product_group_name && 
                  p.product_group_name.toLowerCase().includes("hoodie")
                );
              } else if (subcategory === "jackets") {
                products = products.filter(p => 
                  p.product_group_name && 
                  p.product_group_name.toLowerCase().includes("jacket")
                );
              } else if (subcategory === "bottoms") {
                products = products.filter(p => 
                  p.product_group_name && 
                  (p.product_group_name.toLowerCase().includes("bottom") || 
                   p.product_group_name.toLowerCase().includes("pants") ||
                   p.product_group_name.toLowerCase().includes("jeans") ||
                   p.product_group_name.toLowerCase().includes("trousers"))
                );
              }
            }
          } else if (category === "hoodies") {
            products = products.filter(p => 
              p.product_group_name && 
              p.product_group_name.toLowerCase().includes("hoodie")
            );
          } else if (category === "jackets") {
            products = products.filter(p => 
              p.product_group_name && 
              p.product_group_name.toLowerCase().includes("jacket")
            );
          } else if (category === "accessories") {
            products = products.filter(p => 
              p.product_group_name && 
              (p.product_group_name.toLowerCase().includes("accessory") ||
               p.product_group_name.toLowerCase().includes("hat") ||
               p.product_group_name.toLowerCase().includes("beanie") ||
               p.product_group_name.toLowerCase().includes("scarf") ||
               p.product_group_name.toLowerCase().includes("belt"))
            );
          } else {
            products = products.filter(p => 
              p.product_group_name && 
              p.product_group_name.toLowerCase().includes(category)
            );
          }
        }
        
        // Filter by gender if specified
        if (gender) {
          products = products.filter(p => 
            p.index_group_name && 
            p.index_group_name.toLowerCase().includes(gender)
          );
        }
        
        setItems(products);
      }).catch(() => setItems([]));
    }
  }, [category, subcategory, gender]);

  // Apply sorting
  const sortedItems = [...items];
  switch (sortBy) {
    case "price-low":
      sortedItems.sort((a, b) => a.price - b.price);
      break;
    case "price-high":
      sortedItems.sort((a, b) => b.price - a.price);
      break;
    case "latest":
      // Assuming articles have some date field, using article_id as proxy
      sortedItems.sort((a, b) => b.article_id.localeCompare(a.article_id));
      break;
    default:
      // Default sorting
      break;
  }

  if (isAdmin) {
    // Admin view with table showing name, price, quantity, and sold
    return (
      <div className="app-container mt-10">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-semibold">
            {category ? (category === "kids" ? 
                        (subcategory ? `Kids - ${subcategory.charAt(0).toUpperCase() + subcategory.slice(1)}` : "Kids") :
                        category === "hoodies" ? "Hoodies" : 
                        category === "jackets" ? "Jackets" :
                        category === "accessories" ? "Accessories" :
                        category.charAt(0).toUpperCase() + category.slice(1)) : 
             gender ? gender.charAt(0).toUpperCase() + gender.slice(1) : 
             "Shop"} - Admin View
          </h1>
          <div>
            <label htmlFor="sort" className="mr-2">Sort by:</label>
            <select 
              id="sort"
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="border border-gray-300 rounded-md px-2 py-1"
            >
              <option value="default">Default</option>
              <option value="price-low">Price: Low to High</option>
              <option value="price-high">Price: High to Low</option>
              <option value="latest">Latest</option>
            </select>
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full border-collapse border border-gray-300">
            <thead>
              <tr className="bg-gray-100">
                <th className="border border-gray-300 p-3 text-left">Product Name</th>
                <th className="border border-gray-300 p-3 text-left">Price</th>
                <th className="border border-gray-300 p-3 text-left">Quantity (Stock)</th>
                <th className="border border-gray-300 p-3 text-left">Sold</th>
                <th className="border border-gray-300 p-3 text-left">Image</th>
              </tr>
            </thead>
            <tbody>
              {sortedItems.length ? sortedItems.map((product) => (
                <tr key={product.article_id} className="hover:bg-gray-50">
                  <td className="border border-gray-300 p-3">{product.prod_name || 'N/A'}</td>
                  <td className="border border-gray-300 p-3">${product.price?.toFixed(2) || '0.00'}</td>
                  <td className="border border-gray-300 p-3">{product.stock || 0}</td>
                  <td className="border border-gray-300 p-3">{product.total_sold || 0}</td>
                  <td className="border border-gray-300 p-3">
                    <img
                      src={`/products/${product.image || 'placeholder.jpg'}`}
                      alt={product.prod_name}
                      className="w-16 h-16 object-cover rounded"
                      onError={(e) => {
                        e.target.src = "/products/placeholder.jpg";
                      }}
                    />
                  </td>
                </tr>
              )) : (
                <tr>
                  <td colSpan="5" className="border border-gray-300 p-3 text-center">Loading products...</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    );
  }

  // Regular customer view
  return (
    <div className="app-container mt-10">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-semibold">
          {category ? (category === "kids" ? 
                      (subcategory ? `Kids - ${subcategory.charAt(0).toUpperCase() + subcategory.slice(1)}` : "Kids") :
                      category === "hoodies" ? "Hoodies" : 
                      category === "jackets" ? "Jackets" :
                      category === "accessories" ? "Accessories" :
                      category.charAt(0).toUpperCase() + category.slice(1)) : 
           gender ? gender.charAt(0).toUpperCase() + gender.slice(1) : 
           "Shop"}
        </h1>
        <div>
          <label htmlFor="sort" className="mr-2">Sort by:</label>
          <select 
            id="sort"
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="border border-gray-300 rounded-md px-2 py-1"
          >
            <option value="default">Default</option>
            <option value="price-low">Price: Low to High</option>
            <option value="price-high">Price: High to Low</option>
            <option value="latest">Latest</option>
          </select>
        </div>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
        {sortedItems.length ? sortedItems.map(p => <ProductCard key={p.article_id} product={p} />)
         : Array.from({length:12}).map((_,i)=>(<div key={i} className="card-neutral p-4"><div className="h-44 bg-gray-50 animate-pulse rounded-md"></div></div>))}
      </div>
    </div>
  );
}