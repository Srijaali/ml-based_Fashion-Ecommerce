

# 📌 Project Context — ML + DB E-commerce System (FAST API + PostgreSQL)

This project is a **full-stack ML + DB e-commerce platform** built on:

* **Frontend:** React / your frontend team
* **Backend:** FastAPI
* **Database:** PostgreSQL
* **ML:** Recommendors, Forecasting, NLP, Segmentation (future phase)

This document defines the backend structure, existing implementations, auth logic, and requirements to ensure Cursor does not rewrite completed work.

---

# 🔐 Authentication & Authorization Overview

Authentication for **Admins** and **Customers** is already implemented and working.
JWT tokens are used via **HTTPBearer**, *not OAuth2PasswordBearer*.

### ✔ Completed Authentication Features

### **Admin Auth — DONE**

* Admin login (using `crypt()` for password)
* Admin identity route `/admins/me`
* Admin CRUD (create, update, delete, list)
* Admin activity logs
* Admin password change
* Admin permissions enforced on most admin routes

### **Customer Auth — doing
* Customer signup
* Customer login (JWT)
* Customer profile update
* Customer identity via `/customers/me`

### ✔ Middleware & utilities

* JWT utilities for both customer & admin implemented
* Token decoding validated
* Password hashing via PostgreSQL `crypt()` for admin
* Customer password hashing implemented (likely Python hashing)

---

# 🗄 Database Tables (Final & Confirmed)

### Customers

* customer_id (PK)
* age
* postal_code
* club_member_status
* fashion_news_frequency
* active
* first_name
* last_name
* email
* signup_date

### Articles

* article_id (PK)
* product_code
* prod_name
* product_type_name
* product_group_name
* graphical_appearance_name
* colour_group_name
* department_no
* department_name
* index_name
* index_group_name
* section_name
* garment_group_name
* detail_desc
* price
* stock
* category_id (FK)
* created_at
* last_updated

### Transactions

* transaction_id (PK)
* t_dat
* customer_id (FK)
* article_id (FK)
* price
* sales_channel_id

### Categories

* category_id (PK)
* name
* parent_category_id (self-FK)

### Orders

* order_id
* customer_id (FK)
* order_date
* total_amount
* payment_status
* shipping_address

### Order Items

* order_item_id
* order_id (FK)
* article_id (FK)
* quantity
* unit_price
* line_total

### Reviews

* review_id
* customer_id (FK)
* article_id (FK)
* rating
* review_text
* created_at

### Events

* event_id
* session_id
* customer_id
* article_id
* event_type
* campaign_id
* created_at

### Cart

* cart_id
* customer_id
* article_id
* quantity
* added_at

### Wishlist

* wishlist_id
* customer_id
* article_id
* added_at

---

# 🔐 Role-based Access Control (RBAC)

## ✔ Admin-only endpoints (MUST require `get_current_admin`)

* Article CRUD
* Category CRUD
* Customer activate/deactivate/delete
* Get orders for any customer
* Update order status
* Possibly: delete transactions

## ✔ Customer-only endpoints (MUST require `get_current_customer`)

* Create order
* Create full order
* Update order address (ONLY their own order)
* Get my orders
* Wishlist CRUD
* Cart CRUD
* Reviews create/update/delete
* Their profile update

## ✔ Public endpoints (NO dependency)

* Customer signup
* Customer login
* Articles list / browse
* Categories list

---

# ❗ Remaining Backend Tasks (To be fixed by Cursor)

Cursor should complete ONLY these tasks:

### **1. Fix inconsistent route protection**

Some routes show a lock in Swagger but lack actual `Depends()`.

Required:

* Add `Depends(get_current_admin)` to all admin routes
* Add `Depends(get_current_customer)` to all customer routes
* Ensure public routes remain public

### **2. Fix Orders router permissions**

Customer-only:

* create_order
* create_full_order
* update_order_address
* get_my_orders

Admin-only:

* get_orders_for_customer
* update_order_status

### **3. Fix Swagger security schemes**

* Remove OAuth2PasswordBearer (if present)
* Use ONLY `HTTPBearer`
* Define two schemes:

  * `AdminBearerAuth`
  * `CustomerBearerAuth`
* Assign correct scheme to each route

### **4. Fix transaction deletion permissions**

* Decide if delete transaction is admin-only
* Or limit by ownership (likely admin-only)

### **5. Clean up duplicate/inconsistent dependencies across routers**

### ❗ Cursor must NOT modify:

* Database schema
* SQL triggers
* Model definitions
* Already working business logic
* Authentication implementation

Cursor must only enforce proper authorization and cleanup security dependencies.

---

# 📦 ML Phase Context (For later)

(Not part of immediate backend work)

ML features planned:

* Hybrid recommendation system
* Time series forecasting on transactions
* NLP sentiment analysis on reviews
* Trend insights
* Customer segmentation
* Advanced features if time allows

---

# ✅ Summary for Cursor

Your job is to **fix and unify authentication + route protection** ONLY.

Use:

* `get_current_admin` for admin routes
* `get_current_customer` for customer routes
* Clean HTTPBearer security schemes
* Fix Swagger lock icons
* Update Orders router permission rules
* Do NOT change models, schemas, or DB.

---