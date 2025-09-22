"""
SQLAlchemy models defining the core data structures for Grafline Tracking.

Currently only a minimal `Order` model is defined to support the
drag‑and‑drop workflow. Additional models for customers, quotes and
invoices can be added as the project evolves.
"""

import datetime
import enum
from sqlalchemy import Column, Integer, String, Enum, DateTime

from .database import Base


class OrderStatus(str, enum.Enum):
    """Enumeration of the different states an order can be in.

    The string values here correspond to the canonical names used by
    the frontend when grouping orders into columns. They should not
    contain spaces or lower/upper case mismatches. If you change
    these values, update the frontend accordingly.
    """

    NEW = "NEW"
    IN_PROGRESS = "IN_PROGRESS"
    NEEDS_ATTENTION = "NEEDS_ATTENTION"
    READY_FOR_DELIVERY = "READY_FOR_DELIVERY"
    INVOICED = "INVOICED"


class Order(Base):
    """Represents an order flowing through the production pipeline."""

    __tablename__ = "orders"

    id: int = Column(Integer, primary_key=True, index=True)
    title: str = Column(String, index=True, nullable=False)
    details: str = Column(String, nullable=True)
    status: OrderStatus = Column(Enum(OrderStatus), default=OrderStatus.NEW, index=True)
    created_at: datetime.datetime = Column(
        DateTime, default=datetime.datetime.utcnow, nullable=False
    )
