import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer

class RiskAnalyzer:
    def __init__(self, data):
        self.data = data
        self.scaler = StandardScaler()
        self.imputer = SimpleImputer(strategy='mean')
        self.kmeans = None
        
    def preprocess_data(self):
        """Preprocess data by handling missing values and scaling"""
        features = ['sudden_braking_events', 'speeding_events', 
                   'previous_accidents', 'traffic_fines', 'total_km']
        
        # Handle missing values
        X = self.imputer.fit_transform(self.data[features])
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        return X_scaled, features
    
    def cluster_drivers(self, n_clusters=3):
        """Cluster drivers into risk categories using K-means"""
        X_scaled, features = self.preprocess_data()
        
        # Perform K-means clustering
        self.kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        clusters = self.kmeans.fit_predict(X_scaled)
        
        # Add cluster labels to the original dataframe
        self.data['risk_cluster'] = clusters
        
        # Map clusters to risk categories based on centroid values
        centroids = self.kmeans.cluster_centers_
        risk_levels = ['Low', 'Moderate', 'High']
        
        # Calculate average risk score for each cluster
        cluster_risks = []
        for i in range(n_clusters):
            cluster_risk = np.mean(centroids[i])
            cluster_risks.append((i, cluster_risk))
        
        # Sort clusters by risk level
        cluster_risks.sort(key=lambda x: x[1])
        cluster_mapping = {cluster: risk for (cluster, _), risk in zip(cluster_risks, risk_levels)}
        
        # Map cluster numbers to risk levels
        self.data['risk_category'] = self.data['risk_cluster'].map(cluster_mapping)
        
        return self.data
    
    def calculate_risk_metrics(self):
        """Calculate additional risk metrics"""
        # Calculate normalized risk scores for each feature
        self.data['braking_risk'] = self.data['sudden_braking_events'] / self.data['total_km'] * 1000
        self.data['speeding_risk'] = self.data['speeding_events'] / self.data['total_km'] * 1000
        
        # Calculate experience factor (higher experience reduces risk)
        self.data['experience_factor'] = 1 - (self.data['years_of_experience'] / self.data['years_of_experience'].max())
        
        # Calculate comprehensive risk score
        self.data['comprehensive_risk_score'] = (
            self.data['braking_risk'] * 0.25 +
            self.data['speeding_risk'] * 0.25 +
            self.data['previous_accidents'] * 0.3 +
            self.data['experience_factor'] * 0.2
        )
        
        return self.data
    
    def get_risk_summary(self):
        """Generate summary statistics for risk categories"""
        summary = self.data.groupby('risk_category').agg({
            'comprehensive_risk_score': ['mean', 'count'],
            'previous_accidents': 'mean',
            'total_km': 'mean'
        }).round(2)
        
        return summary

def main():
    # Load sample data
    try:
        data = pd.read_csv('data/driver_data.csv')
        
        # Initialize and run risk analysis
        analyzer = RiskAnalyzer(data)
        
        # Perform clustering and risk analysis
        data_with_risks = analyzer.cluster_drivers()
        data_with_metrics = analyzer.calculate_risk_metrics()
        
        # Display summary
        print("\nRisk Category Summary:")
        print(analyzer.get_risk_summary())
        
        # Save enriched data
        data_with_metrics.to_csv('data/driver_data_with_risks.csv', index=False)
        print("\nEnriched data saved to 'data/driver_data_with_risks.csv'")
        
    except FileNotFoundError:
        print("Error: Please generate driver data first using data_generator.py")

if __name__ == "__main__":
    main() 