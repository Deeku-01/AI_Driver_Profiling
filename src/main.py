import os
from functionalities.data_generator import DriverDataGenerator
from functionalities.risk_analysis import RiskAnalyzer
from functionalities.ml_models import DriverBehaviorAnalyzer
from functionalities.insurance_models import PremiumCalculator

def ensure_directory():
    """Ensure required directories exist"""
    directories = ['data', 'data/ml_results', 'data/sample_data']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

def main():
    print("Starting Driver Risk Analysis Pipeline...")
    
    try:
        # Step 1: Generate synthetic driver data
        print("\n1. Generating driver data...")
        generator = DriverDataGenerator(num_drivers=100)
        driver_data = generator.generate_driver_data()
        generator.save_to_csv(driver_data, 'data/driver_data.csv')
        
        # Step 2: Perform risk analysis
        print("\n2. Analyzing driver risks...")
        risk_analyzer = RiskAnalyzer(driver_data)
        data_with_risks = risk_analyzer.cluster_drivers()
        data_with_metrics = risk_analyzer.calculate_risk_metrics()
        data_with_metrics.to_csv('data/driver_data_with_risks.csv', index=False)
        
        # Step 3: Train ML models and analyze behavior
        print("\n3. Training ML models...")
        behavior_analyzer = DriverBehaviorAnalyzer()
        X_scaled, X_original, y = behavior_analyzer.prepare_data(data_with_metrics)
        classification_results = behavior_analyzer.train_classifiers(X_scaled, y)
        clustering_results = behavior_analyzer.perform_clustering(X_scaled, data_with_metrics)
        behavior_analyzer.plot_results(classification_results, clustering_results)
        
        # Step 4: Calculate insurance premiums
        print("\n4. Calculating insurance premiums...")
        premium_calculator = PremiumCalculator('data/driver_data_with_risks.csv')
        premium_results = premium_calculator.calculate_all_premiums()
        premium_results.to_csv('data/premium_calculations.csv', index=False)
        
        print("\nAnalysis pipeline completed successfully!")
        print("Results have been saved to the 'data' directory.")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    ensure_directory()
    main() 