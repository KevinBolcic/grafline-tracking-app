"""
Pydantic schemas for request and response bodies.

These schemas mirror the SQLAlchemy models but allow FastAPI to
perform validation and automatic documentation generation. They are
versioned separately from the models to allow more flexibility in
exposing or hiding fields from API consumers.
"""

import datetime
from pydantic import BaseModel
from typing import Optional

from .models import OrderStatus


class OrderBase(BaseModel):
    title: str
    details: Optional[str] = None


class OrderCreate(OrderBase):
    pass


class OrderUpdate(BaseModel):
    status: OrderStatus


class OrderRead(OrderBase):
    id: int
    status: OrderStatus
    created_at: datetime.datetime

    class Config:
        orm_mode = True
