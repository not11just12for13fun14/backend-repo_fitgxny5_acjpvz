"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List

# Example schemas (replace with your own):

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# UGC Portfolio specific schemas

class Project(BaseModel):
    """
    Portfolio projects shown on the site
    Collection name: "project"
    """
    title: str = Field(..., description="Project title")
    description: Optional[str] = Field(None, description="Short project summary")
    image_url: Optional[HttpUrl] = Field(None, description="Thumbnail or cover image URL")
    demo_url: Optional[HttpUrl] = Field(None, description="Live demo link")
    source_url: Optional[HttpUrl] = Field(None, description="Source code link")
    author: Optional[str] = Field(None, description="Author or team name")
    tags: List[str] = Field(default_factory=list, description="List of tags")

class Submission(BaseModel):
    """
    User-submitted portfolio entries
    Collection name: "submission"
    """
    name: str = Field(..., description="Submitter name")
    title: str = Field(..., description="Submission title")
    description: Optional[str] = Field(None, description="Short description")
    link: Optional[HttpUrl] = Field(None, description="External or demo link")
    thumbnail: Optional[HttpUrl] = Field(None, description="Thumbnail image URL")
    tags: List[str] = Field(default_factory=list, description="Tags for filtering/search")

# Add your own schemas here:
# --------------------------------------------------

# Note: The Flames database viewer will automatically:
# 1. Read these schemas from GET /schema endpoint
# 2. Use them for document validation when creating/editing
# 3. Handle all database operations (CRUD) directly
# 4. You don't need to create any database endpoints!
