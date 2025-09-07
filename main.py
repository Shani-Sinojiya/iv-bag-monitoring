from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from pydantic import BaseModel
from typing import Optional
import json
from fastapi import WebSocket, WebSocketDisconnect
from contextlib import asynccontextmanager
import config

# Data models


class SensorData(BaseModel):
    weight: int


class WeightRecord(BaseModel):
    weight: int
    timestamp: datetime


# Global variables
mongodb_client = None
database = None
collection = None
connected_websockets = []

# Configuration from simplified config
MONGODB_URL = config.MONGODB_URL
DATABASE_NAME = config.DATABASE_NAME
COLLECTION_NAME = config.COLLECTION_NAME
WEIGHT_THRESHOLD = config.WEIGHT_THRESHOLD_MIN


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global mongodb_client, database, collection
    try:
        mongodb_client = AsyncIOMotorClient(MONGODB_URL)
        database = mongodb_client[DATABASE_NAME]
        collection = database[COLLECTION_NAME]

        # Test connection
        await mongodb_client.admin.command('ping')
        print("Connected to MongoDB successfully!")

        # Create index on timestamp for better query performance
        await collection.create_index("timestamp")

    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
        print("Please ensure MongoDB is running on localhost:27017")

    yield

    # Shutdown
    if mongodb_client:
        mongodb_client.close()

# Create FastAPI app
app = FastAPI(
    title="IoT IV Bag Monitoring System",
    description="Real-time weight monitoring system for IV bags",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# WebSocket connection manager


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                disconnected.append(connection)

        # Remove disconnected websockets
        for connection in disconnected:
            if connection in self.active_connections:
                self.active_connections.remove(connection)


manager = ConnectionManager()

# Helper functions


async def get_latest_weight() -> Optional[WeightRecord]:
    """Get the most recent weight record from database"""
    if collection is None:
        return None

    try:
        latest = await collection.find_one(
            {},
            sort=[("timestamp", -1)]
        )
        if latest:
            return WeightRecord(
                weight=latest["weight"],
                timestamp=latest["timestamp"]
            )
        return None
    except Exception as e:
        print(f"Error fetching latest weight: {e}")
        return None


async def should_insert_record(new_weight: int) -> bool:
    """Check if we should insert a new record (only if weight changed)"""
    latest = await get_latest_weight()
    if not latest:
        return True
    return latest.weight != new_weight


async def insert_weight_record(weight: int) -> WeightRecord:
    """Insert a new weight record into database"""
    if collection is None:
        raise HTTPException(
            status_code=500, detail="Database connection not available")

    record = {
        "weight": weight,
        "timestamp": datetime.utcnow()
    }

    try:
        await collection.insert_one(record)
        return WeightRecord(**record)
    except Exception as e:
        print(f"Error inserting weight record: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to insert weight record")

# API Routes


@app.post("/sensor")
async def receive_sensor_data(sensor_data: SensorData):
    """Receive sensor data from IoT device"""
    try:
        # Only insert if weight has changed
        if await should_insert_record(sensor_data.weight):
            record = await insert_weight_record(sensor_data.weight)

            # Broadcast to all connected WebSocket clients
            message = json.dumps({
                "weight": record.weight,
                "timestamp": record.timestamp.isoformat(),
                "alert": record.weight < WEIGHT_THRESHOLD
            })
            await manager.broadcast(message)

            return {
                "status": "success",
                "message": "Weight recorded",
                "data": record
            }
        else:
            return {
                "status": "ignored",
                "message": "Weight unchanged, not recorded"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/latest")
async def get_latest():
    """Get the most recent weight data"""
    latest = await get_latest_weight()
    if not latest:
        raise HTTPException(status_code=404, detail="No weight data found")

    return {
        "weight": latest.weight,
        "timestamp": latest.timestamp.isoformat(),
        "alert": latest.weight < WEIGHT_THRESHOLD
    }


@app.get("/live", response_class=HTMLResponse)
async def live_dashboard(request: Request):
    """Serve the live dashboard webpage"""
    return templates.TemplateResponse("live.html", {
        "request": request,
        "threshold": WEIGHT_THRESHOLD
    })


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)

    # Send current weight immediately on connection
    try:
        latest = await get_latest_weight()
        if latest:
            message = json.dumps({
                "weight": latest.weight,
                "timestamp": latest.timestamp.isoformat(),
                "alert": latest.weight < WEIGHT_THRESHOLD
            })
            await manager.send_personal_message(message, websocket)
    except Exception as e:
        print(f"Error sending initial data: {e}")

    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.get("/")
async def root():
    """Root endpoint with basic information"""
    return {
        "message": "IoT IV Bag Monitoring System",
        "endpoints": {
            "sensor_data": "/sensor (POST)",
            "latest_weight": "/latest (GET)",
            "live_dashboard": "/live (GET)",
            "websocket": "/ws"
        }
    }

# Health check endpoint


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    db_status = "disconnected"
    db_error = None

    try:
        if mongodb_client is not None:
            # Test the connection
            await mongodb_client.admin.command('ping')
            db_status = "connected"
        else:
            db_error = "MongoDB client not initialized"
    except Exception as e:
        db_error = str(e)

    return {
        "status": "healthy",
        "database": db_status,
        "database_error": db_error,
        "threshold": WEIGHT_THRESHOLD,
        "collection_available": collection is not None
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.DEBUG
    )
