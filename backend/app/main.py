from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from app.db.database import Base, engine
from app.routers import admins, articles, cart, categories, customers, events, order_items, orders, reviews, sections, transactions, wishlist
from app.customer_auth import router as customer_auth_router


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
app.include_router(admins.router)  # Router already has /admins prefix defined
app.include_router(customer_auth_router)  # Customer auth routes (already has /customers/auth prefix)
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
app.include_router(sections.router)  # sections router already has /sections prefix

# ---- Root ----
@app.get("/")
def root():
    return {"message": "Welcome to the LAYR E-Commerce API"}


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    security_schemes = openapi_schema.setdefault("components", {}).setdefault("securitySchemes", {})
    security_schemes.setdefault(
        "AdminToken",
        {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Admin JWT generated via /admins/login",
        },
    )
    security_schemes.setdefault(
        "CustomerToken",
        {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Customer JWT generated via /customers/auth/login",
        },
    )

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
