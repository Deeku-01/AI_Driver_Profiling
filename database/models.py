from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

class Driver(Base):
    __tablename__ = 'drivers'
    
    id = Column(Integer, primary_key=True)
    driver_id = Column(String(50), unique=True, nullable=False)
    license_plate = Column(String(20), unique=True, nullable=False)
    license_number = Column(String(50), unique=True, nullable=False)
    password = Column(String(256), nullable=False)  # Will store hashed password
    registration_date = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    is_active = Column(Boolean, default=True)
    selected_uib_model = Column(String(50))
    model_lock_period = Column(DateTime)
    
    def __repr__(self):
        return f"<Driver(driver_id='{self.driver_id}', license_plate='{self.license_plate}')>" 