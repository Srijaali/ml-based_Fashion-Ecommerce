import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useApp } from "../context/AppContext";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isAdminLogin, setIsAdminLogin] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { login, loginAdmin } = useApp();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      let result;
      
      if (isAdminLogin) {
        // Admin login
        // In development mode, we can use mock authentication
        if (process.env.NODE_ENV === 'development') {
          console.log('Using mock admin authentication in development mode');
          // Use whatever credentials were entered, or defaults
          const adminUsername = email || 'admin';
          const adminPassword = password || 'admin';
          result = await loginAdmin(adminUsername, adminPassword);
        } else {
          // In production, require actual credentials
          if (!email || !password) {
            setError("Please enter username and password");
            setLoading(false);
            return;
          }
          result = await loginAdmin(email, password);
        }
      } else {
        // Customer login
        if (!email || !password) {
          setError("Please enter email and password");
          setLoading(false);
          return;
        }
        
        result = await login(email, password);
      }

      if (result.success) {
        // Redirect based on user type
        if (isAdminLogin) {
          navigate('/admin');
        } else {
          navigate('/profile');
        }
      } else {
        setError(result.error || 'Login failed');
      }
    } catch (err) {
      setError('An unexpected error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 max-w-md mx-auto">
      <h1 className="text-2xl font-bold mb-4">{isAdminLogin ? 'Admin Login' : 'Customer Login'}</h1>
      
      {/* Toggle between Customer and Admin login */}
      <div className="mb-4 flex gap-2">
        <button
          onClick={() => {
            setIsAdminLogin(false);
            setError("");
          }}
          className={`px-4 py-2 rounded ${
            !isAdminLogin
              ? "bg-blue-600 text-white"
              : "bg-gray-200 text-gray-700"
          }`}
        >
          Customer
        </button>
        <button
          onClick={() => {
            setIsAdminLogin(true);
            setError("");
          }}
          className={`px-4 py-2 rounded ${
            isAdminLogin
              ? "bg-blue-600 text-white"
              : "bg-gray-200 text-gray-700"
          }`}
        >
          Admin
        </button>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-100 text-red-700 rounded">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit}>
        {isAdminLogin ? (
          <>
            <div className="mb-4">
              <label className="block text-gray-700 mb-2">Username</label>
              <input
                type="text"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Enter username"
              />
            </div>
            <div className="mb-4">
              <label className="block text-gray-700 mb-2">Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Enter password"
              />
            </div>
          </>
        ) : (
          <>
            <div className="mb-4">
              <label className="block text-gray-700 mb-2">Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Enter email"
              />
            </div>
            <div className="mb-4">
              <label className="block text-gray-700 mb-2">Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Enter password"
              />
            </div>
          </>
        )}

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700 transition-colors disabled:opacity-50"
        >
          {loading ? "Logging in..." : "Login"}
        </button>
      </form>

      {!isAdminLogin && (
        <div className="mt-4 text-center">
          <p className="text-gray-600">
            Don't have an account?{" "}
            <Link to="/signup" className="text-blue-600 hover:underline">
              Sign up
            </Link>
          </p>
        </div>
      )}
      
      {process.env.NODE_ENV === 'development' && isAdminLogin && (
        <div className="mt-4 p-3 bg-yellow-100 text-yellow-700 rounded text-sm">
          <p><strong>Development Mode:</strong> You can login as admin with any username/password</p>
          <p className="mt-1">Try: username=admin, password=admin</p>
        </div>
      )}
    </div>
  );
}