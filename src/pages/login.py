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
from src.styles.custom import apply_custom_style, card, metric_card

# Initialize database manager
db = DatabaseManager()

def init_session_state():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'driver_id' not in st.session_state:
        st.session_state.driver_id = None
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'Driver Dashboard'
    if 'show_register' not in st.session_state:
        st.session_state.show_register = False

def show_driver_dashboard(driver_details):
    apply_custom_style()
    
    # Header Bar
    st.markdown("""
        <div class="header-bar">
            <h1>Driver Dashboard</h1>
            <p>Your personalized driving analytics hub</p>
        </div>
    """, unsafe_allow_html=True)
    
    driver = driver_details["driver"]
    info = driver_details["additional_info"]
    
    # Create modern dashboard layout
    col1, col2 = st.columns(2)
    
    with col1:
        card("Driver Information", f"""
            <div style="font-size: 1.1rem;">
                <p><strong>Driver ID:</strong> {driver.driver_id}</p>
                <p><strong>License Plate:</strong> {driver.license_plate}</p>
                <p><strong>License Number:</strong> {driver.license_number}</p>
                <p><strong>Age:</strong> {info['age']}</p>
                <p><strong>Experience:</strong> {info['years_of_experience']} years</p>
                <p><strong>Vehicle Type:</strong> {info['vehicle_type'].title()}</p>
                <p><strong>Driving Style:</strong> {info['driving_style'].title()}</p>
            </div>
        """)
    
    with col2:
        card("Driving Statistics", "")
        col3, col4 = st.columns([1, 1])
        
        with col3:
            st.markdown(metric_card(
                "Total Distance",
                f"{info['total_km']:.2f} km",
                None
            ), unsafe_allow_html=True)
            
            st.markdown(metric_card(
                "Monthly Average",
                f"{(info['total_km']/12):.2f} km",
                None
            ), unsafe_allow_html=True)
        
        with col4:
            st.markdown(metric_card(
                "Sudden Braking",
                str(info['sudden_braking_events']),
                None
            ), unsafe_allow_html=True)
            
            st.markdown(metric_card(
                "Speeding Events",
                str(info['speeding_events']),
                None
            ), unsafe_allow_html=True)
    
    # Show driving patterns visualization
    st.subheader("Your Driving Pattern")
    show_driving_patterns(info)  # This will show the radar chart
    
    # Current UIB Model Status
    st.subheader("Current UIB Model Status")
    if driver.selected_uib_model:
        col5, col6 = st.columns(2)
        with col5:
            st.info(f"Current Model: {driver.selected_uib_model}")
            if driver.model_lock_period and driver.model_lock_period > datetime.utcnow():
                st.warning(f"Locked until: {driver.model_lock_period.strftime('%Y-%m-%d')}")
            else:
                st.success("You can change your UIB model!")
        
        with col6:
            if driver.selected_uib_model == "Pay-As-You-Drive":
                st.markdown(metric_card(
                    "Monthly Distance",
                    f"{(info['total_km']/12):.1f} km",
                    None
                ), unsafe_allow_html=True)
            elif driver.selected_uib_model == "Pay-How-You-Drive":
                safe_score = 100 - (((info['sudden_braking_events'] or 0) + (info['speeding_events'] or 0)) / 2)
                st.markdown(metric_card(
                    "Safe Driving Score",
                    f"{safe_score:.1f}%",
                    None
                ), unsafe_allow_html=True)
            else:
                risk_events = ((info['sudden_braking_events'] or 0) + 
                             (info['speeding_events'] or 0) + 
                             (info['previous_accidents'] or 0) * 10 +
                             (info['traffic_fines'] or 0) * 5)
                st.markdown(metric_card(
                    "Risk Events",
                    str(risk_events),
                    None
                ), unsafe_allow_html=True)
    else:
        st.warning("No UIB model selected. Visit the Model Recommendations page to choose one!")
        if st.button("Choose a UIB Model", use_container_width=True):
            st.session_state.current_page = 'Model Recommendations'

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
    apply_custom_style()
    
    st.markdown("""
        <div class="header-container">
            <h1>Personalised Insurance Portal</h1>
            <p>Welcome to your personalized insurance platform based on your driving analytics!</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    init_session_state()
    
    if st.session_state.logged_in:
        show_dashboard()
        return
    
    # Switch to register tab if needed
    if st.session_state.show_register:
        st.session_state.show_register = False  # Reset the flag
        st.query_params["tab"] = "register"
    
    # Create a container for the login/register form
    form_container = st.container()
    
    with form_container:
        tabs = st.tabs(["Login", "Register"])
        
        # Login Tab
        with tabs[0]:
            col1, col2, col3 = st.columns([1,2,1])
            with col2:
                st.markdown("""
                    <div style="background-color: white; padding: 2rem; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        <h2 style="text-align: center; color: #1E3D59; margin-bottom: 2rem;">Login</h2>
                """, unsafe_allow_html=True)
                
                license_number = st.text_input("License Number", placeholder="Enter your license number")
                password = st.text_input("Password", type="password", placeholder="Enter your password")
                
                if st.button("Login", use_container_width=True):
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
                
                st.markdown("</div>", unsafe_allow_html=True)
        
        # Registration Tab
        with tabs[1]:
            col1, col2, col3 = st.columns([1,2,1])
            with col2:
                st.markdown("""
                    <div style="background-color: white; padding: 2rem; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        <h2 style="text-align: center; color: #1E3D59; margin-bottom: 2rem;">New Driver Registration</h2>
                """, unsafe_allow_html=True)
                
                st.info("Please enter your license details as they appear in the driver records")
                
                license_plate = st.text_input("License Plate Number", placeholder="Enter license plate")
                reg_license_number = st.text_input("License Number", key="reg_license", placeholder="Enter license number")
                password = st.text_input("Create Password", type="password", key="reg_pass")
                confirm_password = st.text_input("Confirm Password", type="password")
                
                if st.button("Register", use_container_width=True):
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
                
                st.markdown("</div>", unsafe_allow_html=True)
    
    # Add footer
    st.markdown("""
        <div style="position: fixed; bottom: 0; left: 0; right: 0; background-color: #f8f9fa; padding: 1rem; text-align: center; font-size: 0.8rem; color: #6c757d;">
            © 2024 Driver based Insurance Portal. All rights reserved.
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    login_page() 