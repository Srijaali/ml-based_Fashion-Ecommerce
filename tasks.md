


# 🔐 **TASK GROUP 1 — Fix Authentication/Authorization Across All Routers**

### **Task 1.1 — Ensure correct dependencies**

For every router:

* Admin routes must include:

```python
Depends(get_current_admin)
```

* Customer routes must include:

```python
Depends(get_current_customer)
```

* Public routes should have **no dependency** and **no security scheme**.

---

### **Task 1.2 — Apply proper security scheme to each route**

Each route must explicitly declare its security scheme using Swagger syntax:

Admin route:

```python
dependencies=[Depends(get_current_admin)],
tags=["Admin"], 
responses={401: {"description": "Unauthorized"}}
```

Customer route:

```python
dependencies=[Depends(get_current_customer)],
tags=["Customer"],
responses={401: {"description": "Unauthorized"}}
```

---

### **Task 1.3 — Remove invalid or old auth**

Remove ALL instances of:

* `OAuth2PasswordBearer`
* `oauth2_scheme`
* Any unused Bearer classes
* Duplicate or legacy auth utilities

Use only:

* `AdminBearerAuth`
* `CustomerBearerAuth`

---

# 🧠 **TASK GROUP 2 — Fix Specific Router Issues**

### **Task 2.1 — Orders Router**

Apply exact rules:

#### > Customer-only:

* create_order
* create_full_order
* update_order_address
* get_my_orders

#### > Admin-only:

* get_orders_for_customer
* update_order_status
* get_all_orders

---

### **Task 2.2 — Reviews Router**

* Creating, updating, deleting reviews → customer only
* Getting reviews for product → public

---

### **Task 2.3 — Cart Router**

* CRUD operations → customer only
* No admin should have access here

---

### **Task 2.4 — Wishlist Router**

* CRUD operations → customer only

---

### **Task 2.5 — Customer Router**

* signup / login → public
* update profile → customer only
* deactivate / delete → admin only
* get all customers → admin only

---

### **Task 2.6 — Articles Router**

* list articles → public
* filter/search articles → public
* create/update/delete articles → admin only

---

### **Task 2.7 — Categories Router**

* list → public
* create/update/delete → admin only

---

### **Task 2.8 — Events Router**

Internal event tracking:

* Record event → public (app-level) OR customer-only if tied to session
* Analytics endpoints → admin only

---

# 🧼 **TASK GROUP 3 — Code Cleanup**

### **Task 3.1 — Delete unused imports**

Remove any imports not required.

### **Task 3.2 — Remove duplicate endpoint definitions**

Ensure no endpoint is defined twice in any router.

### **Task 3.3 — Standardize router structure**

All routers must use this structure:

```
router = APIRouter(
    prefix="/xyz",
    tags=["XYZ"],
)
```

### **Task 3.4 — Ensure consistent ordering**

1. Imports
2. Router definition
3. Dependencies
4. Endpoints

---

# 📚 **TASK GROUP 4 — Swagger Documentation Fix**

### **Task 4.1 — Ensure lock icons appear correctly**

Add proper security for each route using:

Admin example:

```python
security=[{"AdminBearerAuth": []}]
```

Customer example:

```python
security=[{"CustomerBearerAuth": []}]
```

Public example:

```python
security=[]
```

---

### **Task 4.2 — Remove OAuth2 from swagger**

Ensure no OAuth2 schemes appear.

---

# 🧪 **TASK GROUP 5 — QA + Testing Checklist**

### **Task 5.1 — Test Customer Flow**

* Customer login → get token
* Access customer routes → success
* Access admin routes → 401

### **Task 5.2 — Test Admin Flow**

* Admin login → token
* Access admin routes → success
* Access customer routes → 401

### **Task 5.3 — Test Public Routes**

* Accessible with no token
* No auth prompts

---

# 🟩 **FINAL REQUIREMENT**

All tasks must be completed **without modifying model definitions, business logic, schemas, or database structure**.

Only authentication, dependencies, route protection, and code cleanup should be changed.

---