from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base, Driver
import hashlib
import pandas as pd
from datetime import datetime, timedelta

class DatabaseManager:
    def __init__(self, db_url='sqlite:///driver_portal.db'):
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        self._load_driver_data()
    
    def _load_driver_data(self):
        try:
            self.driver_data = pd.read_csv('src/data/driver_data.csv')
        except Exception as e:
            print(f"Error loading driver data: {e}")
            self.driver_data = None
    
    def _hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register_driver(self, license_plate, license_number, password):
        try:
            # First check if the license number is already registered
            existing_license = self.session.query(Driver).filter_by(
                license_number=license_number
            ).first()
            
            if existing_license:
                return {
                    "success": False, 
                    "error": "This license number is already registered. Please login instead."
                }

            # Find the driver in the CSV data
            if self.driver_data is not None:
                driver_info = self.driver_data[
                    (self.driver_data['license_plate'] == license_plate) & 
                    (self.driver_data['license_number'] == license_number)
                ]
                
                if len(driver_info) == 0:
                    return {
                        "success": False, 
                        "error": "License plate and license number combination not found in records. Please check your details."
                    }
                
                driver_id = str(driver_info.iloc[0]['driver_id'])
                
                # Check if driver_id is already registered
                existing_driver = self.session.query(Driver).filter_by(driver_id=driver_id).first()
                if existing_driver:
                    return {
                        "success": False, 
                        "error": "This driver is already registered. Please login instead."
                    }
                
                # Create new driver
                new_driver = Driver(
                    driver_id=driver_id,
                    license_plate=license_plate,
                    license_number=license_number,
                    password=self._hash_password(password)
                )
                
                self.session.add(new_driver)
                self.session.commit()
                return {"success": True, "driver_id": driver_id}
            else:
                return {"success": False, "error": "Driver data not available. Please try again later."}
        except Exception as e:
            self.session.rollback()
            return {"success": False, "error": f"Registration error: {str(e)}"}
    
    def authenticate_driver(self, license_number, password):
        try:
            driver = self.session.query(Driver).filter_by(
                license_number=license_number,
                password=self._hash_password(password)
            ).first()
            
            if driver:
                driver.last_login = datetime.utcnow()
                self.session.commit()
                return {"success": True, "driver": driver}
            return {"success": False, "error": "Invalid credentials. Please try again."}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def update_uib_model(self, driver_id, model_name, lock_period_months=12):
        try:
            driver = self.session.query(Driver).filter_by(driver_id=driver_id).first()
            if driver:
                driver.selected_uib_model = model_name
                driver.model_lock_period = datetime.utcnow() + timedelta(days=30*lock_period_months)
                self.session.commit()
                return {"success": True}
            return {"success": False, "error": "Driver not found"}
        except Exception as e:
            self.session.rollback()
            return {"success": False, "error": str(e)}
    
    def get_driver_details(self, driver_id):
        try:
            driver = self.session.query(Driver).filter_by(driver_id=driver_id).first()
            if driver:
                # Get additional details from CSV
                if self.driver_data is not None:
                    csv_data = self.driver_data[self.driver_data['driver_id'] == int(driver_id)].iloc[0]
                    return {
                        "success": True,
                        "driver": driver,
                        "additional_info": {
                            "age": csv_data['age'],
                            "driving_style": csv_data['driving_style'],
                            "vehicle_type": csv_data['vehicle_type'],
                            "years_of_experience": csv_data['years_of_experience'],
                            "total_km": csv_data['total_km'],
                            "sudden_braking_events": csv_data['sudden_braking_events'],
                            "speeding_events": csv_data['speeding_events'],
                            "previous_accidents": csv_data['previous_accidents'],
                            "traffic_fines": csv_data['traffic_fines']
                        }
                    }
                return {"success": True, "driver": driver}
            return {"success": False, "error": "Driver not found"}
        except Exception as e:
            return {"success": False, "error": str(e)} 