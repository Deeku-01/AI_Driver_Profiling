import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys

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
    """Get UIB model recommendation based on driving patterns"""
    if risk_score < 0.3:
        base_recommendation = "Pay-As-You-Drive"
        features = [
            "Pay based on actual kilometers driven",
            "Lower premiums for less driving",
            "Ideal for occasional drivers",
            "Monthly distance tracking",
            "Flexible payment options"
        ]
    elif risk_score < 0.6:
        base_recommendation = "Pay-How-You-Drive"
        features = [
            "Premium based on driving behavior",
            "Rewards for safe driving habits",
            "Real-time feedback on driving patterns",
            "Monthly behavior assessment",
            "Personalized driving tips"
        ]
    else:
        base_recommendation = "Manage-How-You-Drive"
        features = [
            "Active risk management",
            "Intensive driving behavior monitoring",
            "Regular safety coaching",
            "Incident alerts and analysis",
            "Mandatory safety workshops"
        ]
    
    return base_recommendation, features

def show_model_comparison(driver_risk_score):
    """Show interactive UIB model comparison"""
    models_data = {
        'Feature': [
            'Premium Calculation',
            'Main Focus',
            'Monitoring Level',
            'Feedback Frequency',
            'Risk Assessment',
            'Reward System'
        ],
        'Pay-As-You-Drive': [
            'Distance Based',
            'Usage Amount',
            'Basic',
            'Monthly',
            'Distance-focused',
            'Low-mileage Discounts'
        ],
        'Pay-How-You-Drive': [
            'Behavior Based',
            'Driving Quality',
            'Moderate',
            'Weekly',
            'Pattern Analysis',
            'Safe Driving Bonuses'
        ],
        'Manage-How-You-Drive': [
            'Risk Based',
            'Risk Management',
            'Intensive',
            'Daily',
            'Comprehensive',
            'Improvement Rewards'
        ]
    }
    
    df_models = pd.DataFrame(models_data)
    
    st.subheader("UIB Model Comparison")
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

def create_score_breakdown(driver_info):
    """Create an interactive bar chart showing score breakdown"""
    categories = {
        'sudden_braking_events': 'Sudden Braking',
        'speeding_events': 'Speeding',
        'previous_accidents': 'Accidents',
        'traffic_fines': 'Traffic Fines'
    }
    
    max_values = {
        'sudden_braking_events': 100,
        'speeding_events': 100,
        'previous_accidents': 3,
        'traffic_fines': 3
    }
    
    scores = []
    for key, label in categories.items():
        if pd.notna(driver_info[key]):
            normalized_value = min(driver_info[key] / max_values[key], 1) * 100
            scores.append({
                'Category': label,
                'Score': normalized_value,
                'Raw Value': driver_info[key]
            })
    
    df = pd.DataFrame(scores)
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df['Category'],
        y=df['Score'],
        text=[f"{score:.1f}%" for score in df['Score']],
        textposition='auto',
        hovertemplate="Category: %{x}<br>Score: %{y:.1f}%<br>Raw Value: %{customdata}<extra></extra>",
        customdata=df['Raw Value'],
        marker_color=['#ff9999', '#99ff99', '#66b3ff', '#ffcc99']
    ))
    
    fig.update_layout(
        title="Driving Score Breakdown",
        yaxis_title="Score (%)",
        showlegend=False,
        height=400
    )
    
    st.plotly_chart(fig)

def create_model_suitability_chart(risk_score, monthly_distance, driving_style):
    """Create an interactive chart showing suitability for each UIB model"""
    
    # Calculate suitability scores for each model
    payd_score = (1 - (monthly_distance / 3000)) * 100  # Higher score for lower distance
    payd_score = max(min(payd_score, 100), 0)  # Clamp between 0 and 100
    
    phyd_score = (1 - risk_score) * 100  # Higher score for lower risk
    
    mhyd_score = risk_score * 100  # Higher score for higher risk
    
    # Add driving style modifier
    style_modifiers = {
        'conservative': {'payd': 1.1, 'phyd': 1.2, 'mhyd': 0.8},
        'moderate': {'payd': 1.0, 'phyd': 1.0, 'mhyd': 1.0},
        'aggressive': {'payd': 0.8, 'phyd': 0.8, 'mhyd': 1.2}
    }
    
    modifier = style_modifiers.get(driving_style, {'payd': 1.0, 'phyd': 1.0, 'mhyd': 1.0})
    
    payd_score *= modifier['payd']
    phyd_score *= modifier['phyd']
    mhyd_score *= modifier['mhyd']
    
    # Create suitability chart
    models = ['Pay-As-You-Drive', 'Pay-How-You-Drive', 'Manage-How-You-Drive']
    scores = [min(payd_score, 100), min(phyd_score, 100), min(mhyd_score, 100)]
    
    fig = go.Figure()
    
    # Add bars with different colors
    colors = ['#2ecc71', '#3498db', '#e74c3c']
    for model, score, color in zip(models, scores, colors):
        fig.add_trace(go.Bar(
            x=[model],
            y=[score],
            name=model,
            marker_color=color,
            text=[f"{score:.1f}%"],
            textposition='auto',
            hovertemplate="Model: %{x}<br>Suitability: %{y:.1f}%<extra></extra>"
        ))
    
    fig.update_layout(
        title="Model Suitability Analysis",
        yaxis_title="Suitability Score (%)",
        showlegend=False,
        height=400
    )
    
    st.plotly_chart(fig)

