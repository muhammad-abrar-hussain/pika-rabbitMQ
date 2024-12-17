from fastapi import FastAPI
from Qtip_ai.database import database
from Qtip_ai.routers import knowledgebase
import asyncio
import subprocess
app = FastAPI()


# Include routers
app.include_router(knowledgebase.router)

@app.on_event("startup")
async def startup():
    await database.connect()

    # Start RabbitMQ consumer
    loop = asyncio.get_event_loop()
    loop.run_in_executor(None, subprocess.run, ["python", "rabbitMQ/receiver.py"])

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.get("/")
async def root():
    return {"message": "Welcome to FastAPI with MySQL"}








