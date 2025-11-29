import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AppProvider } from './context/AppContext';
import { ProtectedRoute, ProtectedRouteAdmin } from './components/ProtectedRoute';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import SearchResults from './pages/SearchResults';

// Customer pages
import Home from './pages/Home';
import ProductListing from './pages/ProductListing';
import ProductDetail from './pages/ProductDetail';
import Cart from './pages/Cart';
import Wishlist from './pages/Wishlist';
import Checkout from './pages/Checkout';
import OrdersHistory from './pages/OrdersHistory';
import Reviews from './pages/Reviews';
import Profile from './pages/Profile';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Contact from './pages/Contact';
import Blog from './pages/Blog';
import Settings from './pages/Settings';

// Admin page
import AdminDashboard from './pages/AdminDashboard';

export default function App() {
  return (
    <AppProvider>
      <Router>
        <div className="flex flex-col min-h-screen">
          <Navbar />
          <main className="flex-grow">
            <Routes>
              <Route path='/' element={<Home />} />
              <Route path='/products' element={<ProductListing />} />
              <Route path='/products/:id' element={<ProductDetail />} />
              <Route path='/login' element={<Login />} />
              <Route path='/signup' element={<Signup />} />
              <Route path='/contact' element={<Contact />} />
              <Route path='/blog' element={<Blog />} />
              <Route path='/search' element={<SearchResults />} />
              
              {/* Protected Customer Routes */}
              <Route path='/cart' element={
                <ProtectedRoute>
                  <Cart />
                </ProtectedRoute>
              } />
              <Route path='/wishlist' element={
                <ProtectedRoute>
                  <Wishlist />
                </ProtectedRoute>
              } />
              <Route path='/checkout' element={
                <ProtectedRoute>
                  <Checkout />
                </ProtectedRoute>
              } />
              <Route path='/orders' element={
                <ProtectedRoute>
                  <OrdersHistory />
                </ProtectedRoute>
              } />
              <Route path='/profile' element={
                <ProtectedRoute>
                  <Profile />
                </ProtectedRoute>
              } />
              <Route path='/settings' element={
                <ProtectedRoute>
                  <Settings />
                </ProtectedRoute>
              } />
              <Route path='/reviews/:productId' element={<Reviews />} />

              {/* Admin Routes */}
              <Route path='/admin' element={
                <ProtectedRouteAdmin>
                  <AdminDashboard />
                </ProtectedRouteAdmin>
              } />
            </Routes>
          </main>
          <Footer />
        </div>
      </Router>
    </AppProvider>
  );
}
