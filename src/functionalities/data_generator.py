import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random

class DriverDataGenerator:
    def __init__(self, num_drivers=100, days=30):
        self.num_drivers = num_drivers
        self.days = days
        
        # Define realistic ranges for different driving styles
        self.style_profiles = {
            'conservative': {
                'daily_km_range': (20, 50),
                'braking_rate': (0.5, 2),    # events per 100km
                'speeding_rate': (0.3, 1.5),  # events per 100km
                'accident_prob': [0.85, 0.12, 0.03, 0],
                'fine_rate': (0.1, 0.5)      # fines per month
            },
            'moderate': {
                'daily_km_range': (30, 70),
                'braking_rate': (1.5, 4),
                'speeding_rate': (1, 3),
                'accident_prob': [0.75, 0.18, 0.05, 0.02],
                'fine_rate': (0.3, 1.0)
            },
            'aggressive': {
                'daily_km_range': (40, 90),
                'braking_rate': (3, 7),
                'speeding_rate': (2.5, 6),
                'accident_prob': [0.65, 0.25, 0.07, 0.03],
                'fine_rate': (0.5, 2.0)
            }
        }
    
    def generate_driver_profile(self):
        """Generate base profile for a driver with realistic correlations"""
        age = np.random.randint(18, 70)
        
        # Adjust driving style probabilities based on age
        if age < 25:
            style_probs = [0.2, 0.5, 0.3]  # Higher chance of aggressive for young drivers
        elif age > 60:
            style_probs = [0.4, 0.5, 0.1]  # Lower chance of aggressive for older drivers
        else:
            style_probs = [0.3, 0.5, 0.2]  # Standard distribution
            
        driving_style = np.random.choice(
            ['conservative', 'moderate', 'aggressive'], 
            p=style_probs
        )
        
        # Vehicle type selection influenced by age and style
        if driving_style == 'aggressive':
            vehicle_probs = [0.3, 0.3, 0.3, 0.1]  # Higher chance of sports/suv
        elif age > 50:
            vehicle_probs = [0.5, 0.3, 0.05, 0.15]  # Higher chance of sedan/suv
        else:
            vehicle_probs = [0.4, 0.3, 0.1, 0.2]  # Standard distribution
            
        vehicle_type = np.random.choice(
            ['sedan', 'suv', 'sports', 'compact'], 
            p=vehicle_probs
        )
        
        # Add license details
        license_number = f"DL{random.randint(100000, 999999)}"
        license_plate = f"KA{random.randint(10, 99)}M{random.randint(1000, 9999)}"
        
        return {
            'age': age,
            'driving_style': driving_style,
            'vehicle_type': vehicle_type,
            'years_of_experience': max(1, age - 18),
            'license_number': license_number,
            'license_plate': license_plate
        }
    
    def generate_monthly_metrics(self, profile):
        """Generate realistic monthly driving metrics based on profile"""
        style = profile['driving_style']
        profile_metrics = self.style_profiles[style]
        
        # Calculate base monthly kilometers
        daily_km_min, daily_km_max = profile_metrics['daily_km_range']
        total_km = np.random.uniform(daily_km_min * 30, daily_km_max * 30)
        
        # Calculate events based on rates per 100km
        braking_min, braking_max = profile_metrics['braking_rate']
        speeding_min, speeding_max = profile_metrics['speeding_rate']
        
        braking_rate = np.random.uniform(braking_min, braking_max)
        speeding_rate = np.random.uniform(speeding_min, speeding_max)
        
        sudden_braking_events = int(total_km * braking_rate / 100)
        speeding_events = int(total_km * speeding_rate / 100)
        
        # Generate accidents based on profile probabilities
        previous_accidents = np.random.choice(
            [0, 1, 2, 3], 
            p=profile_metrics['accident_prob']
        )
        
        # Generate traffic fines
        fine_min, fine_max = profile_metrics['fine_rate']
        traffic_fines = int(np.random.uniform(fine_min, fine_max))
        
        # Add some random variation (5% chance of missing data)
        if random.random() < 0.05:
            sudden_braking_events = np.nan
        if random.random() < 0.05:
            speeding_events = np.nan
            
        return {
            'total_km': round(total_km, 2),
            'sudden_braking_events': sudden_braking_events,
            'speeding_events': speeding_events,
            'previous_accidents': previous_accidents,
            'traffic_fines': traffic_fines
        }
    
    def generate_driver_data(self):
        """Generate complete dataset for all drivers"""
        data = []
        
        for driver_id in range(1, self.num_drivers + 1):
            # Generate base profile
            profile = self.generate_driver_profile()
            
            # Generate monthly metrics
            metrics = self.generate_monthly_metrics(profile)
            
            # Combine all data
            driver_data = {
                'driver_id': driver_id,
                **profile,
                **metrics,
                'data_date': datetime.now().strftime('%Y-%m-%d')
            }
            
            data.append(driver_data)
        
        return pd.DataFrame(data)
    
    def save_to_csv(self, data, filepath='data/driver_data.csv'):
        """Save generated data to CSV file"""
        import os
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        data.to_csv(filepath, index=False)
        print(f"Data saved to {filepath}")

def main():
    # Generate and save data
    generator = DriverDataGenerator(num_drivers=100)
    driver_data = generator.generate_driver_data()
    generator.save_to_csv(driver_data)
    
    # Display data distribution
    print("\nDriving Style Distribution:")
    print(driver_data['driving_style'].value_counts(normalize=True) * 100)
    
    print("\nVehicle Type Distribution:")
    print(driver_data['vehicle_type'].value_counts(normalize=True) * 100)
    
    print("\nMetrics by Driving Style:")
    print(driver_data.groupby('driving_style')[
        ['total_km', 'sudden_braking_events', 'speeding_events', 'traffic_fines']
    ].mean())
    
    print("\nMissing Values:")
    print(driver_data.isnull().sum())

if __name__ == "__main__":
    main() 