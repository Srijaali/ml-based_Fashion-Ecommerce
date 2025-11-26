
---

# ✅ **auth_checklist.md — Authentication & Authorization Verification**

This checklist ensures every auth flow, token type, and protected route works correctly after implementing fixes.

---

# 🔐 **1. TOKEN GENERATION CHECKS**

## **1.1 — Admin Login**

* [ ] Call: `POST /admin/login`
* [ ] Should return:

  * **200 OK**
  * JSON containing:

    * `access_token`
    * `token_type: "bearer"`
    * `role: "admin"`
* [ ] Copy the returned token → save as `ADMIN_TOKEN`

## **1.2 — Customer Login**

* [ ] Call: `POST /customers/login`
* [ ] Should return:

  * **200 OK**
  * `access_token`
  * `token_type: "bearer"`
  * `role: "customer"`
* [ ] Copy token → save as `CUSTOMER_TOKEN`

---

# 🧪 **2. TOKEN VALIDATION CHECKS**

## **2.1 — Admin Token**

* [ ] Decode the token manually (JWT site or code)
* [ ] Must contain fields:

  * `sub` = admin_id
  * `role` = `"admin"`

## **2.2 — Customer Token**

* Same checks:

  * `sub` = customer_id
  * `role` = `"customer"`

---

# 🔒 **3. AUTHORIZATION CHECKS — ROUTE BY ROUTE**

This section ensures correct access control.

---

# **3.1 ORDERS ROUTER**

## **Customer-only**

Test these with CUSTOMER_TOKEN:

| Endpoint                     | Customer should | Admin should | Public should |
| ---------------------------- | --------------- | ------------ | ------------- |
| POST /orders                 | ✔ allowed       | ❌ 401        | ❌             |
| POST /orders/full            | ✔               | ❌            | ❌             |
| PATCH /orders/update-address | ✔               | ❌            | ❌             |
| GET /orders/my               | ✔               | ❌            | ❌             |

## **Admin-only**

Test with ADMIN_TOKEN:

| Endpoint                  | Admin should | Customer | Public |
| ------------------------- | ------------ | -------- | ------ |
| GET /orders/all           | ✔            | ❌        | ❌      |
| GET /orders/customer/{id} | ✔            | ❌        | ❌      |
| PATCH /orders/status      | ✔            | ❌        | ❌      |

---

# **3.2 REVIEWS ROUTER**

| Endpoint                  | Public | Customer | Admin                         |
| ------------------------- | ------ | -------- | ----------------------------- |
| GET /reviews/article/{id} | ✔      | ✔        | ✔                             |
| POST /reviews             | ❌      | ✔        | ❌                             |
| PATCH /reviews/{id}       | ❌      | ✔        | ✔ *(optional admin override)* |
| DELETE /reviews/{id}      | ❌      | ✔        | ✔ *(optional admin override)* |

---

# **3.3 CART ROUTER**

| Endpoint           | Customer | Admin | Public |
| ------------------ | -------- | ----- | ------ |
| POST /cart         | ✔        | ❌     | ❌      |
| GET /cart/my       | ✔        | ❌     | ❌      |
| PATCH /cart/update | ✔        | ❌     | ❌      |
| DELETE /cart/{id}  | ✔        | ❌     | ❌      |

---

# **3.4 WISHLIST ROUTER**

Customer only:

* [ ] add to wishlist
* [ ] get wishlist
* [ ] remove

Admin/public should **always fail**.

---

# **3.5 CUSTOMER ROUTER**

| Endpoint                | Public | Customer | Admin |
| ----------------------- | ------ | -------- | ----- |
| POST /customers/signup  | ✔      | ✔        | ✔     |
| POST /customers/login   | ✔      | ✔        | ✔     |
| GET /customers/me       | ❌      | ✔        | ❌     |
| PATCH /customers/update | ❌      | ✔        | ❌     |
| GET /customers/all      | ❌      | ❌        | ✔     |
| DELETE /customers/{id}  | ❌      | ❌        | ✔     |

---

# **3.6 ARTICLES ROUTER**

| Endpoint              | Public | Customer | Admin |
| --------------------- | ------ | -------- | ----- |
| GET /articles         | ✔      | ✔        | ✔     |
| GET /articles/search  | ✔      | ✔        | ✔     |
| POST /articles/create | ❌      | ❌        | ✔     |
| PATCH /articles/{id}  | ❌      | ❌        | ✔     |
| DELETE /articles/{id} | ❌      | ❌        | ✔     |

---

# **3.7 CATEGORIES ROUTER**

* Public:

  * GET all categories
  * GET category tree

* Admin ONLY:

  * POST create
  * PATCH update
  * DELETE remove

---

# **3.8 EVENTS ROUTER**

| Endpoint              | Public                                          | Customer | Admin |
| --------------------- | ----------------------------------------------- | -------- | ----- |
| POST /events/record   | ✔ or customer-only (depending on session model) | ✔        | ✔     |
| GET /events/analytics | ❌                                               | ❌        | ✔     |

---

# 🧹 **4. TOKEN ERROR CASES**

Test these:

## **4.1 No token**

* [ ] Calling any protected route → must return:

  * **401 Unauthorized**
  * message: `"Not authenticated"`

## **4.2 Wrong token type**

Example: Customer uses admin-only route

* [ ] Must return:

  * **401 Unauthorized**
  * `"Admin privileges required"`

## **4.3 Expired token**

Manually modify expiration → test

* [ ] Should reject with:

  * `"Token expired"`

---

# 🧼 **5. INTERNAL CODE CHECKS**

* [ ] No OAuth2 schemes left
* [ ] No old unused Bearer classes
* [ ] All routers now use:

  * `Depends(get_current_admin)`
  * `Depends(get_current_customer)`
* [ ] Swagger shows correct lock icons
* [ ] Public routes show NO lock

---

# 🟢 **If everything checks out → AUTH IS FULLY CORRECT**

Let me know if you want:

✔ A Postman collection with all these tests
✔ A pytest suite auto-generated for these auth flows
✔ A monitoring dashboard for auth failures