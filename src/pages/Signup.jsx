import { useState } from "react";
import { api } from "../api/api";

export default function Signup() {
  const [form, setForm] = useState({ 
    first_name: "", 
    last_name: "", 
    email: "",
    gender: ""
  });

  const handleChange = e => 
    setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = e => {
    e.preventDefault();
    api.post("/customers", { ...form, signup_date: new Date() })
      .then(() => alert("Signup successful!"))
      .catch(err => console.error(err));
  };

  return (
    <div className="p-6 max-w-md mx-auto">
      <h1 className="text-2xl font-bold mb-4">Signup</h1>
      <form className="space-y-4" onSubmit={handleSubmit}>
        <input
          name="first_name"
          placeholder="First Name"
          value={form.first_name}
          onChange={handleChange}
          className="w-full border p-2 rounded"
        />

        <input
          name="last_name"
          placeholder="Last Name"
          value={form.last_name}
          onChange={handleChange}
          className="w-full border p-2 rounded"
        />

        {/* Gender dropdown */}
        <select
          name="gender"
          value={form.gender}
          onChange={handleChange}
          className="w-full border p-2 rounded"
        >
          <option value="">Select Gender</option>
          <option value="Female">Female</option>
          <option value="Male">Male</option>
        </select>

        <input
          name="email"
          placeholder="Email"
          value={form.email}
          onChange={handleChange}
          className="w-full border p-2 rounded"
        />

        <button 
          type="submit" 
          className="bg-green-600 text-white px-4 py-2 rounded"
        >
          Signup
        </button>
      </form>
    </div>
  );
}
