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

import sys
import os

# Add the 'packages' folder to the system path
sys.path.append(os.path.join(os.path.dirname(__file__), 'packages'))

from databases import Database
from sqlalchemy import create_engine, MetaData

DATABASE_URL = "mysql+pymysql://root:123456@localhost:3306/qtip_schema"

database = Database(DATABASE_URL)
engine = create_engine(DATABASE_URL)
metadata = MetaData()


async def db_fetch_files(presentation_id):
    query = """
    SELECT filepath
    FROM QTip_Api_presentationknowledgebase
    WHERE presentation_id = REPLACE(:presentation_id, '-', '')
    """
    rows = await database.fetch_all(query,
                                    {"presentation_id": presentation_id})
    if not rows:
        raise Exception("No files found for the given presentation ID.")

    files = [dict(row) for row in rows]
    return {"files": files}

async def db_save_topics(topics, presentation_id):
    try:
        query = """
                    INSERT INTO QTip_Api_aigeneratedtopic
                    (uuid, presenter_id, presentation_id, title, summary, open_ai_request_completion_id)
                    VALUES (
                        REPLACE(UUID(), '-', ''),
                        REPLACE(:presenter_id, '-', ''),
                        REPLACE(:presentation_id, '-', ''),
                        :title,
                        :summary,
                        :open_ai_request_completion_id
                    )
                """
        values = {
            "presenter_id": str(topic.presenter_id),
            "presentation_id": str(topic.presentation_id),
            "title": topic.title,
            "summary": topic.summary,
            "open_ai_request_completion_id": topic.open_ai_request_completion_id,
        }
        await database.execute(query=query, values=values)

        return {"message": "AI-generated topic successfully created."}
