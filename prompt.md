

# 🧠 **PROJECT PROMPT FOR CURSOR**

You are assisting in the backend development of a **FastAPI + PostgreSQL** e-commerce/ML system.

Your primary responsibilities:

---

# 🎯 **MAIN GOAL**

**Fix authentication + authorization inconsistencies across all routers**
— without rewriting working logic or touching any unrelated code.

---

# 🛑 **DO NOT DO THE FOLLOWING**

You must NOT modify:

❌ Database schema
❌ SQL files
❌ Models/Pydantic schemas
❌ Working business logic
❌ Existing authentication logic
❌ Admin or customer password hashing
❌ JWT utility functions
❌ Anything in ML pipeline
❌ Anything in the frontend

**Focus ONLY on security, route protection, and cleanup of auth dependencies.**

---

# 🔐 **AUTH SYSTEM RULES (Must Implement)**

### Use these two dependencies only:

```python
get_current_admin
get_current_customer
```

### Use these two security schemes only:

* `AdminBearerAuth` → For admin routes
* `CustomerBearerAuth` → For customer routes

Do **NOT** use `OAuth2PasswordBearer` anywhere.

---

# 🔐 **RBAC RULES — APPLY THESE EXACTLY**

### ✅ Admin-only routes

(Use `Depends(get_current_admin)` + AdminBearerAuth)

* Admin CRUD
* Article CRUD
* Category CRUD
* Customer activate/deactivate/delete
* Access ANY user’s order data
* Update ANY order status
* Delete transactions (if enabled)
* View all orders, analytics, reports

### ✅ Customer-only routes

(Use `Depends(get_current_customer)` + CustomerBearerAuth)

* Create order
* Create full order
* Update address for their own order
* Get *their* orders
* Cart CRUD
* Wishlist CRUD
* Reviews (create/update/delete)
* Profile update

### 🟢 Public routes

(No auth needed)

* Customer signup
* Customer login
* Articles list
* Categories list

---

# ⚙️ **WHAT CURSOR MUST FIX**

Apply the following changes across all routers:

### **1. Add missing authorization dependencies**

If a route requires admin → add

```python
Depends(get_current_admin)
```

If a route requires customer → add

```python
Depends(get_current_customer)
```

### **2. Clean up Swagger documentation**

* Assign correct security scheme (`AdminBearerAuth` or `CustomerBearerAuth`)
* Ensure lock icons appear correctly
* Remove OAuth-based schemes if they exist

### **3. Correct permission logic in Orders router**

Make these **customer-only**:

* create_order
* create_full_order
* update_order_address
* get_my_orders

Make these **admin-only**:

* get_orders_for_customer
* update_order_status

### **4. Clean duplicates + unify pattern**

Ensure:

* All routers use consistent dependency imports
* No old/unused dependencies remain
* No mixed auth patterns

---

# 🧼 **CLEANUP RULES**

Cursor must ensure:

* Consistent import structure
* No duplicate functions
* No unreachable/unused code
* No leftover OAuth dependencies
* No accidental renaming or refactoring of valid code

---

# 📌 When unsure:

If a route relates to **system management**, it is admin-only.
If a route relates to **a personal action by customer**, it is customer-only.
If the route is for **public browsing**, it is public.

---

# 🧪 Testing Requirements (Auto by Cursor)

Cursor must ensure after changes:

* Admin routes correctly 401/403 for customers
* Customer routes correctly 401/403 for admins
* Public routes are accessible
* Swagger security icons appear correctly
* Token decoding still works

---

# 🟩 FINAL REMINDER FOR CURSOR

**Do not change business logic.
Do not modify models.
Do not alter database schema.
Only fix authorization + route protection.**