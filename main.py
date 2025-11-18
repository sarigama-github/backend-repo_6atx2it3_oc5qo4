import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bson import ObjectId
from typing import List, Optional

from database import db, create_document, get_documents
from schemas import Product, Order, OrderItem

app = FastAPI(title="Gaming E-commerce API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Gaming E-commerce Backend Running"}

# Util to convert Mongo docs

def serialize_doc(doc):
    if not doc:
        return doc
    d = dict(doc)
    if "_id" in d:
        d["id"] = str(d.pop("_id"))
    return d

@app.get("/api/products")
def list_products(category: Optional[str] = None, platform: Optional[str] = None, limit: int = 50):
    query = {}
    if category:
        query["category"] = category
    if platform:
        query["platform"] = platform
    try:
        docs = get_documents("product", query, limit)
        return [serialize_doc(doc) for doc in docs]
    except Exception as e:
        # Fallback demo data if DB isn't available
        demo = [
            {
                "id": "demo1",
                "title": "Pro Gaming Headset",
                "description": "7.1 surround, noise-cancel mic",
                "price": 89.99,
                "category": "accessories",
                "platform": "PC",
                "in_stock": True,
                "image": "https://images.unsplash.com/photo-1610962493842-6f681afe0102?q=80&w=1200&auto=format&fit=crop",
                "rating": 4.6,
            },
            {
                "id": "demo2",
                "title": "Mechanical Keyboard RGB",
                "description": "Hot-swappable, PBT keycaps",
                "price": 129.0,
                "category": "accessories",
                "platform": "PC",
                "in_stock": True,
                "image": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?q=80&w=1200&auto=format&fit=crop",
                "rating": 4.8,
            },
            {
                "id": "demo3",
                "title": "PS5 DualSense Controller",
                "description": "Haptic feedback, adaptive triggers",
                "price": 69.99,
                "category": "controllers",
                "platform": "PS5",
                "in_stock": True,
                "image": "https://images.unsplash.com/photo-1606811841689-23dfddce3e95?q=80&w=1200&auto=format&fit=crop",
                "rating": 4.7,
            },
        ]
        return demo

class CartItem(BaseModel):
    product_id: str
    title: str
    price: float
    quantity: int
    image: Optional[str] = None

class CheckoutRequest(BaseModel):
    name: str
    email: str
    address: str
    items: List[CartItem]

@app.post("/api/checkout")
def checkout(payload: CheckoutRequest):
    if not payload.items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    subtotal = sum(i.price * i.quantity for i in payload.items)
    tax = round(subtotal * 0.1, 2)
    total = round(subtotal + tax, 2)

    order_items = [
        OrderItem(
            product_id=i.product_id,
            title=i.title,
            price=i.price,
            quantity=i.quantity,
            image=i.image,
        )
        for i in payload.items
    ]

    order = Order(
        customer_name=payload.name,
        customer_email=payload.email,
        address=payload.address,
        items=order_items,
        subtotal=subtotal,
        tax=tax,
        total=total,
        status="pending",
    )

    try:
        order_id = create_document("order", order)
        return {"success": True, "order_id": order_id, "total": total}
    except Exception:
        # If DB not configured, still return simulated success
        return {"success": True, "order_id": "demo-order", "total": total}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        from database import db as _db
        if _db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = _db.name if hasattr(_db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = _db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
