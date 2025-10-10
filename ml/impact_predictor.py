"""
Impact Prediction Model for CarbonSense
Predicts carbon reduction impact using machine learning
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
from datetime import datetime, timedelta
import json
from typing import Dict, List, Any, Tuple

class CarbonImpactPredictor:
    """ML model to predict carbon footprint reduction impacts"""
    
    def __init__(self):
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.feature_columns = [
            'baseline_transport',
            'baseline_food', 
            'baseline_energy',
            'baseline_consumption',
            'user_age',
            'household_size',
            'income_level',
            'urban_rural',
            'previous_actions',
            'engagement_score'
        ]
        self.is_trained = False
    
    def generate_synthetic_data(self, n_samples: int = 10000) -> pd.DataFrame:
        """Generate synthetic training data for the model"""
        np.random.seed(42)
        
        data = {
            # Baseline emissions (kg CO2 per month)
            'baseline_transport': np.random.lognormal(4, 0.8, n_samples),
            'baseline_food': np.random.lognormal(3.5, 0.6, n_samples),
            'baseline_energy': np.random.lognormal(3.8, 0.7, n_samples),
            'baseline_consumption': np.random.lognormal(3.2, 0.9, n_samples),
            
            # User demographics
            'user_age': np.random.normal(40, 15, n_samples).clip(18, 80),
            'household_size': np.random.poisson(2.5, n_samples).clip(1, 8),
            'income_level': np.random.normal(70000, 30000, n_samples).clip(20000, 200000),
            'urban_rural': np.random.choice([0, 1], n_samples, p=[0.7, 0.3]),  # 0=urban, 1=rural
            
            # Behavioral factors
            'previous_actions': np.random.poisson(3, n_samples).clip(0, 20),
            'engagement_score': np.random.beta(2, 2, n_samples) * 100,
        }
        
        df = pd.DataFrame(data)
        
        # Generate target variable (actual reduction achieved)
        # More engaged users with higher baselines achieve better results
        baseline_total = (df['baseline_transport'] + df['baseline_food'] + 
                         df['baseline_energy'] + df['baseline_consumption'])
        
        # Reduction factors based on engagement and other factors
        engagement_factor = df['engagement_score'] / 100
        experience_factor = np.tanh(df['previous_actions'] / 10)
        demographic_factor = 1 + (df['user_age'] - 40) * 0.001 - df['household_size'] * 0.02
        
        # Maximum theoretical reduction with noise
        max_reduction = baseline_total * 0.4  # 40% max reduction
        actual_reduction = (max_reduction * engagement_factor * 
                          experience_factor * demographic_factor * 
                          np.random.normal(1, 0.2, n_samples))
        
        df['actual_reduction'] = actual_reduction.clip(0, baseline_total * 0.6)
        
        return df
    
    def train_model(self, data: pd.DataFrame = None):
        """Train the impact prediction model"""
        
        if data is None:
            print("Generating synthetic training data...")
            data = self.generate_synthetic_data()
        
        # Prepare features and target
        X = data[self.feature_columns]
        y = data['actual_reduction']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        print("Training impact prediction model...")
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate model
        y_pred = self.model.predict(X_test_scaled)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        print(f"Model Performance:")
        print(f"- Mean Absolute Error: {mae:.2f} kg CO2/month")
        print(f"- R² Score: {r2:.3f}")
        
        # Feature importance
        feature_importance = dict(zip(
            self.feature_columns,
            self.model.feature_importances_
        ))
        
        print("\nFeature Importance:")
        for feature, importance in sorted(feature_importance.items(), 
                                        key=lambda x: x[1], reverse=True):
            print(f"- {feature}: {importance:.3f}")
        
        self.is_trained = True
        return {'mae': mae, 'r2': r2, 'feature_importance': feature_importance}
    
    def predict_impact(self, user_profile: Dict[str, Any], 
                      actions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Predict carbon reduction impact for specific actions"""
        
        if not self.is_trained:
            print("Training model with synthetic data...")
            self.train_model()
        
        # Prepare user features
        user_features = np.array([[
            user_profile.get('baseline_transport', 100),
            user_profile.get('baseline_food', 80),
            user_profile.get('baseline_energy', 120),
            user_profile.get('baseline_consumption', 60),
            user_profile.get('user_age', 35),
            user_profile.get('household_size', 2),
            user_profile.get('income_level', 65000),
            user_profile.get('urban_rural', 0),
            user_profile.get('previous_actions', 5),
            user_profile.get('engagement_score', 75)
        ]])
        
        # Scale features
        user_features_scaled = self.scaler.transform(user_features)
        
        # Base prediction
        base_prediction = self.model.predict(user_features_scaled)[0]
        
        # Adjust predictions for specific actions
        action_impacts = []
        total_predicted_impact = 0
        
        for action in actions:
            # Action-specific multipliers
            action_multipliers = {
                'public_transit': 1.2,
                'plant_based_meals': 1.0,
                'renewable_energy': 1.5,
                'carpooling': 0.8,
                'energy_efficiency': 1.1,
                'local_food': 0.6,
                'waste_reduction': 0.7
            }
            
            action_type = action.get('type', 'default')
            multiplier = action_multipliers.get(action_type, 1.0)
            
            # Calculate action-specific impact
            category_baseline = user_profile.get(f"baseline_{action.get('category', 'transport')}", 50)
            action_impact = base_prediction * 0.1 * multiplier  # Each action contributes ~10% of base
            
            # Add uncertainty bounds
            uncertainty = action_impact * 0.2  # ±20% uncertainty
            
            action_result = {
                'action': action_type,
                'category': action.get('category', 'general'),
                'predicted_impact': round(action_impact, 2),
                'confidence_interval': [
                    round(action_impact - uncertainty, 2),
                    round(action_impact + uncertainty, 2)
                ],
                'confidence_score': min(0.95, 0.6 + multiplier * 0.2),
                'timeframe': action.get('timeframe', 'monthly')
            }
            
            action_impacts.append(action_result)
            total_predicted_impact += action_impact
        
        return {
            'user_id': user_profile.get('user_id', 'unknown'),
            'baseline_total': sum([
                user_profile.get('baseline_transport', 100),
                user_profile.get('baseline_food', 80),
                user_profile.get('baseline_energy', 120),
                user_profile.get('baseline_consumption', 60)
            ]),
            'predicted_total_reduction': round(total_predicted_impact, 2),
            'reduction_percentage': round(
                (total_predicted_impact / sum([
                    user_profile.get('baseline_transport', 100),
                    user_profile.get('baseline_food', 80),
                    user_profile.get('baseline_energy', 120),
                    user_profile.get('baseline_consumption', 60)
                ])) * 100, 1
            ),
            'action_impacts': action_impacts,
            'prediction_date': datetime.now().isoformat(),
            'model_confidence': 0.82
        }
    
    def save_model(self, filepath: str):
        """Save trained model to disk"""
        if self.is_trained:
            joblib.dump({
                'model': self.model,
                'scaler': self.scaler,
                'feature_columns': self.feature_columns
            }, filepath)
            print(f"Model saved to {filepath}")
        else:
            print("No trained model to save")
    
    def load_model(self, filepath: str):
        """Load trained model from disk"""
        try:
            data = joblib.load(filepath)
            self.model = data['model']
            self.scaler = data['scaler']
            self.feature_columns = data['feature_columns']
            self.is_trained = True
            print(f"Model loaded from {filepath}")
        except FileNotFoundError:
            print(f"Model file not found: {filepath}")

