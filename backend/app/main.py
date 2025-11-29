from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.staticfiles import StaticFiles
import os

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
    sections,
    transactions,
    wishlist,
    cart,
)
from app.customer_auth import router as customer_auth_router


app = FastAPI(
    title="LAYR API",
    description="FastAPI backend for e-commerce project",
    version="1.0.0"
)

# ---- CORS ----
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# ---- Static Files ----
# Serve filtered_images directory at /images endpoint
filtered_images_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "filtered_images")
if os.path.exists(filtered_images_path):
    app.mount("/images", StaticFiles(directory=filtered_images_path), name="images")

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
app.include_router(sections.router, prefix="/sections", tags=["Sections"])

# ---- Root ----
@app.get("/")
def root():
    return {"message": "Welcome to the LAYR E-Commerce API"}


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="E-Commerce API",
        version="1.0.0",
        description="E-Commerce Database Project API",
        routes=app.routes,
    )

    # Forcefully wipe ALL existing security schemes
    openapi_schema["components"]["securitySchemes"] = {}

    # Insert ONLY our scheme
    openapi_schema["components"]["securitySchemes"]["BearerAuth"] = {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
        "description": "Paste your JWT token from /admins/login or /customers/auth/login"
    }

    # Apply BearerAuth globally
    for path, path_item in openapi_schema["paths"].items():
        for method in path_item:
            if method in ["get", "post", "put", "delete", "patch"]:
                if "security" not in path_item[method]:
                    path_item[method]["security"] = [{"BearerAuth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema