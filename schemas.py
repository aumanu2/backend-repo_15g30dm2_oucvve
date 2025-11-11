"""
Database Schemas for cutConnect

Each Pydantic model below represents a MongoDB collection. The collection name
is the lowercase of the class name (e.g., Barber -> "barber").

These schemas validate data for barbers, their services/portfolio, clients, and
appointments (in-store or at-home).
"""
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Literal
from datetime import datetime

# -----------------------------
# EMBEDDED MODELS
# -----------------------------
class Service(BaseModel):
    name: str = Field(..., description="Service name, e.g., 'Fade', 'Beard Trim'")
    duration_minutes: int = Field(..., ge=5, le=600, description="Estimated duration")
    price: float = Field(..., ge=0, description="Price in USD")
    description: Optional[str] = Field(None, description="Service details")

class PortfolioItem(BaseModel):
    image_url: str = Field(..., description="Public image URL of the work")
    caption: Optional[str] = Field(None, description="Short caption/notes")

class Location(BaseModel):
    type: Literal["in_store", "at_home"] = Field(..., description="Appointment type")
    address: Optional[str] = Field(None, description="Required when type is at_home")

# -----------------------------
# TOP-LEVEL COLLECTIONS
# -----------------------------
class Barber(BaseModel):
    name: str = Field(..., description="Barber's display name")
    bio: Optional[str] = Field(None, description="Short bio/about")
    avatar_url: Optional[str] = Field(None, description="Profile image URL")
    shop_name: Optional[str] = Field(None, description="Shop name if applicable")
    shop_address: Optional[str] = Field(None, description="Shop address if in-store offered")
    services: List[Service] = Field(default_factory=list, description="Services offered")
    portfolio: List[PortfolioItem] = Field(default_factory=list, description="Portfolio items")
    rating: Optional[float] = Field(0, ge=0, le=5, description="Average rating")

class Client(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None

class Appointment(BaseModel):
    barber_id: str = Field(..., description="Associated barber _id as string")
    client: Client
    service_name: str = Field(..., description="Name of selected service")
    start_time: datetime = Field(..., description="Appointment start in ISO 8601")
    location: Location
    notes: Optional[str] = None
    status: Literal["pending", "confirmed", "cancelled"] = "pending"
