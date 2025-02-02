import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.cluster import KMeans
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.metrics import confusion_matrix, classification_report, silhouette_score
from sklearn.impute import SimpleImputer
import matplotlib.pyplot as plt
import seaborn as sns

class DriverBehaviorAnalyzer:
    def __init__(self):
        # Classification models
        self.models = {
            'logistic': LogisticRegression(random_state=42),
            'decision_tree': DecisionTreeClassifier(random_state=42, max_depth=5),
            'random_forest': RandomForestClassifier(random_state=42, n_estimators=100)
        }
        # Clustering model
        self.kmeans = KMeans(n_clusters=3, random_state=42)
        
        self.scaler = StandardScaler()
        self.imputer = SimpleImputer(strategy='mean')
        self.trained_models = {}
        self.feature_names = None
        
    def prepare_data(self, data):
        """Prepare data for analysis"""
        features = [
            'sudden_braking_events', 'speeding_events', 
            'previous_accidents', 'traffic_fines',
            'total_km', 'age', 'years_of_experience'
        ]
        self.feature_names = features
        
        # Create binary target based on multiple risk factors
        # Calculate risk score from normalized features
        risk_factors = data[['sudden_braking_events', 'speeding_events', 'previous_accidents', 'traffic_fines']]
        normalized_factors = (risk_factors - risk_factors.mean()) / risk_factors.std()
        risk_score = normalized_factors.mean(axis=1)
        
        # Create binary target (Safe/Abnormal) based on risk score
        risk_threshold = risk_score.median()
        y = (risk_score > risk_threshold).astype(int)
        y = y.map({0: 'Safe', 1: 'Abnormal'})
        
        # Prepare feature matrix
        X = data[features]
        X = self.imputer.fit_transform(X)
        X_scaled = self.scaler.fit_transform(X)
        
        return X_scaled, X, y
    
    def train_classifiers(self, X, y):
        """Train and evaluate classification models"""
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        results = {}
        for name, model in self.models.items():
            # Train model
            model.fit(X_train, y_train)
            self.trained_models[name] = model
            
            # Make predictions
            y_pred = model.predict(X_test)
            
            # Calculate metrics
            results[name] = {
                'accuracy': accuracy_score(y_test, y_pred),
                'precision': precision_score(y_test, y_pred, pos_label='Abnormal'),
                'recall': recall_score(y_test, y_pred, pos_label='Abnormal'),
                'f1': f1_score(y_test, y_pred, pos_label='Abnormal'),
                'confusion_matrix': confusion_matrix(y_test, y_pred),
                'classification_report': classification_report(y_test, y_pred),
                'feature_importance': self.get_feature_importance(name, model)
            }
        
        return results
    
    def perform_clustering(self, X, original_data):
        """Perform K-means clustering and analyze results"""
        # Fit K-means
        cluster_labels = self.kmeans.fit_predict(X)
        
        # Calculate cluster centers and silhouette score
        centers = self.kmeans.cluster_centers_
        silhouette_avg = silhouette_score(X, cluster_labels)
        
        # Map clusters to risk levels based on center values
        center_risks = np.mean(centers, axis=1)
        risk_mapping = {
            np.argmin(center_risks): 'Low Risk',
            np.argsort(center_risks)[1]: 'Moderate Risk',
            np.argmax(center_risks): 'High Risk'
        }
        
        # Add cluster labels to original data
        cluster_results = original_data.copy()
        cluster_results['risk_cluster'] = cluster_labels
        cluster_results['risk_level'] = cluster_results['risk_cluster'].map(risk_mapping)
        
        # Calculate cluster statistics
        cluster_stats = cluster_results.groupby('risk_level').agg({
            'sudden_braking_events': 'mean',
            'speeding_events': 'mean',
            'previous_accidents': 'mean',
            'traffic_fines': 'mean',
            'driver_id': 'count'
        }).round(2)
        
        return {
            'cluster_results': cluster_results,
            'cluster_stats': cluster_stats,
            'silhouette_score': silhouette_avg,
            'risk_mapping': risk_mapping
        }
    
    def get_feature_importance(self, model_name, model):
        """Get feature importance for classification models"""
        if model_name == 'logistic':
            importance = model.coef_[0]
        else:
            importance = model.feature_importances_
        return dict(zip(self.feature_names, importance))
    
    def plot_results(self, classification_results, clustering_results, save_path='data/ml_results/'):
        """Plot comprehensive analysis results"""
        import os
        os.makedirs(save_path, exist_ok=True)
        
        # Remove the plt.style.use line completely
        # seaborn import will automatically set better styling
        
        # 1. Classification Results
        # Confusion matrices with improved layout
        fig, axes = plt.subplots(1, 3, figsize=(18, 6))
        for i, (name, metrics) in enumerate(classification_results.items()):
            sns.heatmap(metrics['confusion_matrix'], 
                       annot=True, 
                       fmt='d',
                       cmap='Blues',
                       ax=axes[i],
                       xticklabels=['Safe', 'Abnormal'],
                       yticklabels=['Safe', 'Abnormal'])
            axes[i].set_title(f'{name.title()} Confusion Matrix')
            axes[i].set_xlabel('Predicted')
            axes[i].set_ylabel('Actual')
        plt.tight_layout()
        plt.savefig(f'{save_path}confusion_matrices.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # Feature importance comparison
        plt.figure(figsize=(12, 6))
        x = np.arange(len(self.feature_names))
        width = 0.25
        for i, (name, metrics) in enumerate(classification_results.items()):
            importance = metrics['feature_importance']
            plt.bar(x + i*width, 
                   list(importance.values()), 
                   width, 
                   label=name.title())
        
        plt.xlabel('Features')
        plt.ylabel('Importance Score')
        plt.title('Feature Importance Comparison Across Models')
        plt.xticks(x + width, self.feature_names, rotation=45, ha='right')
        plt.legend()
        plt.tight_layout()
        plt.savefig(f'{save_path}feature_importance.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 2. Clustering Results
        # Risk level distribution with percentages
        plt.figure(figsize=(10, 6))
        cluster_counts = clustering_results['cluster_results']['risk_level'].value_counts()
        total = len(clustering_results['cluster_results'])
        percentages = [f'{(count/total)*100:.1f}%' for count in cluster_counts]
        
        ax = cluster_counts.plot(kind='bar', color=['green', 'yellow', 'red'])
        plt.title('Distribution of Risk Levels')
        plt.xlabel('Risk Level')
        plt.ylabel('Number of Drivers')
        
        # Add percentage labels on bars
        for i, (count, percentage) in enumerate(zip(cluster_counts, percentages)):
            ax.text(i, count, percentage, ha='center', va='bottom')
            
        plt.tight_layout()
        plt.savefig(f'{save_path}risk_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 3. Model Performance Comparison
        plt.figure(figsize=(10, 6))
        metrics = ['accuracy', 'precision', 'recall', 'f1']
        x = np.arange(len(metrics))
        width = 0.25
        
        for i, (name, results) in enumerate(classification_results.items()):
            performance = [results[metric] for metric in metrics]
            plt.bar(x + i*width, performance, width, label=name.title())
        
        plt.xlabel('Metrics')
        plt.ylabel('Score')
        plt.title('Model Performance Comparison')
        plt.xticks(x + width, metrics)
        plt.legend()
        plt.tight_layout()
        plt.savefig(f'{save_path}model_performance.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 4. Cluster Characteristics
        plt.figure(figsize=(12, 6))
        cluster_stats = clustering_results['cluster_stats']
        cluster_stats.drop('driver_id', axis=1).plot(kind='bar')
        plt.title('Characteristics of Risk Clusters')
        plt.xlabel('Risk Level')
        plt.ylabel('Average Value')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        plt.savefig(f'{save_path}cluster_characteristics.png', dpi=300, bbox_inches='tight')
        plt.close()

def main():
    try:
        # Load data
        data = pd.read_csv('data/driver_data_with_risks.csv')
        
        # Initialize analyzer
        analyzer = DriverBehaviorAnalyzer()
        
        # Prepare data
        X_scaled, X_original, y = analyzer.prepare_data(data)
        
        # Perform classification
        classification_results = analyzer.train_classifiers(X_scaled, y)
        
        # Perform clustering
        clustering_results = analyzer.perform_clustering(X_scaled, data)
        
        # Display classification results
        print("\nClassification Model Performance:")
        for model_name, metrics in classification_results.items():
            print(f"\n{model_name.upper()}:")
            print(f"Accuracy: {metrics['accuracy']:.3f}")
            print(f"Precision: {metrics['precision']:.3f}")
            print(f"Recall: {metrics['recall']:.3f}")
            print(f"F1 Score: {metrics['f1']:.3f}")
            print("\nClassification Report:")
            print(metrics['classification_report'])
        
        # Display clustering results
        print("\nClustering Results:")
        print("\nCluster Statistics:")
        print(clustering_results['cluster_stats'])
        print(f"\nSilhouette Score: {clustering_results['silhouette_score']:.3f}")
        
        # Plot results
        analyzer.plot_results(classification_results, clustering_results)
        print("\nVisualization plots have been saved to 'data/ml_results/'")
        
        # Save results
        clustering_results['cluster_results'].to_csv('data/driver_risk_clusters.csv', index=False)
        
    except FileNotFoundError:
        print("Error: Required data files not found. Please run previous steps first.")

if __name__ == "__main__":
    main() 