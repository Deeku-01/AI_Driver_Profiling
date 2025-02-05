import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys
from src.styles.custom import apply_custom_style, card, metric_card

# Add the project root directory to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

def calculate_risk_score(driver_info):
    """Calculate a risk score based on driving behavior"""
    # Normalize and weight different factors
    weights = {
        'sudden_braking_events': 0.25,
        'speeding_events': 0.25,
        'previous_accidents': 0.3,
        'traffic_fines': 0.2
    }
    
    max_values = {
        'sudden_braking_events': 100,
        'speeding_events': 100,
        'previous_accidents': 3,
        'traffic_fines': 3
    }
    
    score = 0
    for factor, weight in weights.items():
        if pd.notna(driver_info[factor]):
            normalized_value = min(driver_info[factor] / max_values[factor], 1)
            score += normalized_value * weight
    
    return score

def get_model_recommendation(risk_score, total_km, driving_style):
    """Get model recommendation based on risk score and driving patterns"""
    if risk_score < 0.3:
        base_recommendation = "Premium"
        features = [
            "Highest coverage for safe drivers",
            "Rewards for consistent safe driving",
            "Personal accident cover up to ₹15 lakhs",
            "Zero depreciation cover",
            "24/7 roadside assistance"
        ]
    elif risk_score < 0.6:
        base_recommendation = "Standard"
        features = [
            "Balanced coverage for average risk drivers",
            "Personal accident cover up to ₹10 lakhs",
            "Basic roadside assistance",
            "Partial zero depreciation cover",
            "Optional add-ons available"
        ]
    else:
        base_recommendation = "Basic"
        features = [
            "Essential coverage for high-risk drivers",
            "Personal accident cover up to ₹5 lakhs",
            "Basic third-party liability",
            "Optional roadside assistance",
            "Mandatory coverage features"
        ]
    
    return base_recommendation, features

def show_model_comparison(driver_risk_score):
    """Show interactive model comparison"""
    models_data = {
        'Feature': [
            'Premium Discount',
            'Personal Accident Cover',
            'Zero Depreciation',
            'Roadside Assistance',
            'NCB Bonus',
            'Add-ons Available'
        ],
        'Basic': [
            'Up to 10%',
            '₹5 lakhs',
            'No',
            'Optional',
            'Up to 20%',
            'Limited'
        ],
        'Standard': [
            'Up to 25%',
            '₹10 lakhs',
            'Partial',
            'Basic',
            'Up to 35%',
            'Multiple'
        ],
        'Premium': [
            'Up to 40%',
            '₹15 lakhs',
            'Full',
            '24/7 Premium',
            'Up to 50%',
            'Comprehensive'
        ]
    }
    
    df_models = pd.DataFrame(models_data)
    
    st.subheader("Model Comparison")
    st.dataframe(df_models.set_index('Feature'), use_container_width=True)

def create_risk_gauge(risk_score):
    """Create a gauge chart for risk score"""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = risk_score * 100,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Risk Score"},
        gauge = {
            'axis': {'range': [0, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 30], 'color': "lightgreen"},
                {'range': [30, 60], 'color': "yellow"},
                {'range': [60, 100], 'color': "red"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': risk_score * 100
            }
        }
    ))
    
    st.plotly_chart(fig)

def show_driving_patterns(driver_info):
    """Show driving pattern visualizations"""
    # Prepare data for radar chart
    categories = ['Sudden Braking', 'Speeding', 'Accidents', 'Fines']
    values = [
        driver_info['sudden_braking_events'] / 100 if pd.notna(driver_info['sudden_braking_events']) else 0,
        driver_info['speeding_events'] / 100 if pd.notna(driver_info['speeding_events']) else 0,
        driver_info['previous_accidents'] / 3 if pd.notna(driver_info['previous_accidents']) else 0,
        driver_info['traffic_fines'] / 3 if pd.notna(driver_info['traffic_fines']) else 0
    ]
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Your Driving Pattern'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )),
        showlegend=False
    )
    
    st.plotly_chart(fig)

def show_recommendations(driver_details):
    """Main function to show model recommendations"""
    apply_custom_style()
    
    st.markdown("""
        <div style="text-align: center; padding: 1rem 0;">
            <h1>🎯 UIB Model Recommendations</h1>
            <p style="color: #6c757d;">Find the perfect insurance model based on your driving patterns</p>
        </div>
    """, unsafe_allow_html=True)
    
    if not driver_details["success"]:
        st.error("Error loading driver details")
        return
    
    driver = driver_details["driver"]
    info = driver_details["additional_info"]
    
    # Calculate risk score
    risk_score = calculate_risk_score(info)
    
    # Get model recommendation
    recommended_model, features = get_model_recommendation(risk_score, info['total_km'], info['driving_style'])
    
    # Create tabs with modern styling
    tabs = st.tabs(["📊 Profile & Risk", "🎯 Score Analysis", "💡 Model Comparison", "💰 Cost Analysis"])
    
    with tabs[0]:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(card("Your Driving Profile", f"""
                <div style="font-size: 1.1rem;">
                    <p><strong>Driving Style:</strong> {info['driving_style'].title()}</p>
                    <p><strong>Vehicle Type:</strong> {info['vehicle_type'].title()}</p>
                    <p><strong>Experience:</strong> {info['years_of_experience']} years</p>
                    <p><strong>Total Distance:</strong> {info['total_km']:.2f} km</p>
                    <p><strong>Monthly Distance:</strong> {info['total_km']/12:.2f} km</p>
                </div>
            """), unsafe_allow_html=True)
            
            if info['total_km']/12 < 1000:
                st.info("💡 Low monthly usage suggests Pay-As-You-Drive might be cost-effective")
            elif info['total_km']/12 > 2000:
                st.info("💡 High monthly usage suggests focusing on driving behavior for better rates")
        
        with col2:
            st.markdown(card("Risk Assessment", ""))
            create_risk_gauge(risk_score)
            
            if info['driving_style'] == 'conservative':
                st.success("👍 Conservative driving style is ideal for Pay-How-You-Drive benefits")
            elif info['driving_style'] == 'aggressive':
                st.warning("⚠️ Aggressive driving style might benefit from Manage-How-You-Drive coaching")

    # Continue updating the other tabs similarly...
    
    st.header("Driving Patterns Analysis")
    show_driving_patterns(info)
    
    st.header("Recommended Model")
    st.subheader(f"🎯 {recommended_model}")
    st.write("Features included:")
    for feature in features:
        st.write(f"✓ {feature}")
    
    show_model_comparison(risk_score)
    
    st.header("Make Your Choice")
    available_models = ["Basic", "Standard", "Premium"]
    selected_model = st.selectbox(
        "Choose your UIB Model",
        available_models,
        index=available_models.index(recommended_model)
    )
    
    if selected_model != recommended_model:
        st.warning("""
            ⚠️ Note: You're selecting a different model than recommended. 
            This might affect your coverage and premiums.
        """)
    
    if st.button("Confirm Model Selection"):
        # Update the model in the database
        from database.db_manager import DatabaseManager
        db = DatabaseManager()
        result = db.update_uib_model(driver.driver_id, selected_model)
        
        if result["success"]:
            st.success(f"Successfully enrolled in the {selected_model} model!")
            st.info("You will be locked into this model for 12 months")
        else:
            st.error("Failed to update model. Please try again.") 