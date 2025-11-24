import { Link, useNavigate } from "react-router-dom";
import { useState, useEffect } from "react";

export default function Navbar() {
  const [showSearch, setShowSearch] = useState(false);
  const [query, setQuery] = useState("");
  const [showShopMenu, setShowShopMenu] = useState(false);
  const [showMenSubmenu, setShowMenSubmenu] = useState(false);
  const [showWomenSubmenu, setShowWomenSubmenu] = useState(false);
  const [showKidsSubmenu, setShowKidsSubmenu] = useState(false);
  const [isAdmin, setIsAdmin] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const syncAdminStatus = () => {
      setIsAdmin(localStorage.getItem('isAdmin') === 'true');
    };
    syncAdminStatus();

    window.addEventListener('storage', syncAdminStatus);
    window.addEventListener('admin-status-changed', syncAdminStatus);
    return () => {
      window.removeEventListener('storage', syncAdminStatus);
      window.removeEventListener('admin-status-changed', syncAdminStatus);
    };
  }, []);


  const handleSearch = (e) => {
    e.preventDefault();
    if (!query.trim()) return;
    navigate(`/search?query=${encodeURIComponent(query.trim())}`);
    setQuery("");
    setShowSearch(false);
  };

  return (
    <header className="w-full bg-white border-b border-gray-100 sticky top-0 z-30">
      <div className="app-container flex items-center justify-between py-4">
        {/* LEFT LINKS */}
        <div className="flex items-center space-x-6 text-sm text-brand-600">
          <Link to="/" className="hover:text-black">Home</Link>
          <div 
            className="relative"
            onMouseEnter={() => setShowShopMenu(true)}
            onMouseLeave={() => {
              setShowShopMenu(false);
              setShowMenSubmenu(false);
              setShowWomenSubmenu(false);
              setShowKidsSubmenu(false);
            }}
          >
            <Link to="/products" className="hover:text-black cursor-pointer block py-2">Shop</Link>
            {showShopMenu && (
              <div className="absolute top-full left-0 pt-2 w-48 z-50">
                <div className="bg-white border border-gray-200 rounded-md shadow-lg py-2">
                <Link 
                  to="/products?gender=men"
                  className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 relative group cursor-pointer"
                  onMouseEnter={() => setShowMenSubmenu(true)}
                  onMouseLeave={() => setShowMenSubmenu(false)}
                >
                  Men →
                  {showMenSubmenu && (
                    <div className="absolute left-full top-0 pl-1 w-40 z-50">
                      <div className="bg-white border border-gray-200 rounded-md shadow-lg py-2">
                      <Link 
                        to="/products?gender=men&category=hoodies"
                        className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 cursor-pointer"
                      >
                        Hoodies
                      </Link>
                      <Link 
                        to="/products?gender=men&category=jackets"
                        className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 cursor-pointer"
                      >
                        Jackets
                      </Link>
                      <Link 
                        to="/products?gender=men&category=bottoms"
                        className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 cursor-pointer"
                      >
                        Bottoms
                      </Link>
                      </div>
                    </div>
                  )}
                </Link>
                <Link 
                  to="/products?gender=women"
                  className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 relative group cursor-pointer"
                  onMouseEnter={() => setShowWomenSubmenu(true)}
                  onMouseLeave={() => setShowWomenSubmenu(false)}
                >
                  Women →
                  {showWomenSubmenu && (
                    <div className="absolute left-full top-0 pl-1 w-40 z-50">
                      <div className="bg-white border border-gray-200 rounded-md shadow-lg py-2">
                      <Link 
                        to="/products?gender=women&category=hoodies"
                        className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 cursor-pointer"
                      >
                        Hoodies
                      </Link>
                      <Link 
                        to="/products?gender=women&category=jackets"
                        className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 cursor-pointer"
                      >
                        Jackets
                      </Link>
                      <Link 
                        to="/products?gender=women&category=bottoms"
                        className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 cursor-pointer"
                      >
                        Bottoms
                      </Link>
                      </div>
                    </div>
                  )}
                </Link>
                <Link 
                  to="/products?category=kids"
                  className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 relative group cursor-pointer"
                  onMouseEnter={() => setShowKidsSubmenu(true)}
                  onMouseLeave={() => setShowKidsSubmenu(false)}
                >
                  Kids →
                  {showKidsSubmenu && (
                    <div className="absolute left-full top-0 pl-1 w-40 z-50">
                      <div className="bg-white border border-gray-200 rounded-md shadow-lg py-2">
                      <Link 
                        to="/products?category=kids&subcategory=hoodies"
                        className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 cursor-pointer"
                      >
                        Hoodies
                      </Link>
                      <Link 
                        to="/products?category=kids&subcategory=jackets"
                        className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 cursor-pointer"
                      >
                        Jackets
                      </Link>
                      <Link 
                        to="/products?category=kids&subcategory=bottoms"
                        className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 cursor-pointer"
                      >
                        Bottoms
                      </Link>
                      </div>
                    </div>
                  )}
                </Link>
                <Link 
                  to="/products"
                  className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 cursor-pointer"
                >
                  For All
                </Link>
                <Link 
                  to="/products?category=accessories"
                  className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 cursor-pointer"
                >
                  Accessories
                </Link>
                </div>
              </div>
            )}
          </div>
          <Link to="/blog" className="hover:text-black">Blog</Link>
          <Link to="/contact" className="hover:text-black">Contact</Link>
        </div>

        {/* CENTER LOGO */}
        <div className="text-2xl font-semibold text-gray-900">
          <Link to="/">LAYR<span className="text-brand-600">.</span></Link>
        </div>

        {/* RIGHT ICONS */}
        <div className="flex items-center space-x-4 relative">
          {/* search icon toggles a small search dropdown */}
          <button
            onClick={() => setShowSearch(prev => !prev)}
            className="text-gray-600 hover:text-black p-2 rounded"
            aria-label="Search"
          >
            🔍
          </button>

          {showSearch && (
            <form onSubmit={handleSearch} className="absolute top-12 right-0 bg-white border rounded-md shadow p-3 w-72">
              <input
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="w-full border border-gray-200 px-3 py-2 rounded text-sm"
                placeholder="Search products..."
                aria-label="Search input"
              />
              <button 
                type="submit"
                className="mt-2 w-full bg-blue-600 text-white py-1 rounded text-sm hover:bg-blue-700"
              >
                Search
              </button>
            </form>
          )}

          {isAdmin ? (
            <Link to="/admin" className="text-gray-600 hover:text-black p-2">⚙️</Link>
          ) : (
            <Link to="/settings" className="text-gray-600 hover:text-black p-2">⚙️</Link>
          )}
          <Link to="/wishlist" className="text-gray-600 hover:text-black p-2">♡</Link>
          <Link to="/profile" className="text-gray-600 hover:text-black p-2">👤</Link>
          <Link to="/cart" className="text-gray-600 hover:text-black p-2 text-lg">🛒</Link>
        </div>
      </div>
    </header>
  );
}