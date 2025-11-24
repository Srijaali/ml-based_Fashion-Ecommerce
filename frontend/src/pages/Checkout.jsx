import { useState } from "react";
import { api } from "../api/api";

export default function Checkout() {
  const [form, setForm] = useState({ name:"", address:"", city:"", postal:"" });
  const [success, setSuccess] = useState(false);

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = (e) => {
    e.preventDefault();
    // Simulate order creation
    api.post("/orders", {
      customer_id: "C101",
      order_date: new Date(),
      total_amount: 100,
      shipping_address: `${form.address}, ${form.city}, ${form.postal}`
    })
    .then(() => setSuccess(true))
    .catch(err => console.error(err));
  };

  if(success) return <p className="p-6 text-green-600 font-bold">Order placed successfully!</p>

  return (
    <div className="p-6 max-w-md">
      <h1 className="text-2xl font-bold mb-4">Checkout</h1>
      <form className="space-y-4" onSubmit={handleSubmit}>
        <input name="name" placeholder="Full Name" value={form.name} onChange={handleChange} className="w-full border p-2 rounded"/>
        <input name="address" placeholder="Address" value={form.address} onChange={handleChange} className="w-full border p-2 rounded"/>
        <input name="city" placeholder="City" value={form.city} onChange={handleChange} className="w-full border p-2 rounded"/>
        <input name="postal" placeholder="Postal Code" value={form.postal} onChange={handleChange} className="w-full border p-2 rounded"/>
        <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded">Place Order</button>
      </form>
    </div>
  );
}
