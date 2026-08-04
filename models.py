from sqlalchemy import Column, Integer, Float, String, DateTime
from database import Base
from datetime import datetime

class DeviceSnapshot(Base):
    __tablename__ = "snapshots"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(String)
    battery_level = Column(Float, default=-1)
    battery_state = Column(String, default="unknown")
    device_model = Column(String, default="unknown")
    system_version = Column(String, default="unknown")
    device_name = Column(String, default="unknown")
    orientation = Column(String, default="unknown")
    latitude = Column(Float, default=0)
    longitude = Column(Float, default=0)
    accel_x = Column(Float, default=0)
    accel_y = Column(Float, default=0)
    accel_z = Column(Float, default=0)
    gyro_alpha = Column(Float, default=0)
    gyro_beta = Column(Float, default=0)
    gyro_gamma = Column(Float, default=0)
    network_type = Column(String, default="unknown")
    speed_mbps = Column(Float, default=0)
    received_at = Column(DateTime, default=datetime.utcnow)