def get_demo_predictions():
    """Generate demo predictions for showcase"""
    
    predictor = CarbonImpactPredictor()
    
    # Demo user profile
    demo_profile = {
        'user_id': 'demo-user',
        'baseline_transport': 120,  # kg CO2/month
        'baseline_food': 90,
        'baseline_energy': 150,
        'baseline_consumption': 70,
        'user_age': 32,
        'household_size': 2,
        'income_level': 75000,
        'urban_rural': 0,  # urban
        'previous_actions': 3,
        'engagement_score': 80
    }
    
    # Demo actions
    demo_actions = [
        {
            'type': 'public_transit',
            'category': 'transport',
            'description': 'Use public transit 3 days/week',
            'timeframe': 'monthly'
        },
        {
            'type': 'plant_based_meals',
            'category': 'food',
            'description': 'Plant-based meals 4 days/week',
            'timeframe': 'monthly'
        },
        {
            'type': 'renewable_energy',
            'category': 'energy',
            'description': 'Switch to renewable energy plan',
            'timeframe': 'monthly'
        }
    ]
    
    # Get predictions
    predictions = predictor.predict_impact(demo_profile, demo_actions)
    
    return predictions

if __name__ == "__main__":
    # Generate and display demo predictions
    demo_results = get_demo_predictions()
    print(json.dumps(demo_results, indent=2, default=str))