def create_cost_benefit_analysis(driver_info, risk_score):
    """Create an interactive visualization for cost-benefit analysis"""
    monthly_distance = driver_info['total_km'] / 12
    
    # Calculate estimated monthly premiums for each model
    base_premium = 5000  # Base monthly premium
    
    # PAYD calculation
    distance_factor = monthly_distance / 1000  # per 1000 km
    payd_premium = base_premium * (0.7 + (distance_factor * 0.1))
    
    # PHYD calculation
    behavior_factor = risk_score
    phyd_premium = base_premium * (0.8 + (behavior_factor * 0.4))
    
    # MHYD calculation
    risk_factor = risk_score
    mhyd_premium = base_premium * (0.9 + (risk_factor * 0.6))
    
    # Create comparison chart
    models = ['Pay-As-You-Drive', 'Pay-How-You-Drive', 'Manage-How-You-Drive']
    premiums = [payd_premium, phyd_premium, mhyd_premium]
    
    # Calculate potential savings
    savings = [
        base_premium - payd_premium,
        base_premium - phyd_premium,
        base_premium - mhyd_premium
    ]
    
    fig = go.Figure()
    
    # Add premium bars
    fig.add_trace(go.Bar(
        name='Monthly Premium',
        x=models,
        y=premiums,
        marker_color='#3498db',
        text=[f"₹{p:.0f}" for p in premiums],
        textposition='auto',
    ))
    
    # Add savings bars
    fig.add_trace(go.Bar(
        name='Potential Monthly Savings',
        x=models,
        y=savings,
        marker_color='#2ecc71',
        text=[f"₹{s:.0f}" for s in savings],
        textposition='auto',
    ))
    
    fig.update_layout(
        title="Cost-Benefit Analysis",
        yaxis_title="Amount (₹)",
        barmode='group',
        height=400
    )
    
    st.plotly_chart(fig)

def show_recommendations(driver_details):
    """Main function to show model recommendations"""
    st.title("UIB Model Recommendations")
    
    if not driver_details["success"]:
        st.error("Error loading driver details")
        return
    
    driver = driver_details["driver"]
    info = driver_details["additional_info"]
    
    # Calculate risk score
    risk_score = calculate_risk_score(info)
    
    # Get model recommendation
    recommended_model, features = get_model_recommendation(risk_score, info['total_km'], info['driving_style'])
    
    # Create tabs for different analyses
    tabs = st.tabs(["Profile & Risk", "Score Analysis", "Model Comparison", "Cost Analysis"])
    
    with tabs[0]:
        col1, col2 = st.columns(2)
        
        with col1:
            st.header("Your Driving Profile")
            st.write(f"Driving Style: {info['driving_style'].title()}")
            st.write(f"Vehicle Type: {info['vehicle_type'].title()}")
            st.write(f"Experience: {info['years_of_experience']} years")
            st.write(f"Total Distance: {info['total_km']:.2f} km")
            
            monthly_distance = info['total_km'] / 12
            st.write(f"Average Monthly Distance: {monthly_distance:.2f} km")
            
            if monthly_distance < 1000:
                st.info("💡 Low monthly usage suggests Pay-As-You-Drive might be cost-effective")
            elif monthly_distance > 2000:
                st.info("💡 High monthly usage suggests focusing on driving behavior for better rates")
        
        with col2:
            st.header("Risk Assessment")
            create_risk_gauge(risk_score)
            
            if info['driving_style'] == 'conservative':
                st.success("👍 Conservative driving style is ideal for Pay-How-You-Drive benefits")
            elif info['driving_style'] == 'aggressive':
                st.warning("⚠️ Aggressive driving style might benefit from Manage-How-You-Drive coaching")
    
    with tabs[1]:
        st.header("Detailed Score Analysis")
        create_score_breakdown(info)
        show_driving_patterns(info)
    
    with tabs[2]:
        st.header("Model Suitability Analysis")
        create_model_suitability_chart(risk_score, monthly_distance, info['driving_style'])
        
        st.header("Recommended UIB Model")
        st.subheader(f"🎯 {recommended_model}")
        st.write("Features included:")
        for feature in features:
            st.write(f"✓ {feature}")
        
        show_model_comparison(risk_score)
    
    with tabs[3]:
        st.header("Cost-Benefit Analysis")
        create_cost_benefit_analysis(info, risk_score)
        
        st.info("""
        💡 The cost analysis is based on:
        - Your monthly driving distance
        - Your driving behavior scores
        - Risk assessment
        - Potential savings from each model
        """)
    
    st.header("Make Your Choice")
    available_models = ["Pay-As-You-Drive", "Pay-How-You-Drive", "Manage-How-You-Drive"]
    selected_model = st.selectbox(
        "Choose your UIB Model",
        available_models,
        index=available_models.index(recommended_model)
    )
    
    if selected_model != recommended_model:
        st.warning("""
            ⚠️ Note: You're selecting a different model than recommended. 
            Consider your driving patterns and usage carefully.
        """)
    
    if st.button("Confirm Model Selection"):
        from database.db_manager import DatabaseManager
        db = DatabaseManager()
        result = db.update_uib_model(driver.driver_id, selected_model)
        
        if result["success"]:
            st.success(f"Successfully enrolled in the {selected_model} model!")
            st.info("You will be locked into this model for 12 months")
            
            if selected_model == "Pay-As-You-Drive":
                st.info("📱 Download our app to start tracking your mileage")
            elif selected_model == "Pay-How-You-Drive":
                st.info("🚗 Your driving behavior monitoring will begin within 24 hours")
            else:
                st.info("📅 We'll contact you to schedule your first driving assessment")
        else:
            st.error("Failed to update model. Please try again.") 