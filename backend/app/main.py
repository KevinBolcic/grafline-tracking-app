"""
Main entry point for the Grafline Tracking API.

This FastAPI application exposes endpoints for listing, creating and
updating orders. It also sets up CORS to allow requests from the
frontend origin. Additional routers (customers, quotes, invoices)
can be added as the project expands.
"""

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .database import get_db, engine
from .models import Base, Order, OrderStatus
from .schemas import OrderCreate, OrderRead, OrderUpdate


# Create all tables if they do not exist
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Grafline Tracking API")

# Allow all origins for simplicity. In production you may wish to restrict this.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/orders", response_model=list[OrderRead])
def list_orders(db: Session = Depends(get_db)):
    """Return all orders in the system."""
    return db.query(Order).order_by(Order.created_at.desc()).all()


@app.post("/orders", response_model=OrderRead, status_code=201)
def create_order(order_in: OrderCreate, db: Session = Depends(get_db)):
    """Create a new order given a title and details."""
    order = Order(title=order_in.title, details=order_in.details, status=OrderStatus.NEW)
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


@app.put("/orders/{order_id}", response_model=OrderRead)
def update_order(order_id: int, order_update: OrderUpdate, db: Session = Depends(get_db)):
    """Update the status of an existing order."""
    order = db.get(Order, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    order.status = order_update.status
    db.commit()
    db.refresh(order)
    return order


@app.get("/healthz")
def health_check():
    """Simple health check endpoint for Render."""
    return {"status": "ok"}
