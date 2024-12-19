"""
Database configuration for the QTip application.

This module sets up the connection to the MySQL database using SQLAlchemy and Databases.

Attributes:
    DATABASE_URL (str): The connection string for the MySQL database.
    database (Database): An asynchronous database connection instance from the Databases library.
    engine (Engine): A SQLAlchemy engine for synchronous database operations.
    metadata (MetaData): Metadata instance used for defining and reflecting database schemas.

Usage:
    - `database`: Used for asynchronous operations, such as querying or inserting data.
    - `engine`: Used for synchronous database interactions or schema-related tasks.
"""

from databases import Database
from sqlalchemy import create_engine, MetaData

DATABASE_URL = "mysql+pymysql://root:123456@localhost:3306/qtip_schema"


database = Database(DATABASE_URL)
engine = create_engine(DATABASE_URL)
metadata = MetaData()
