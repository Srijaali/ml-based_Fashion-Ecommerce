import { useState } from "react";
import { api } from "../api/api";
import { useNavigate } from "react-router-dom";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [signupForm, setSignupForm] = useState({
    firstName: "",
    lastName: "",
    contact: "",
    email: "",
    password: "",
    confirmPassword: "",
    address: ""
  });
  const [signupState, setSignupState] = useState({ loading: false, success: "", error: "" });
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    
    // Check if admin login
    if (email === "admin@admin.com" && password === "admin123") {
      localStorage.setItem('isAdmin', 'true');
      localStorage.setItem('adminLoggedIn', 'true');
      window.dispatchEvent(new Event('admin-status-changed'));
      alert("Admin login successful!");
      navigate('/admin');
      return;
    }

    // Demo/Test mode - bypass database for UI testing
    if (email === "demo@user.com" && password === "demo123") {
      const demoUser = {
        customer_id: "DEMO-001",
        first_name: "Demo",
        last_name: "User",
        email: "demo@user.com",
        active: true
      };
      localStorage.setItem('loggedInUser', JSON.stringify(demoUser));
      localStorage.setItem('userId', demoUser.customer_id);
      localStorage.setItem('isAdmin', 'false');
      window.dispatchEvent(new Event('admin-status-changed'));
      alert("Demo login successful! (No database connection needed)");
      navigate('/profile');
      return;
    }

    // Regular customer login (requires database)
    api.get(`/customers?email=${email}`).then(res => {
      if(res.data.length && password === "password123") {
        // Store user data in localStorage
        const user = res.data[0];
        localStorage.setItem('loggedInUser', JSON.stringify(user));
        localStorage.setItem('userId', user.customer_id);
        localStorage.setItem('isAdmin', 'false');
        window.dispatchEvent(new Event('admin-status-changed'));
        alert("Login successful!");
        navigate('/profile'); // Redirect to profile
      } else {
        setError("Invalid credentials");
      }
    }).catch(err => {
      // If database is not connected, suggest demo mode
      if (err.code === 'ERR_NETWORK_ERROR' || err.message.includes('Network Error')) {
        setError("Database not connected. Use demo@user.com / demo123 for UI testing");
      } else {
        setError("Login failed");
      }
    });
  };

  const handleSignupChange = (e) => {
    setSignupForm(prev => ({ ...prev, [e.target.name]: e.target.value }));
    setSignupState({ loading: false, success: "", error: "" });
  };

  const handleInlineSignup = (e) => {
    e.preventDefault();
    
    // Validate passwords match
    if (signupForm.password !== signupForm.confirmPassword) {
      setSignupState({ loading: false, success: "", error: "Passwords do not match!" });
      return;
    }

    // Validate password length
    if (signupForm.password.length < 6) {
      setSignupState({ loading: false, success: "", error: "Password must be at least 6 characters long!" });
      return;
    }

    setSignupState({ loading: true, success: "", error: "" });

    const customerId = `CUS-${Date.now()}`;
    const payload = {
      customer_id: customerId,
      first_name: signupForm.firstName,
      last_name: signupForm.lastName,
      email: signupForm.email,
      postal_code: signupForm.address || null,
      club_member_status: signupForm.contact || null,
      signup_date: new Date().toISOString(),
      active: true,
      password: signupForm.password // Store password (backend may need to hash this)
    };

    api.post("/customers", payload)
      .then(() => {
        setSignupState({ loading: false, success: "Account created successfully! You can now log in with your email and password.", error: "" });
        setSignupForm({ firstName: "", lastName: "", contact: "", email: "", password: "", confirmPassword: "", address: "" });
      })
      .catch(() => setSignupState({ loading: false, success: "", error: "Signup failed. Please try again." }));
  };

  return (
    <div className="p-6 max-w-md mx-auto">
      <h1 className="text-2xl font-bold mb-4">Login</h1>
      {error && <p className="text-red-600">{error}</p>}
      <form className="space-y-4" onSubmit={handleSubmit}>
        <input type="email" placeholder="Email" value={email} onChange={e=>setEmail(e.target.value)} className="w-full border p-2 rounded"/>
        <input type="password" placeholder="Password" value={password} onChange={e=>setPassword(e.target.value)} className="w-full border p-2 rounded"/>
        <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded w-full">Login</button>
      </form>
      <div className="mt-4 p-4 bg-gray-50 rounded-lg">
        <p className="text-sm font-semibold text-gray-700 mb-2">Sample Credentials:</p>
        <div className="text-xs text-gray-600 space-y-1">
          <p><strong>Admin:</strong> admin@admin.com / admin123</p>
          <p><strong>Demo User (No DB):</strong> demo@user.com / demo123</p>
          <p><strong>Customer (DB):</strong> Use any email from your database / password123</p>
          <p className="text-blue-600 mt-2 font-semibold">💡 Use demo@user.com to test UI without database!</p>
        </div>
      </div>

      <div className="mt-10 border-t pt-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-3">New to LAYR?</h2>
        <p className="text-sm text-gray-600 mb-4">Create your customer account by sharing a few quick details.</p>
        {signupState.error && <p className="text-sm text-red-600 mb-3">{signupState.error}</p>}
        {signupState.success && <p className="text-sm text-green-600 mb-3">{signupState.success}</p>}
        <form className="space-y-4" onSubmit={handleInlineSignup}>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <input
              name="firstName"
              placeholder="First Name *"
              value={signupForm.firstName}
              onChange={handleSignupChange}
              className="w-full border p-2 rounded"
              required
            />
            <input
              name="lastName"
              placeholder="Last Name *"
              value={signupForm.lastName}
              onChange={handleSignupChange}
              className="w-full border p-2 rounded"
              required
            />
          </div>
          <input
            name="contact"
            placeholder="Contact Number *"
            value={signupForm.contact}
            onChange={handleSignupChange}
            className="w-full border p-2 rounded"
            required
          />
          <input
            type="email"
            name="email"
            placeholder="Email *"
            value={signupForm.email}
            onChange={handleSignupChange}
            className="w-full border p-2 rounded"
            required
          />
          <input
            type="password"
            name="password"
            placeholder="Password * (min 6 characters)"
            value={signupForm.password}
            onChange={handleSignupChange}
            className="w-full border p-2 rounded"
            required
            minLength={6}
          />
          <input
            type="password"
            name="confirmPassword"
            placeholder="Confirm Password *"
            value={signupForm.confirmPassword}
            onChange={handleSignupChange}
            className="w-full border p-2 rounded"
            required
            minLength={6}
          />
          <textarea
            name="address"
            placeholder="Address"
            value={signupForm.address}
            onChange={handleSignupChange}
            rows={3}
            className="w-full border p-2 rounded"
          />
          <button
            type="submit"
            disabled={signupState.loading}
            className="bg-green-600 text-white px-4 py-2 rounded w-full disabled:opacity-50"
          >
            {signupState.loading ? "Submitting..." : "Sign Up"}
          </button>
        </form>
      </div>
    </div>
  );
}
