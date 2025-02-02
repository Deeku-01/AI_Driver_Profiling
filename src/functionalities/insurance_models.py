import numpy as np
import pandas as pd

class InsuranceModel:
    def __init__(self):
        # Base annual premium for different vehicle types (in Rupees)
        self.base_premiums = {
            'sedan': 25000,    # Changed from 1000 to 25000
            'suv': 30000,      # Changed from 1200 to 30000
            'sports': 40000,   # Changed from 1500 to 40000
            'compact': 20000   # Changed from 800 to 20000
        }
        
        # Distance brackets (monthly km) and their factors
        self.distance_brackets = {
            500: {'factor': 0.7, 'description': 'Very Low Usage'},
            1000: {'factor': 0.85, 'description': 'Low Usage'},
            1500: {'factor': 1.0, 'description': 'Average Usage'},
            2000: {'factor': 1.2, 'description': 'High Usage'},
            float('inf'): {'factor': 1.4, 'description': 'Very High Usage'}
        }
    
    def calculate_distance_factor(self, total_km):
        """Calculate distance factor for PAYD model"""
        monthly_km = total_km / 30
        
        # Find appropriate bracket
        for bracket, info in self.distance_brackets.items():
            if monthly_km <= bracket:
                return {
                    'monthly_km': round(monthly_km, 2),
                    'bracket_description': info['description'],
                    'distance_factor': info['factor']
                }
    
    def calculate_risk_score(self, driver_data):
        """Calculate normalized risk score based on driving metrics"""
        # Calculate rates per 100km
        km_factor = 100 / driver_data['total_km'] if driver_data['total_km'] > 0 else 0
        
        # Handle missing values with median values for the driving style
        braking_events = driver_data['sudden_braking_events']
        speeding_events = driver_data['speeding_events']
        
        if pd.isna(braking_events):
            if driver_data['driving_style'] == 'conservative':
                braking_events = 1.25
            elif driver_data['driving_style'] == 'moderate':
                braking_events = 2.75
            else:
                braking_events = 5.0
                
        if pd.isna(speeding_events):
            if driver_data['driving_style'] == 'conservative':
                speeding_events = 0.9
            elif driver_data['driving_style'] == 'moderate':
                speeding_events = 2.0
            else:
                speeding_events = 4.25
        
        # Calculate individual risk components
        braking_risk = min(2.0, (braking_events * km_factor) / 5)  # Normalize to 0-2 range
        speeding_risk = min(2.0, (speeding_events * km_factor) / 5)
        accident_risk = min(2.0, driver_data['previous_accidents'] * 0.67)
        fine_risk = min(2.0, driver_data['traffic_fines'] * 0.5)
        
        # Calculate weighted risk score
        risk_score = (
            braking_risk * 0.3 +
            speeding_risk * 0.3 +
            accident_risk * 0.25 +
            fine_risk * 0.15
        )
        
        return {
            'braking_risk': round(braking_risk, 2),
            'speeding_risk': round(speeding_risk, 2),
            'accident_risk': round(accident_risk, 2),
            'fine_risk': round(fine_risk, 2),
            'total_risk_score': round(risk_score, 2)
        }
    
    def calculate_behavior_weight(self, driver_data, risk_score):
        """Calculate behavior weight for PHYD model"""
        # Base weight starts at 1.0
        base_weight = 1.0
        
        # Adjust for driving style
        style_adjustments = {
            'conservative': -0.2,  # Discount for conservative drivers
            'moderate': 0,         # No adjustment for moderate drivers
            'aggressive': 0.3      # Premium for aggressive drivers
        }
        
        # Adjust for experience
        if driver_data['years_of_experience'] < 3:
            experience_factor = 0.2
        elif driver_data['years_of_experience'] < 10:
            experience_factor = 0.1
        else:
            experience_factor = 0
            
        # Adjust for age
        if driver_data['age'] < 25:
            age_factor = 0.2
        elif driver_data['age'] > 65:
            age_factor = 0.1
        else:
            age_factor = 0
            
        # Calculate final behavior weight
        behavior_weight = (
            base_weight +
            style_adjustments[driver_data['driving_style']] +
            experience_factor +
            age_factor +
            (risk_score['total_risk_score'] - 1) * 0.2  # Risk score adjustment
        )
        
        # Ensure weight stays within reasonable bounds
        behavior_weight = max(0.6, min(1.8, behavior_weight))
        
        return round(behavior_weight, 2)

    def calculate_premiums(self, driver_data):
        """Calculate both PAYD and PHYD premiums with detailed breakdown"""
        base_premium = self.base_premiums[driver_data['vehicle_type']]
        
        # Calculate PAYD premium
        distance_info = self.calculate_distance_factor(driver_data['total_km'])
        payd_premium = base_premium * distance_info['distance_factor']
        
        # Calculate PHYD premium
        risk_scores = self.calculate_risk_score(driver_data)
        behavior_weight = self.calculate_behavior_weight(driver_data, risk_scores)
        phyd_premium = base_premium * behavior_weight
        
        return {
            'driver_id': driver_data['driver_id'],
            'base_premium': base_premium,
            'distance_info': distance_info,
            'risk_scores': risk_scores,
            'behavior_weight': behavior_weight,
            'payd_premium': round(payd_premium, 2),
            'phyd_premium': round(phyd_premium, 2)
        }

