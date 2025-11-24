import ProductCard from "../components/ProductCard";
import Button from "../components/Button";
import { fetchProducts, fetchTrendingProducts } from "../api/api";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

export default function Home() {
  const [products, setProducts] = useState([]);
  const [trendingProducts, setTrendingProducts] = useState([]);
  const [activeCategory, setActiveCategory] = useState("women");

  useEffect(() => {
    const tempProducts = [
      {
        article_id: 1,
        prod_name: "Black Minimal Jacket",
        price: 120,
        image: "product1.png",
      },
      {
        article_id: 2,
        prod_name: "Grey Urban Hoodie",
        price: 90,
        image: "product2.png",
      },
      {
        article_id: 3,
        prod_name: "Olive Overshirt",
        price: 110,
        image: "product3.png",
      },
      {
        article_id: 4,
        prod_name: "Classic Denim Jacket",
        price: 150,
        image: "product4.png",
      },
      {
        article_id: 5,
        prod_name: "Stone Cargo Jacket",
        price: 160,
        image: "product5.png",
      },
      {
        article_id: 6,
        prod_name: "Ember",
        price: 40,
        image: "beanie1.jpg",
      },
      {
        article_id: 7,
        prod_name: "Obsidian",
        price: 190,
        image: "beanie2.jpg",
      },
      {
        article_id: 8,
        prod_name: "Ecru",
        price: 80,
        image: "beanie3.jpg",
      },
    ];

    setProducts(tempProducts);
    
    // Fetch trending products
    fetchTrendingProducts(8)
      .then(res => setTrendingProducts(res.data || []))
      .catch(() => setTrendingProducts([]));
  }, []);

  // Filter products based on active category
  const filteredProducts = products.filter(product => {
    if (activeCategory === "women") {
      return product.prod_name.includes("Urban") || product.prod_name.includes("Overshirt") || product.prod_name.includes("Ecru");
    } else if (activeCategory === "men") {
      return product.prod_name.includes("Minimal") || product.prod_name.includes("Denim") || product.prod_name.includes("Cargo");
    } else if (activeCategory === "kids") {
      return product.prod_name.includes("Ember") || product.prod_name.includes("Obsidian");
    } else if (activeCategory === "accessories") {
      return product.prod_name.includes("Ember") || product.prod_name.includes("Obsidian") || product.prod_name.includes("Ecru");
    }
    return true;
  });

  return (
    <div>
      {/* HERO */}
      <section className="w-full">
        <div className="w-full h-[50vh] sm:h-[60vh] md:h-[70vh] relative overflow-hidden">
          <img 
            src="/hero.jpg" 
            alt="hero" 
            className="absolute inset-0 w-full h-full object-cover" 
          />
          <div className="absolute inset-0 hero-overlay flex items-center justify-center">
            <div className="text-center text-white px-4">
              <p className="uppercase tracking-wider text-sm mb-4">STRATA</p>
              <h1 className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-bold leading-tight mb-6">
                Outerwear for the
                <span className="block">Modern You</span>
              </h1>
              <Button className="bg-blue-600 text-white hover:bg-blue-700">Discover Now</Button>
            </div>
          </div>
        </div>
      </section>

      {/* TRENDING ARTICLES */}
      {trendingProducts.length > 0 && (
        <section className="app-container mt-16">
          <h2 className="text-3xl font-semibold text-gray-900 text-center mb-10">Trending Articles</h2>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
            {trendingProducts.map((product) => (
              <ProductCard key={product.article_id} product={product} />
            ))}
          </div>
        </section>
      )}

      {/* NEW ARRIVALS */}
      <section className="app-container mt-16">
        <h2 className="text-3xl font-semibold text-gray-900 text-center">New Arrivals</h2>
        <div className="flex justify-center mt-6 text-sm text-gray-500 space-x-6">
          <button 
            className={`pb-1 ${activeCategory === "women" ? "border-b-2 border-gray-900" : ""}`}
            onClick={() => setActiveCategory("women")}
          >
            Women
          </button>
          <button 
            className={`pb-1 ${activeCategory === "men" ? "border-b-2 border-gray-900" : ""}`}
            onClick={() => setActiveCategory("men")}
          >
            Men
          </button>
          <button 
            className={`pb-1 ${activeCategory === "kids" ? "border-b-2 border-gray-900" : ""}`}
            onClick={() => setActiveCategory("kids")}
          >
            Kids
          </button>
          <button 
            className={`pb-1 ${activeCategory === "accessories" ? "border-b-2 border-gray-900" : ""}`}
            onClick={() => setActiveCategory("accessories")}
          >
            Accessories
          </button>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-10 mt-10">
          {filteredProducts.length
            ? filteredProducts.map((p) => (
                <ProductCard key={p.article_id} product={p} />
              ))
            : Array.from({ length: 8 }).map((_, i) => (
                <div key={i} className="card-neutral p-4">
                  <div className="h-44 bg-gray-50 animate-pulse rounded-md"></div>
                </div>
              ))}
        </div>
      </section>

      {/* BASED ON YOUR INTERACTIONS */}
      <section className="app-container mt-16">
        <h2 className="text-3xl font-semibold text-gray-900 text-center mb-10">Based on Your Interactions</h2>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
          {products.slice(0, 4).map((product) => (
            <ProductCard key={`interaction-${product.article_id}`} product={product} />
          ))}
        </div>
      </section>

      {/* CUSTOMERS ALSO BOUGHT */}
      <section className="app-container mt-16">
        <h2 className="text-3xl font-semibold text-gray-900 text-center mb-10">Customers Also Bought</h2>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
          {products.slice(4).map((product) => (
            <ProductCard key={`bought-${product.article_id}`} product={product} />
          ))}
        </div>
      </section>

      {/* CATEGORY CARDS */}
      <section className="app-container mt-16 grid grid-cols-1 md:grid-cols-4 gap-6 mb-20">
        <div 
          className="bg-gray-50 rounded-xl p-6 md:p-8 flex flex-col justify-between aspect-[4/3] min-h-[250px]"
          style={{ 
            backgroundImage: "url('/products/men.jpg')",
            backgroundSize: 'cover',
            backgroundPosition: 'center',
            backgroundRepeat: 'no-repeat'
          }}
        >
          <div>
            <h3 className="text-xl sm:text-2xl font-semibold mb-2 text-white drop-shadow-lg">Where Men Meet Luxury</h3>
            <p className="text-gray-100 drop-shadow-md mb-4">Layer Up for Winter.</p>
          </div>
          <Link to="/products?gender=men">
            <Button className="bg-white text-black self-start">Shop Now</Button>
          </Link>
        </div>

        <div
          className="bg-gray-50 rounded-xl p-6 md:p-8 flex flex-col justify-between aspect-[4/3] min-h-[250px]"
          style={{ 
            backgroundImage: "url('/products/women.png')",
            backgroundSize: 'cover',
            backgroundPosition: 'center',
            backgroundRepeat: 'no-repeat'
          }}
        >
          <div>
            <h3 className="text-xl sm:text-2xl font-semibold mb-2 text-white drop-shadow-lg">Layers Made for Her</h3>
            <p className="text-gray-100 drop-shadow-md mb-4">Winter essentials, reimagined.</p>
          </div>
          <Link to="/products?gender=women">
            <Button className="bg-white text-black self-start">Shop Now</Button>
          </Link>
        </div>

        <div
          className="bg-gray-50 rounded-xl p-6 md:p-8 flex flex-col justify-between aspect-[4/3] min-h-[250px]"
          style={{ 
            backgroundImage: "url('/products/kids.jpg')",
            backgroundSize: 'cover',
            backgroundPosition: 'center',
            backgroundRepeat: 'no-repeat'
          }}
        >
          <div>
            <h3 className="text-xl sm:text-2xl font-semibold mb-2 text-white drop-shadow-lg">Style for Little Ones</h3>
            <p className="text-gray-100 drop-shadow-md mb-4">Comfortable and trendy.</p>
          </div>
          <Link to="/products?category=kids">
            <Button className="bg-white text-black self-start">Shop Now</Button>
          </Link>
        </div>

        <div
          className="bg-gray-50 rounded-xl p-6 md:p-8 flex flex-col justify-between aspect-[4/3] min-h-[250px]"
          style={{ 
            backgroundImage: "url('/products/accessories.jpg')",
            backgroundSize: 'cover',
            backgroundPosition: 'center',
            backgroundRepeat: 'no-repeat'
          }}
        >
          <div>
            <h3 className="text-xl sm:text-2xl font-semibold mb-2 text-white drop-shadow-lg">Accessorize Your Look</h3>
            <p className="text-gray-100 drop-shadow-md mb-4">The perfect finishing touches.</p>
          </div>
          <Link to="/products?category=accessories">
            <Button className="bg-white text-black self-start">Shop Now</Button>
          </Link>
        </div>
      </section>
    </div>
  );
}