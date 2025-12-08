import ProductCard from "../components/ProductCard";
import { sections, articles } from "../api/api";
import { useEffect, useState } from "react";
import { useLocation } from "react-router-dom";

export default function ProductListing() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [sortBy, setSortBy] = useState("popular");
  const [currentPage, setCurrentPage] = useState(1); // Changed to 1-indexed for display
  const [totalPages, setTotalPages] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const location = useLocation();

  // Get query parameters
  const queryParams = new URLSearchParams(location.search);
  const section = queryParams.get("section"); // No default, undefined if not present
  const category = queryParams.get("category");
  
  const ITEMS_PER_PAGE = 24;

  // Load products based on section/category
  const loadProducts = async (page = 1) => { // Changed to 1-indexed
    setLoading(true);
    
    try {
      const offset = (page - 1) * ITEMS_PER_PAGE; // Convert to 0-indexed for API
      let response;
      let newProducts = [];
      let totalCount = 0;
      
      console.log('Loading products - Section:', section, 'Category:', category, 'Page:', page);
      
      try {
        if (category) {
          // Try sections API first for category products
          console.log('Fetching category products:', `${section}/${category}`);
          // Get products for this category with proper pagination
          response = await sections.getCategoryProducts(
            section, 
            category, 
            sortBy, 
            ITEMS_PER_PAGE, // Get only what we need for this page
            offset         // Proper offset for pagination
          );
          console.log('Category products response:', response);
        } else if (section) {
          // Try sections API first for section products
          console.log('Fetching section products:', section);
          // Get products for this section with proper pagination
          response = await sections.getSectionProducts(
            section, 
            ITEMS_PER_PAGE, // Get only what we need for this page
            offset         // Proper offset for pagination
          );
          console.log('Section products response:', response);
        } else {
          // "For All" case - fetch all products without section filtering
          console.log('Fetching all products (For All case)');
          // Use articles API as fallback for all products
          const articlesResponse = await articles.getAll(offset, ITEMS_PER_PAGE);
          newProducts = articlesResponse.data || [];
          
          // Try to get total count for pagination
          try {
            const totalCountResponse = await articles.getAll(0, 1000); // Get a larger sample
            totalCount = (totalCountResponse.data || []).length;
          } catch (countError) {
            totalCount = newProducts.length;
            console.warn('Could not get total product count:', countError);
          }
          
          console.log('All products response:', newProducts);
          // Skip the rest of the try block since we already have our data
          throw new Error('USE_FALLBACK');
        }
        
        newProducts = response.data?.products || [];
        totalCount = response.data?.total_products || newProducts.length;
        
        // If we got fewer products than expected and it's the first page, 
        // try to get a better count by fetching a larger set once
        if (page === 1 && newProducts.length < ITEMS_PER_PAGE && totalCount === newProducts.length) {
          try {
            // Try to get total count by fetching more items
            const countResponse = await (category 
              ? sections.getCategoryProducts(section, category, sortBy, 100, 0)
              : sections.getSectionProducts(section, 100, 0));
            totalCount = countResponse.data?.total_products || (countResponse.data?.products || []).length;
          } catch (countError) {
            console.warn('Could not get accurate product count:', countError);
          }
        }
      } catch (sectionsError) {
        // Check if this is our special "USE_FALLBACK" case for "For All"
        if (sectionsError.message === 'USE_FALLBACK') {
          // We already have the data from the "For All" case, so just continue
          console.log('Using "For All" data');
        } else {
          console.warn('Sections API failed, falling back to articles API:', sectionsError);
          console.warn('Sections API error details:', sectionsError.response?.data);
          
          // Fallback to articles API with client-side filtering
          const articlesResponse = await articles.getAll(offset, ITEMS_PER_PAGE);
          newProducts = articlesResponse.data || [];
          
          // Try to get total count for pagination
          try {
            const totalCountResponse = await articles.getAll(0, 500); // Get a reasonable sample
            totalCount = (totalCountResponse.data || []).length;
          } catch (countError) {
            totalCount = newProducts.length;
            console.warn('Could not get total product count:', countError);
          }
          
          // Filter by section if needed (this is inefficient but necessary for fallback)
          if (section && section !== 'all') {
            // Note: This won't work well with pagination since we're filtering client-side
            // This is just a fallback mechanism
            console.log(`Fallback mode - filtering by section '${section}' not implemented for pagination`);
          }
          
          // Filter by category if needed (this is inefficient but necessary for fallback)
          if (category) {
            // Note: This won't work well with pagination since we're filtering client-side
            // This is just a fallback mechanism
            console.log(`Fallback mode - filtering by category '${category}' not implemented for pagination`);
          }
          
          console.log('Using fallback articles API, products:', newProducts.length);
        }
      }
      
      console.log('Loaded products:', newProducts.length, newProducts);
      
      // Always replace items (not append)
      setItems(newProducts);
      
      // Update total count and calculate total pages
      setTotalCount(totalCount);
      setTotalPages(Math.ceil(totalCount / ITEMS_PER_PAGE) || 1);
      
      // Scroll to top when page changes
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (err) {
      console.error('Failed to load products:', err);
      console.error('Error details:', err.response?.data);
      setItems([]);
      setTotalPages(1);
    } finally {
      setLoading(false);
    }
  };

  // Initial load when section/category/sort changes
  useEffect(() => {
    setCurrentPage(1);
    loadProducts(1);
  }, [section, category, sortBy]);

  // Handle page change
  const handlePageChange = (page) => {
    setCurrentPage(page);
    loadProducts(page);
  };

  // Generate page numbers to display
  const getPageNumbers = () => {
    const pages = [];
    const maxPagesToShow = 7;
    
    if (totalPages <= maxPagesToShow) {
      // Show all pages if total is small
      for (let i = 1; i <= totalPages; i++) {
        pages.push(i);
      }
    } else {
      // Show subset with ellipsis
      if (currentPage <= 4) {
        // Near start
        for (let i = 1; i <= 5; i++) pages.push(i);
        pages.push('...');
        pages.push(totalPages);
      } else if (currentPage >= totalPages - 3) {
        // Near end
        pages.push(1);
        pages.push('...');
        for (let i = totalPages - 4; i <= totalPages; i++) pages.push(i);
      } else {
        // Middle
        pages.push(1);
        pages.push('...');
        for (let i = currentPage - 1; i <= currentPage + 1; i++) pages.push(i);
        pages.push('...');
        pages.push(totalPages);
      }
    }
    
    return pages;
  };

  // Get page title
  const getTitle = () => {
    if (category) {
      return category.charAt(0).toUpperCase() + category.slice(1);
    }
    
    // Handle the "For All" case when no section is specified
    if (!section || section === 'all') {
      return 'For All';
    }
    
    return section.charAt(0).toUpperCase() + section.slice(1) + "'s Fashion";
  };

  return (
    <div className="app-container mt-10">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-semibold">{getTitle()}</h1>
          <p className="text-sm text-gray-500 mt-1">
            {loading ? 'Loading...' : `Showing ${items.length} of ${totalCount} products - Page ${currentPage} of ${totalPages}`}
          </p>
        </div>
        <div>
          <label htmlFor="sort" className="mr-2 text-sm">Sort by:</label>
          <select 
            id="sort"
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="border border-gray-300 rounded-md px-3 py-2 text-sm"
          >
            <option value="popular">Popular</option>
            <option value="price_low_high">Price: Low to High</option>
            <option value="price_high_low">Price: High to Low</option>
            <option value="newest">Newest</option>
          </select>
        </div>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
          {Array.from({length: 12}).map((_, i) => (
            <div key={i} className="card-neutral p-4">
              <div className="h-64 bg-gray-200 animate-pulse rounded-md"></div>
              <div className="h-4 bg-gray-200 animate-pulse rounded mt-4"></div>
              <div className="h-4 bg-gray-200 animate-pulse rounded mt-2 w-2/3"></div>
            </div>
          ))}
        </div>
      ) : items.length > 0 ? (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
            {items.map(p => (
              <ProductCard key={p.article_id} product={p} />
            ))}
          </div>
          
          {/* Pagination Controls */}
          {totalPages > 1 && (
            <div className="flex justify-center items-center gap-2 mt-12">
              {/* Previous Button */}
              <button
                onClick={() => handlePageChange(currentPage - 1)}
                disabled={currentPage === 1}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                Previous
              </button>
              
              {/* Page Numbers */}
              {getPageNumbers().map((page, index) => (
                page === '...' ? (
                  <span key={`ellipsis-${index}`} className="px-2 text-gray-400">...</span>
                ) : (
                  <button
                    key={page}
                    onClick={() => handlePageChange(page)}
                    className={`px-4 py-2 border rounded-lg transition-colors ${
                      currentPage === page
                        ? 'bg-blue-600 text-white border-blue-600'
                        : 'border-gray-300 hover:bg-gray-50'
                    }`}
                  >
                    {page}
                  </button>
                )
              ))}
              
              {/* Next Button */}
              <button
                onClick={() => handlePageChange(currentPage + 1)}
                disabled={currentPage === totalPages}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                Next
              </button>
            </div>
          )}
        </>
      ) : (
        <div className="text-center py-16">
          <div className="max-w-md mx-auto">
            <svg className="mx-auto h-24 w-24 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
            </svg>
            <h3 className="text-xl font-semibold text-gray-900 mt-4">No products found</h3>
            <p className="text-gray-500 mt-2">Try adjusting your filters or check back later.</p>
          </div>
        </div>
      )}
    </div>
  );
}