class PremiumCalculator:
    def __init__(self, csv_path='data/driver_data.csv'):
        self.driver_data = pd.read_csv(csv_path)
        self.insurance_model = InsuranceModel()
    
    def calculate_all_premiums(self):
        """Calculate premiums for all drivers"""
        results = []
        
        for _, driver in self.driver_data.iterrows():
            premium_info = self.insurance_model.calculate_premiums(driver)
            
            results.append({
                'driver_id': driver['driver_id'],
                'driving_style': driver['driving_style'],
                'vehicle_type': driver['vehicle_type'],
                'monthly_km': premium_info['distance_info']['monthly_km'],
                'risk_score': premium_info['risk_scores']['total_risk_score'],
                'behavior_weight': premium_info['behavior_weight'],
                'payd_premium': premium_info['payd_premium'],
                'phyd_premium': premium_info['phyd_premium'],
                'recommended_model': 'PAYD' if premium_info['payd_premium'] < premium_info['phyd_premium'] else 'PHYD'
            })
        
        return pd.DataFrame(results)

def main():
    try:
        calculator = PremiumCalculator()
        results = calculator.calculate_all_premiums()
        
        # Save results
        results.to_csv('data/premium_calculations.csv', index=False)
        
        # Display analysis
        print("\nPremium Recommendations Summary:")
        print("\nModel Distribution:")
        print(results['recommended_model'].value_counts())
        print("\nPercentage Split:")
        print(results['recommended_model'].value_counts(normalize=True) * 100)
        
        print("\nAverage Premiums by Driving Style:")
        style_premiums = results.groupby('driving_style').agg({
            'payd_premium': 'mean',
            'phyd_premium': 'mean'
        }).round(2)
        print(style_premiums)
        
        print("\nRecommendations by Driving Style:")
        style_recommendations = pd.crosstab(
            results['driving_style'],
            results['recommended_model']
        )
        print(style_recommendations)
        
        # Calculate and display average savings with ₹ symbol
        results['savings'] = results.apply(
            lambda x: abs(x['payd_premium'] - x['phyd_premium']),
            axis=1
        )
        print("\nAverage Potential Savings: ₹{:.2f}".format(results['savings'].mean()))
        
        # Add more detailed savings analysis
        print("\nAverage Savings by Driving Style:")
        style_savings = results.groupby('driving_style')['savings'].mean().round(2)
        print(style_savings.apply(lambda x: f"₹{x:,.2f}"))
        
        print("\nMaximum Potential Savings: ₹{:,.2f}".format(results['savings'].max()))
        print("Minimum Potential Savings: ₹{:,.2f}".format(results['savings'].min()))
        
    except FileNotFoundError:
        print("Error: Driver data file not found. Please run data_generator.py first.")

if __name__ == "__main__":
    main() 