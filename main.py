from fastapi import FastAPI, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
import json

from database import engine, get_db, Base
from models import DeviceSnapshot

Base.metadata.create_all(bind=engine)

app = FastAPI(title="PhoneDash API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, data: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(data)
            except:
                pass

manager = ConnectionManager()

class DataPayload(BaseModel):
    timestamp: str
    battery_level: Optional[float] = -1
    battery_state: Optional[str] = "unknown"
    device_model: Optional[str] = "unknown"
    system_version: Optional[str] = "unknown"
    device_name: Optional[str] = "unknown"
    orientation: Optional[str] = "unknown"
    latitude: Optional[float] = 0
    longitude: Optional[float] = 0
    accel_x: Optional[float] = 0
    accel_y: Optional[float] = 0
    accel_z: Optional[float] = 0
    gyro_alpha: Optional[float] = 0
    gyro_beta: Optional[float] = 0
    gyro_gamma: Optional[float] = 0
    network_type: Optional[str] = "unknown"
    speed_mbps: Optional[float] = 0

@app.post("/api/data")
async def receive_data(payload: DataPayload, db: Session = Depends(get_db)):
    snap = DeviceSnapshot(**payload.dict())
    db.add(snap)
    db.commit()
    # Broadcast to all connected dashboard clients
    await manager.broadcast(payload.dict())
    return {"status": "ok"}

@app.get("/api/latest")
def get_latest(db: Session = Depends(get_db)):
    snap = db.query(DeviceSnapshot).order_by(DeviceSnapshot.id.desc()).first()
    if not snap:
        return {}
    return snap.__dict__

@app.get("/api/history")
def get_history(limit: int = 100, db: Session = Depends(get_db)):
    snaps = db.query(DeviceSnapshot).order_by(DeviceSnapshot.id.desc()).limit(limit).all()
    return [
        {
            "timestamp": s.timestamp,
            "battery_level": s.battery_level,
            "latitude": s.latitude,
            "longitude": s.longitude,
            "accel_x": s.accel_x,
            "accel_y": s.accel_y,
            "accel_z": s.accel_z,
            "gyro_alpha": s.gyro_alpha,
            "gyro_beta": s.gyro_beta,
            "gyro_gamma": s.gyro_gamma,
        }
        for s in reversed(snaps)
    ]

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()  # keep alive
    except WebSocketDisconnect:
        manager.disconnect(websocket)
