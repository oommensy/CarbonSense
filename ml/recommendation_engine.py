"""
CarbonSense AI Recommendations Engine
Provides personalized carbon reduction suggestions using machine learning
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, accuracy_score
import joblib
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple, Optional
import json
import os

class CarbonRecommendationEngine:
    """AI-powered recommendations for carbon footprint reduction"""
    
    def __init__(self, model_path: str = "models/"):
        self.model_path = model_path
        self.emission_factors = {
            'transport': {
                'car_gasoline': 0.21,  # kg CO2 per km
                'car_electric': 0.05,
                'bus': 0.089,
                'train': 0.041,
                'bicycle': 0.0,
                'walking': 0.0,
                'flight_domestic': 0.255,
                'flight_international': 0.298
            },
            'food': {
                'beef': 27.0,  # kg CO2 per kg
                'lamb': 39.2,
                'pork': 12.1,
                'chicken': 6.9,
                'fish': 6.1,
                'eggs': 4.2,
                'dairy': 3.2,
                'vegetables': 2.0,
                'fruits': 1.1,
                'grains': 1.4
            },
            'energy': {
                'electricity_grid': 0.5,  # kg CO2 per kWh
                'electricity_renewable': 0.02,
                'natural_gas': 2.04,
                'heating_oil': 2.52,
                'coal': 2.86
            },
            'waste': {
                'landfill': 0.57,  # kg CO2 per kg
                'recycling': 0.1,
                'composting': 0.05
            }
        }
        
        # Initialize models
        self.carbon_predictor = None
        self.recommendation_classifier = None
        self.user_clusterer = None
        self.scaler = StandardScaler()
        
        # Create model directory if it doesn't exist
        os.makedirs(model_path, exist_ok=True)
        
        # Load existing models or create new ones
        self._load_or_create_models()
    
    def _load_or_create_models(self):
        """Load existing models or create and train new ones"""
        try:
            # Try to load existing models
            self.carbon_predictor = joblib.load(f"{self.model_path}/carbon_predictor.pkl")
            self.recommendation_classifier = joblib.load(f"{self.model_path}/recommendation_classifier.pkl")
            self.user_clusterer = joblib.load(f"{self.model_path}/user_clusterer.pkl")
            self.scaler = joblib.load(f"{self.model_path}/scaler.pkl")
            print("Loaded existing ML models")
        except FileNotFoundError:
            print("Training new ML models...")
            self._train_models()
    
    def _generate_synthetic_data(self, n_samples: int = 10000) -> Tuple[pd.DataFrame, np.ndarray]:
        """Generate synthetic training data"""
        np.random.seed(42)
        
        # User demographics and behavior patterns
        users = []
        for i in range(n_samples):
            user = {
                # Demographics
                'age': np.random.normal(35, 15),
                'income': np.random.lognormal(10, 0.5),
                'household_size': np.random.randint(1, 6),
                'urban': np.random.choice([0, 1], p=[0.3, 0.7]),
                
                # Transport patterns
                'car_km_week': np.random.gamma(2, 50),
                'public_transport_usage': np.random.beta(2, 5),
                'flights_per_year': np.random.poisson(2),
                
                # Energy patterns
                'home_kwh_month': np.random.gamma(3, 150),
                'renewable_energy': np.random.choice([0, 1], p=[0.8, 0.2]),
                'heating_type': np.random.choice([0, 1, 2], p=[0.5, 0.3, 0.2]),  # gas, electric, oil
                
                # Food patterns
                'meat_meals_week': np.random.poisson(10),
                'local_food_ratio': np.random.beta(3, 5),
                'organic_food_ratio': np.random.beta(2, 8),
                
                # Waste patterns
                'waste_kg_week': np.random.gamma(2, 5),
                'recycling_ratio': np.random.beta(4, 3),
                
                # Behavioral factors
                'environmental_concern': np.random.beta(3, 2),
                'tech_adoption': np.random.beta(2, 3),
                'social_influence': np.random.beta(3, 3),
            }
            users.append(user)
        
        df = pd.DataFrame(users)
        
        # Calculate carbon footprint based on activities
        carbon_footprint = (
            df['car_km_week'] * 52 * 0.21 +  # Car transport
            df['flights_per_year'] * 500 * 0.25 +  # Flights
            df['home_kwh_month'] * 12 * 0.5 +  # Electricity
            df['meat_meals_week'] * 52 * 2.5 +  # Food
            df['waste_kg_week'] * 52 * 0.3  # Waste
        )
        
        # Add some noise
        carbon_footprint += np.random.normal(0, 500, len(df))
        carbon_footprint = np.maximum(carbon_footprint, 1000)  # Minimum 1 ton per year
        
        return df, carbon_footprint
    
    def _train_models(self):
        """Train all ML models"""
        # Generate training data
        X, y = self._generate_synthetic_data()
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train carbon footprint predictor
        self.carbon_predictor = RandomForestRegressor(n_estimators=100, random_state=42)
        self.carbon_predictor.fit(X_train_scaled, y_train)
        
        # Evaluate predictor
        y_pred = self.carbon_predictor.predict(X_test_scaled)
        mse = mean_squared_error(y_test, y_pred)
        print(f"Carbon predictor MSE: {mse:.2f}")
        
        # Train user clusterer for recommendation targeting
        self.user_clusterer = KMeans(n_clusters=5, random_state=42)
        user_clusters = self.user_clusterer.fit_predict(X_train_scaled)
        
        # Create recommendation labels based on user characteristics
        recommendation_labels = []
        for i, row in X_train.iterrows():
            if row['car_km_week'] > 200:
                recommendation_labels.append(0)  # Transport recommendations
            elif row['home_kwh_month'] > 400:
                recommendation_labels.append(1)  # Energy recommendations
            elif row['meat_meals_week'] > 12:
                recommendation_labels.append(2)  # Food recommendations
            elif row['recycling_ratio'] < 0.5:
                recommendation_labels.append(3)  # Waste recommendations
            else:
                recommendation_labels.append(4)  # General recommendations
        
        # Train recommendation classifier
        self.recommendation_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        self.recommendation_classifier.fit(X_train_scaled, recommendation_labels)
        
        # Evaluate classifier
        test_labels = []
        for i, row in X_test.iterrows():
            if row['car_km_week'] > 200:
                test_labels.append(0)
            elif row['home_kwh_month'] > 400:
                test_labels.append(1)
            elif row['meat_meals_week'] > 12:
                test_labels.append(2)
            elif row['recycling_ratio'] < 0.5:
                test_labels.append(3)
            else:
                test_labels.append(4)
        
        rec_pred = self.recommendation_classifier.predict(X_test_scaled)
        accuracy = accuracy_score(test_labels, rec_pred)
        print(f"Recommendation classifier accuracy: {accuracy:.2f}")
        
        # Save models
        joblib.dump(self.carbon_predictor, f"{self.model_path}/carbon_predictor.pkl")
        joblib.dump(self.recommendation_classifier, f"{self.model_path}/recommendation_classifier.pkl")
        joblib.dump(self.user_clusterer, f"{self.model_path}/user_clusterer.pkl")
        joblib.dump(self.scaler, f"{self.model_path}/scaler.pkl")
        
        print("Models trained and saved successfully")
    
    def predict_carbon_footprint(self, user_features: Dict[str, Any]) -> float:
        """Predict user's annual carbon footprint"""
        if self.carbon_predictor is None:
            return 8000.0  # Default estimate
        
        # Convert features to DataFrame
        feature_df = pd.DataFrame([user_features])
        
        # Ensure all required features are present
        required_features = ['age', 'income', 'household_size', 'urban', 'car_km_week',
                           'public_transport_usage', 'flights_per_year', 'home_kwh_month',
                           'renewable_energy', 'heating_type', 'meat_meals_week',
                           'local_food_ratio', 'organic_food_ratio', 'waste_kg_week',
                           'recycling_ratio', 'environmental_concern', 'tech_adoption',
                           'social_influence']
        
        for feature in required_features:
            if feature not in feature_df.columns:
                feature_df[feature] = 0.5  # Default value
        
        feature_df = feature_df[required_features]
        
        # Scale features
        features_scaled = self.scaler.transform(feature_df)
        
        # Predict
        prediction = self.carbon_predictor.predict(features_scaled)[0]
        return max(prediction, 1000.0)  # Minimum 1 ton per year
    
    def get_recommendations(self, user_data: Dict[str, Any], user_entries: List[Dict]) -> List[Dict[str, Any]]:
        """Generate personalized recommendations for carbon reduction"""
        
        # Extract user features for ML prediction
        user_features = self._extract_user_features(user_data, user_entries)
        
        # Get recommendation category from classifier
        if self.recommendation_classifier is not None:
            feature_df = pd.DataFrame([user_features])
            required_features = ['age', 'income', 'household_size', 'urban', 'car_km_week',
                               'public_transport_usage', 'flights_per_year', 'home_kwh_month',
                               'renewable_energy', 'heating_type', 'meat_meals_week',
                               'local_food_ratio', 'organic_food_ratio', 'waste_kg_week',
                               'recycling_ratio', 'environmental_concern', 'tech_adoption',
                               'social_influence']
            
            for feature in required_features:
                if feature not in feature_df.columns:
                    feature_df[feature] = 0.5
            
            feature_df = feature_df[required_features]
            features_scaled = self.scaler.transform(feature_df)
            
            rec_category = self.recommendation_classifier.predict(features_scaled)[0]
        else:
            rec_category = 0
        
        # Analyze user's carbon entries
        carbon_analysis = self._analyze_carbon_entries(user_entries)
        
        # Generate recommendations based on analysis
        recommendations = []
        
        # Transport recommendations
        if rec_category == 0 or carbon_analysis['transport']['percentage'] > 30:
            transport_recs = self._get_transport_recommendations(carbon_analysis['transport'])
            recommendations.extend(transport_recs)
        
        # Energy recommendations
        if rec_category == 1 or carbon_analysis['energy']['percentage'] > 25:
            energy_recs = self._get_energy_recommendations(carbon_analysis['energy'])
            recommendations.extend(energy_recs)
        
        # Food recommendations
        if rec_category == 2 or carbon_analysis['food']['percentage'] > 20:
            food_recs = self._get_food_recommendations(carbon_analysis['food'])
            recommendations.extend(food_recs)
        
        # Waste recommendations
        if rec_category == 3 or carbon_analysis['waste']['percentage'] > 10:
            waste_recs = self._get_waste_recommendations(carbon_analysis['waste'])
            recommendations.extend(waste_recs)
        
        # Add general recommendations if not enough specific ones
        if len(recommendations) < 3:
            recommendations.extend(self._get_general_recommendations())
        
        # Sort by potential impact and return top 5
        recommendations.sort(key=lambda x: x['potential_co2_reduction'], reverse=True)
        return recommendations[:5]
    
    def _extract_user_features(self, user_data: Dict, user_entries: List[Dict]) -> Dict[str, float]:
        """Extract features from user data for ML models"""
        features = {
            'age': user_data.get('age', 35),
            'income': user_data.get('income', 50000),
            'household_size': user_data.get('household_size', 2),
            'urban': 1 if user_data.get('location_type') == 'urban' else 0,
            'environmental_concern': user_data.get('environmental_concern', 0.7),
            'tech_adoption': user_data.get('tech_adoption', 0.6),
            'social_influence': user_data.get('social_influence', 0.5),
        }
        
        # Calculate features from carbon entries
        if user_entries:
            # Transport patterns
            transport_entries = [e for e in user_entries if e.get('category') == 'transport']
            features['car_km_week'] = sum(e.get('amount', 0) for e in transport_entries 
                                         if 'car' in e.get('activity', '').lower()) / max(len(transport_entries) or 1, 1)
            features['public_transport_usage'] = len([e for e in transport_entries 
                                                    if any(t in e.get('activity', '').lower() 
                                                          for t in ['bus', 'train', 'subway'])]) / max(len(transport_entries) or 1, 1)
            features['flights_per_year'] = len([e for e in transport_entries 
                                              if 'flight' in e.get('activity', '').lower()]) * 4  # Estimate
            
            # Energy patterns
            energy_entries = [e for e in user_entries if e.get('category') == 'energy']
            features['home_kwh_month'] = sum(e.get('amount', 0) for e in energy_entries 
                                           if 'electricity' in e.get('activity', '').lower()) / max(len(energy_entries) or 1, 1)
            features['renewable_energy'] = 1 if any('renewable' in e.get('activity', '').lower() 
                                                   for e in energy_entries) else 0
            features['heating_type'] = 0  # Default to gas
            
            # Food patterns
            food_entries = [e for e in user_entries if e.get('category') == 'food']
            features['meat_meals_week'] = len([e for e in food_entries 
                                             if any(m in e.get('activity', '').lower() 
                                                   for m in ['beef', 'pork', 'chicken'])]) / 4  # Estimate weekly
            features['local_food_ratio'] = 0.3  # Default
            features['organic_food_ratio'] = 0.2  # Default
            
            # Waste patterns
            waste_entries = [e for e in user_entries if e.get('category') == 'waste']
            features['waste_kg_week'] = sum(e.get('amount', 0) for e in waste_entries) / max(len(waste_entries) or 1, 1)
            features['recycling_ratio'] = len([e for e in waste_entries 
                                             if 'recycling' in e.get('activity', '').lower()]) / max(len(waste_entries) or 1, 1)
        else:
            # Default values if no entries
            features.update({
                'car_km_week': 100,
                'public_transport_usage': 0.3,
                'flights_per_year': 2,
                'home_kwh_month': 300,
                'renewable_energy': 0,
                'heating_type': 0,
                'meat_meals_week': 8,
                'local_food_ratio': 0.3,
                'organic_food_ratio': 0.2,
                'waste_kg_week': 15,
                'recycling_ratio': 0.5,
            })
        
        return features
    
    def _analyze_carbon_entries(self, user_entries: List[Dict]) -> Dict[str, Any]:
        """Analyze carbon entries to extract insights"""
        if not user_entries:
            return {
                'transport': {'total': 0, 'percentage': 0, 'entries': []},
                'energy': {'total': 0, 'percentage': 0, 'entries': []},
                'food': {'total': 0, 'percentage': 0, 'entries': []},
                'waste': {'total': 0, 'percentage': 0, 'entries': []}
            }
        
        # Group entries by category
        categories = {}
        total_carbon = 0
        
        for entry in user_entries:
            category = entry.get('category', 'other')
            carbon = entry.get('carbon_footprint', 0)
            
            if category not in categories:
                categories[category] = {'total': 0, 'entries': []}
            
            categories[category]['total'] += carbon
            categories[category]['entries'].append(entry)
            total_carbon += carbon
        
        # Calculate percentages
        for category in categories:
            categories[category]['percentage'] = (categories[category]['total'] / total_carbon * 100) if total_carbon > 0 else 0
        
        # Ensure all main categories exist
        for cat in ['transport', 'energy', 'food', 'waste']:
            if cat not in categories:
                categories[cat] = {'total': 0, 'percentage': 0, 'entries': []}
        
        return categories
    
    def _get_transport_recommendations(self, transport_data: Dict) -> List[Dict[str, Any]]:
        """Get transport-specific recommendations"""
        recommendations = []
        
        if transport_data['total'] > 100:  # High transport emissions
            recommendations.append({
                'category': 'transport',
                'title': 'Switch to Public Transit',
                'description': 'Using public transit 2 days per week could reduce your transport emissions by 30%',
                'potential_co2_reduction': transport_data['total'] * 0.3,
                'difficulty': 'medium',
                'timeframe': 'immediate',
                'confidence': 0.85,
                'actions': [
                    'Research public transit routes',
                    'Buy a weekly transit pass',
                    'Plan transit days'
                ]
            })
        
        if transport_data['total'] > 50:
            recommendations.append({
                'category': 'transport',
                'title': 'Work From Home',
                'description': 'Remote work 1-2 days per week eliminates commute emissions',
                'potential_co2_reduction': transport_data['total'] * 0.4,
                'difficulty': 'easy',
                'timeframe': 'immediate',
                'confidence': 0.90,
                'actions': [
                    'Discuss WFH with manager',
                    'Set up home office',
                    'Plan WFH schedule'
                ]
            })
        
        return recommendations
    
    def _get_energy_recommendations(self, energy_data: Dict) -> List[Dict[str, Any]]:
        """Get energy-specific recommendations"""
        recommendations = []
        
        if energy_data['total'] > 80:
            recommendations.append({
                'category': 'energy',
                'title': 'Switch to Renewable Energy',
                'description': 'Green energy plans can reduce home emissions by 80%',
                'potential_co2_reduction': energy_data['total'] * 0.8,
                'difficulty': 'medium',
                'timeframe': '1-2 weeks',
                'confidence': 0.85,
                'actions': [
                    'Research green energy providers',
                    'Compare plan costs',
                    'Switch energy provider'
                ]
            })
        
        if energy_data['total'] > 40:
            recommendations.append({
                'category': 'energy',
                'title': 'LED Light Upgrade',
                'description': 'LED bulbs use 75% less energy than incandescent',
                'potential_co2_reduction': energy_data['total'] * 0.15,
                'difficulty': 'easy',
                'timeframe': '1 week',
                'confidence': 0.95,
                'actions': [
                    'Inventory current bulbs',
                    'Purchase LED replacements',
                    'Replace high-usage bulbs first'
                ]
            })
        
        return recommendations
    
    def _get_food_recommendations(self, food_data: Dict) -> List[Dict[str, Any]]:
        """Get food-specific recommendations"""
        recommendations = []
        
        if food_data['total'] > 60:
            recommendations.append({
                'category': 'food',
                'title': 'Meatless Monday',
                'description': 'Plant-based meals 1 day per week can reduce food emissions by 15%',
                'potential_co2_reduction': food_data['total'] * 0.15,
                'difficulty': 'easy',
                'timeframe': 'immediate',
                'confidence': 0.88,
                'actions': [
                    'Plan plant-based meals',
                    'Try meat alternatives',
                    'Explore vegetarian recipes'
                ]
            })
        
        if food_data['total'] > 100:
            recommendations.append({
                'category': 'food',
                'title': 'Local & Seasonal Food',
                'description': 'Buying local reduces transport emissions by 25%',
                'potential_co2_reduction': food_data['total'] * 0.25,
                'difficulty': 'medium',
                'timeframe': 'immediate',
                'confidence': 0.75,
                'actions': [
                    'Find local farmers markets',
                    'Join CSA program',
                    'Choose seasonal produce'
                ]
            })
        
        return recommendations
    
    def _get_waste_recommendations(self, waste_data: Dict) -> List[Dict[str, Any]]:
        """Get waste-specific recommendations"""
        recommendations = []
        
        if waste_data['total'] > 20:
            recommendations.append({
                'category': 'waste',
                'title': 'Increase Recycling',
                'description': 'Proper recycling can reduce waste emissions by 60%',
                'potential_co2_reduction': waste_data['total'] * 0.6,
                'difficulty': 'easy',
                'timeframe': 'immediate',
                'confidence': 0.85,
                'actions': [
                    'Learn local recycling rules',
                    'Set up recycling bins',
                    'Track recycling progress'
                ]
            })
        
        return recommendations
    
    def _get_general_recommendations(self) -> List[Dict[str, Any]]:
        """Get general carbon reduction recommendations"""
        return [
            {
                'category': 'lifestyle',
                'title': 'Carbon Offset Investment',
                'description': 'Offset remaining emissions with verified carbon credits',
                'potential_co2_reduction': 50.0,
                'difficulty': 'easy',
                'timeframe': 'immediate',
                'confidence': 0.95,
                'actions': [
                    'Calculate monthly footprint',
                    'Research offset providers',
                    'Set up offset subscription'
                ]
            },
            {
                'category': 'lifestyle',
                'title': 'Digital Carbon Tracking',
                'description': 'Regular tracking increases awareness and reduces emissions by 15%',
                'potential_co2_reduction': 30.0,
                'difficulty': 'easy',
                'timeframe': 'immediate',
                'confidence': 0.80,
                'actions': [
                    'Use carbon tracking apps',
                    'Set weekly tracking goals',
                    'Share progress with friends'
                ]
            }
        ]

# Initialize the model when module is imported
recommendation_engine = CarbonRecommendationEngine()

def get_user_recommendations(user_data: Dict, user_entries: List[Dict]) -> List[Dict[str, Any]]:
    """Main function to get recommendations for a user"""
    return recommendation_engine.get_recommendations(user_data, user_entries)

def predict_user_carbon_footprint(user_features: Dict[str, Any]) -> float:
    """Predict user's carbon footprint"""
    return recommendation_engine.predict_carbon_footprint(user_features)