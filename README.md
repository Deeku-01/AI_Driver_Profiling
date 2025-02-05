# AI Driver Profiling System

## Overview
The AI Driver Profiling System is an advanced analytics platform that leverages machine learning to analyze driver behavior and provide personalized insurance model recommendations. The system processes driving data to calculate risk scores, analyze patterns, and suggest optimal Usage-Based Insurance (UBI) models for each driver.

## Installation & Setup

1. Clone the repository:
```bash
git clone https://github.com/Deeku-01/AI_Driver_Profiling.git
```
2. Change directory:
```bash
cd AI_Driver_Profiling
```
3. Install required packages:
```bash
pip install -r requirements.txt
```
4. Run the data pipeline in sequence:
```bash
Generate synthetic driver data:
python src/functionalities/data_generator.py

Perform risk analysis:
python src/functionalities/risk_analysis.py

Run ML models:
python src/functionalities/ml_models.py

Calculate insurance premiums:
python src/functionalities/insurance_models.py
```


5. Start the Streamlit application:
```bash
streamlit run src/pages/login.py
```

## Key Features

### 1. Driver Behavior Analysis
- Real-time monitoring of driving patterns
- Tracking of key metrics:
  - Sudden braking events
  - Speeding incidents
  - Previous accidents
  - Traffic violations
  - Total kilometers driven

### 2. Risk Assessment
- Machine learning-based risk clustering
- Comprehensive risk scoring using multiple factors:
  - Driving style (Conservative, Moderate, Aggressive)
  - Vehicle type (Sedan, SUV, Sports, Compact)
  - Experience level
  - Age factor
  - Historical incidents

### 3. Insurance Model Recommendations
Three tailored UBI models:
- **Pay-As-You-Drive (PAYD)**
  - Distance-based premium calculation
  - Ideal for occasional drivers
  - Monthly distance tracking
  
- **Pay-How-You-Drive (PHYD)**
  - Behavior-based premium calculation
  - Real-time feedback
  - Safe driving rewards
  
- **Manage-How-You-Drive (MHYD)**
  - Intensive risk management
  - Regular safety coaching
  - Comprehensive monitoring

### 4. Interactive Dashboard
- Personal driving statistics
- Risk score visualization
- Model comparison tools
- Cost-benefit analysis
- Real-time recommendations

## Technical Architecture

### Core Components
1. **Data Generation & Processing**
   - `data_generator.py`: Synthetic driver data generation
   - `risk_analysis.py`: Risk assessment algorithms
   - `ml_models.py`: Machine learning model implementations

2. **Insurance Logic**
   - `insurance_models.py`: Premium calculation engines
   - `model_recommendation.py`: UBI model selection logic

3. **User Interface**
   - `login.py`: Authentication system
   - Streamlit-based interactive dashboard

### Technologies Used
- Python 3.x
- Streamlit
- Pandas & NumPy
- Scikit-learn
- Plotly
- SQLAlchemy


## Data Flow
1. Driver data collection/generation
2. Risk analysis and clustering
3. Machine learning model processing
4. Premium calculation
5. UBI model recommendation
6. Interactive visualization

## Machine Learning Models
- K-means clustering for risk categorization
- Random Forest for behavior classification
- Logistic Regression for risk prediction
- Decision Trees for model recommendations

## Security Features
- Secure authentication system
- Password protection
- Session management
- Data encryption

## Future Enhancements
- Real-time GPS integration
- Mobile app development
- Advanced telemetrics
- Predictive accident analysis
- Integration with external insurance providers

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.


## Acknowledgments
- Insurance industry standards
- Machine learning best practices
- Traffic safety guidelines