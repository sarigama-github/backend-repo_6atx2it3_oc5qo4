"""
Database Schemas for the Gaming E‑commerce app

Each Pydantic model represents a MongoDB collection.
Collection name is the lowercase class name (e.g., Product -> "product").
"""

from pydantic import BaseModel, Field
from typing import Optional, List

class Product(BaseModel):
    """Products available for sale"""
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Short description")
    price: float = Field(..., ge=0, description="Price in USD")
    category: str = Field(..., description="Category, e.g., accessories, consoles, games")
    platform: Optional[str] = Field(None, description="Platform, e.g., PC, PS5, Xbox, Switch")
    in_stock: bool = Field(True, description="Whether product is currently in stock")
    image: Optional[str] = Field(None, description="Image URL")
    rating: Optional[float] = Field(4.5, ge=0, le=5, description="Average rating")

class OrderItem(BaseModel):
    product_id: str = Field(..., description="Referenced product _id as string")
    title: str = Field(..., description="Product title at time of purchase")
    price: float = Field(..., ge=0, description="Unit price at time of purchase")
    quantity: int = Field(..., ge=1, description="Quantity purchased")
    image: Optional[str] = None

class Order(BaseModel):
    """Orders placed by customers"""
    customer_name: str
    customer_email: str
    address: str
    items: List[OrderItem]
    subtotal: float = Field(..., ge=0)
    tax: float = Field(..., ge=0)
    total: float = Field(..., ge=0)
    status: str = Field("pending", description="Order status")
