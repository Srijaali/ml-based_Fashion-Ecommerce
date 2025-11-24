from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.database import Base, engine
from app.routers import (
    admins,
    articles,
    categories,
    customers,
    events,
    orders,
    order_items,
    reviews,
    transactions,
    wishlist,
    cart,
)

app = FastAPI(
    title="LAYR API",
    description="FastAPI backend for e-commerce project",
    version="1.0.0"
)

# ---- CORS ----
origins = ["*"]  # change to specific frontend domains later
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Create tables on startup ----
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


# ---- Register Routers ---
app.include_router(admins.router, prefix="/admins",tags=['Admins'])
app.include_router(articles.router, prefix="/articles", tags=["Articles"])
app.include_router(categories.router, prefix="/categories", tags=["Categories"])
app.include_router(customers.router, prefix="/customers", tags=["Customers"])
app.include_router(events.router, prefix="/events", tags=["Events"])
app.include_router(orders.router, prefix="/orders", tags=["Orders"])
app.include_router(order_items.router, prefix="/order-items", tags=["Order Items"])
app.include_router(reviews.router, prefix="/reviews", tags=["Reviews"])
app.include_router(transactions.router, prefix="/transactions", tags=["Transactions"])
app.include_router(wishlist.router, prefix="/wishlist", tags=["Wishlist"])
app.include_router(cart.router, prefix="/cart", tags=["Cart"])

# ---- Root ----
@app.get("/")
def root():
    return {"message": "Welcome to the LAYR E-Commerce API"}
