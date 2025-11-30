import ProductCard from "../components/ProductCard";
import Button from "../components/Button";
import { sections, articles } from "../api/api";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

export default function Home() {
  const [featuredProducts, setFeaturedProducts] = useState([]);
  const [sectionsList, setSectionsList] = useState([]);
  const [activeSection, setActiveSection] = useState("women");
  const [sectionProducts, setSectionProducts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Load sections
    sections.getSections()
      .then(res => {
        setSectionsList(res.data.sections || []);
      })
      .catch(err => console.error('Failed to load sections:', err));

    // Load featured products
    articles.getAll(0, 8)
      .then(res => {
        setFeaturedProducts(res.data || []);
      })
      .catch(err => console.error('Failed to load products:', err))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    // Load section products when active section changes
    if (activeSection) {
      sections.getSectionProducts(activeSection, 8)
        .then(res => {
          setSectionProducts(res.data.products || []);
        })
        .catch(err => console.error('Failed to load section products:', err));
    }
  }, [activeSection]);

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
              <Link to="/products">
                <Button className="bg-blue-600 text-white hover:bg-blue-700">Discover Now</Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* FEATURED PRODUCTS */}
      <section className="app-container mt-16">
        <h2 className="text-3xl font-semibold text-gray-900 text-center mb-10">Featured Products</h2>
        {loading ? (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
            {Array.from({ length: 8 }).map((_, i) => (
              <div key={i} className="card-neutral p-4">
                <div className="h-44 bg-gray-50 animate-pulse rounded-md"></div>
              </div>
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
            {featuredProducts.map((product) => (
              <ProductCard key={product.article_id} product={product} />
            ))}
          </div>
        )}
      </section>

      {/* NEW ARRIVALS BY SECTION */}
      <section className="app-container mt-16">
        <h2 className="text-3xl font-semibold text-gray-900 text-center">New Arrivals</h2>
        <div className="flex justify-center mt-6 text-sm text-gray-500 space-x-6 flex-wrap">
          {sectionsList.map((section) => (
            <button
              key={section.id}
              className={`pb-1 ${activeSection === section.name ? "border-b-2 border-gray-900" : ""}`}
              onClick={() => setActiveSection(section.name)}
            >
              {section.display}
            </button>
          ))}
        </div>

        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-10 mt-10">
          {sectionProducts.length > 0
            ? sectionProducts.map((p) => (
                <ProductCard key={p.article_id} product={p} />
              ))
            : Array.from({ length: 8 }).map((_, i) => (
                <div key={i} className="card-neutral p-4">
                  <div className="h-44 bg-gray-50 animate-pulse rounded-md"></div>
                </div>
              ))}
        </div>
      </section>

      {/* CATEGORY CARDS */}
      <section className="app-container mt-16 grid grid-cols-1 md:grid-cols-4 gap-6 mb-20">
        <div 
          className="bg-gray-50 rounded-xl p-6 md:p-8 flex flex-col justify-between aspect-[4/3] min-h-[250px]"
          style={{ 
            backgroundImage: "url('/images/men.jpg')",
            backgroundSize: 'cover',
            backgroundPosition: 'center',
            backgroundRepeat: 'no-repeat'
          }}
        >
          <div>
            <h3 className="text-xl sm:text-2xl font-semibold mb-2 text-white drop-shadow-lg">Where Men Meet Luxury</h3>
            <p className="text-gray-100 drop-shadow-md mb-4">Layer Up for Winter.</p>
          </div>
          <Link to="/products?section=men">
            <Button className="bg-white text-black self-start">Shop Now</Button>
          </Link>
        </div>

        <div
          className="bg-gray-50 rounded-xl p-6 md:p-8 flex flex-col justify-between aspect-[4/3] min-h-[250px]"
          style={{ 
            backgroundImage: "url('/filtered_images/women.png')",
            backgroundSize: 'cover',
            backgroundPosition: 'center',
            backgroundRepeat: 'no-repeat'
          }}
        >
          <div>
            <h3 className="text-xl sm:text-2xl font-semibold mb-2 text-white drop-shadow-lg">Layers Made for Her</h3>
            <p className="text-gray-100 drop-shadow-md mb-4">Winter essentials, reimagined.</p>
          </div>
          <Link to="/products?section=women">
            <Button className="bg-white text-black self-start">Shop Now</Button>
          </Link>
        </div>

        <div
          className="bg-gray-50 rounded-xl p-6 md:p-8 flex flex-col justify-between aspect-[4/3] min-h-[250px]"
          style={{ 
            backgroundImage: "url('/images/kids.jpg')",
            backgroundSize: 'cover',
            backgroundPosition: 'center',
            backgroundRepeat: 'no-repeat'
          }}
        >
          <div>
            <h3 className="text-xl sm:text-2xl font-semibold mb-2 text-white drop-shadow-lg">Style for Little Ones</h3>
            <p className="text-gray-100 drop-shadow-md mb-4">Comfortable and trendy.</p>
          </div>
          <Link to="/products?section=kids">
            <Button className="bg-white text-black self-start">Shop Now</Button>
          </Link>
        </div>

        <div
          className="bg-gray-50 rounded-xl p-6 md:p-8 flex flex-col justify-between aspect-[4/3] min-h-[250px]"
          style={{ 
            backgroundImage: "url('/images/accessories.jpg')",
            backgroundSize: 'cover',
            backgroundPosition: 'center',
            backgroundRepeat: 'no-repeat'
          }}
        >
          <div>
            <h3 className="text-xl sm:text-2xl font-semibold mb-2 text-white drop-shadow-lg">Accessorize Your Look</h3>
            <p className="text-gray-100 drop-shadow-md mb-4">The perfect finishing touches.</p>
          </div>
          <Link to="/products?section=accessories">
            <Button className="bg-white text-black self-start">Shop Now</Button>
          </Link>
        </div>
      </section>
    </div>
  );
}