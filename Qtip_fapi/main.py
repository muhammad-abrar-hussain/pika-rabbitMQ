"""
Main FastAPI application file for the QTip project.

This file initializes the FastAPI app, sets up the database connection, and starts a RabbitMQ consumer.
It also handles application startup and shutdown events, ensuring proper resource management.

Modules and Features:
- Includes FastAPI routers for handling specific API endpoints (knowledgebase and Question).
- Connects to the database on application startup and disconnects on shutdown.
- Starts the RabbitMQ consumer process for message handling.

Attributes:
    app (FastAPI): The FastAPI application instance.

Endpoints:
    - GET `/`: A root endpoint to test if the app is running, returning a welcome message.

Event Handlers:
    - `startup`: Establishes the database connection and starts the RabbitMQ consumer on application startup.
    - `shutdown`: Closes the database connection when the server shuts down.

Usage:
    Run this file to start the FastAPI application and initialize required services (database and RabbitMQ).
"""


from fastapi import FastAPI
from Qtip_fapi.database import database
from Qtip_fapi.routers import knowledgebase
from Qtip_fapi.routers import Question
import asyncio
import subprocess
import os

app = FastAPI()

app.include_router(knowledgebase.router)
app.include_router(Question.router)


@app.on_event("startup")
async def startup():
    """Made connection with db on app start.

    & starting rabbitMQ consumer.
"""
    try:
        await database.connect()
        print("Database connected successfully.")
    except Exception as e:
        print(f"Database connection failed: {e}")

    # Start RabbitMQ consumer
    loop = asyncio.get_event_loop()
    receiver_path = os.path.join(os.path.dirname(__file__), "receiver.py")
    loop.run_in_executor(None, subprocess.run, ["python", receiver_path])


@app.on_event("shutdown")
async def shutdown():
    """To close connection with db."""
    await database.disconnect()


@app.get("/")
async def root():
    """/,endpoint to test app."""
    return {"message": "Welcome to FastAPI with MySQL"}
