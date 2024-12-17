from fastapi import FastAPI
from Qtip_fapi.database import database
from Qtip_fapi.routers import knowledgebase
import asyncio
import subprocess
import os

app = FastAPI()

# Include routers
app.include_router(knowledgebase.router)


@app.on_event("startup")
async def startup():
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
    await database.disconnect()

@app.get("/")
async def root():
    return {"message": "Welcome to FastAPI with MySQL"}
