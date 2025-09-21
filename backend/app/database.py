"""
Database connection and session management for the backend.

This module defines the SQLAlchemy engine and session maker used
throughout the application. It reads the `DATABASE_URL` environment
variable to determine the connection string. When running locally
without a configured database, it defaults to a SQLite database
stored in `./dev.db`.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


# Read the database URL from the environment, falling back to a local
# SQLite database. On Render, this will be provided by the managed
# Postgres instance.
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./dev.db")

# When using SQLite we need to disable thread check. Postgres does not
# require special connect arguments.
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

# Create the SQLAlchemy engine and session factory
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for declarative models
Base = declarative_base()

def get_db():
    """Yield a database session for dependency injection in FastAPI.

    This helper function is used in FastAPI dependencies to provide a
    database session that is properly closed after the request completes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
