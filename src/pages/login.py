import streamlit as st
import sys
import os
from pathlib import Path
from datetime import datetime

# Add the project root directory to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

# Import after adding to path
from database.db_manager import DatabaseManager
from src.model_recommendation import show_recommendations, create_risk_gauge, show_driving_patterns
import time

# Initialize database manager
db = DatabaseManager()

def init_session_state():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'driver_id' not in st.session_state:
        st.session_state.driver_id = None
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'Driver Dashboard'

def show_driver_dashboard(driver_details):
    st.title("Driver Dashboard")
    
    driver = driver_details["driver"]
    info = driver_details["additional_info"]
    
    # Display driver information in columns
    col1, col2 = st.columns(2)
    
    with col1:
        st.header("Driver Information")
        st.write(f"Driver ID: {driver.driver_id}")
        st.write(f"License Plate: {driver.license_plate}")
        st.write(f"License Number: {driver.license_number}")
        
        if "additional_info" in driver_details:
            info = driver_details["additional_info"]
            st.write(f"Age: {info['age']}")
            st.write(f"Years of Experience: {info['years_of_experience']}")
            st.write(f"Vehicle Type: {info['vehicle_type']}")
            st.write(f"Driving Style: {info['driving_style']}")
    
    with col2:
        st.header("Driving Statistics")
        if "additional_info" in driver_details:
            info = driver_details["additional_info"]
            st.write(f"Total Distance: {info['total_km']:.2f} km")
            st.write(f"Monthly Average: {(info['total_km']/12):.2f} km")
            st.write(f"Sudden Braking Events: {info['sudden_braking_events']}")
            st.write(f"Speeding Events: {info['speeding_events']}")
            st.write(f"Previous Accidents: {info['previous_accidents']}")
            st.write(f"Traffic Fines: {info['traffic_fines']}")
    
    # Show driving patterns visualization
    st.header("Your Driving Pattern")
    show_driving_patterns(info)
    
    # Current UIB Model Status
    st.header("Current UIB Model Status")
    if driver.selected_uib_model:
        col3, col4 = st.columns(2)
        with col3:
            st.info(f"Current Model: {driver.selected_uib_model}")
            if driver.model_lock_period and driver.model_lock_period > datetime.utcnow():
                st.warning(f"Locked into current model until: {driver.model_lock_period.strftime('%Y-%m-%d')}")
            else:
                st.success("You can change your UIB model. Visit the Model Recommendations page to explore options!")
        
        with col4:
            if driver.selected_uib_model == "Pay-As-You-Drive":
                st.metric("Monthly Distance", f"{(info['total_km']/12):.1f} km", "Tracked")
            elif driver.selected_uib_model == "Pay-How-You-Drive":
                safe_score = 100 - (((info['sudden_braking_events'] or 0) + (info['speeding_events'] or 0)) / 2)
                st.metric("Safe Driving Score", f"{safe_score:.1f}%", "Monitored")
            else:  # Manage-How-You-Drive
                risk_events = ((info['sudden_braking_events'] or 0) + 
                             (info['speeding_events'] or 0) + 
                             (info['previous_accidents'] or 0) * 10 +
                             (info['traffic_fines'] or 0) * 5)
                st.metric("Risk Events", f"{risk_events}", "Monitored")
    else:
        st.warning("No UIB model selected. Visit the Model Recommendations page to choose one!")
        st.button("Choose a UIB Model", on_click=lambda: setattr(st.session_state, 'current_page', 'Model Recommendations'))

def show_dashboard():
    st.sidebar.title("Navigation")
    pages = ['Driver Dashboard', 'Model Recommendations']
    
    st.session_state.current_page = st.sidebar.radio("Go to", pages)
    
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.driver_id = None
        st.rerun()
    
    driver_details = db.get_driver_details(st.session_state.driver_id)
    if not driver_details["success"]:
        st.error("Error loading driver details")
        return
    
    if st.session_state.current_page == 'Driver Dashboard':
        show_driver_dashboard(driver_details)
    else:
        show_recommendations(driver_details)

def login_page():
    st.title("Driver Portal Login")
    
    # Initialize session state
    init_session_state()
    
    if st.session_state.logged_in:
        show_dashboard()
        return
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    # Login Tab
    with tab1:
        st.header("Login")
        license_number = st.text_input("License Number")
        password = st.text_input("Password", type="password")
        
        if st.button("Login"):
            if license_number and password:
                result = db.authenticate_driver(license_number, password)
                if result["success"]:
                    st.session_state.logged_in = True
                    st.session_state.driver_id = result["driver"].driver_id
                    st.success("Login successful!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Invalid credentials. Please try again.")
            else:
                st.warning("Please fill in all fields.")
    
    # Registration Tab
    with tab2:
        st.header("New Driver Registration")
        st.info("Please enter your license details as they appear in the driver records")
        license_plate = st.text_input("License Plate Number")
        reg_license_number = st.text_input("License Number", key="reg_license")
        password = st.text_input("Create Password", type="password", key="reg_pass")
        confirm_password = st.text_input("Confirm Password", type="password")
        
        if st.button("Register"):
            if license_plate and reg_license_number and password and confirm_password:
                if password != confirm_password:
                    st.error("Passwords do not match!")
                    return
                
                result = db.register_driver(license_plate, reg_license_number, password)
                if result["success"]:
                    st.success(f"Registration successful! Your Driver ID is: {result['driver_id']}")
                    st.info("Please use your license number and password to login.")
                else:
                    st.error(f"Registration failed: {result['error']}")
            else:
                st.warning("Please fill in all fields.")

if __name__ == "__main__":
    login_page() 