"""
Demo Data Generator for CarbonSense
Generates realistic and compelling demo data for showcasing the platform
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any
import random
import uuid

class CarbonSenseDemoDataGenerator:
    """Generates comprehensive demo data for all CarbonSense features"""
    
    def __init__(self):
        self.demo_users = self._create_demo_users()
        self.demo_companies = self._create_demo_companies()
        self.start_date = datetime.now() - timedelta(days=365)
        
    def _create_demo_users(self) -> List[Dict[str, Any]]:
        """Create diverse demo user profiles"""
        return [
            {
                'id': 'user_001',
                'name': 'Alex Chen',
                'email': 'alex@example.com',
                'age': 29,
                'location': 'San Francisco, CA',
                'occupation': 'Software Engineer',
                'household_size': 2,
                'income_level': 95000,
                'engagement_level': 'high',
                'motivation': 'environmental_impact',
                'baseline_emissions': {
                    'transport': 120,  # kg CO2/month
                    'food': 95,
                    'energy': 145,
                    'consumption': 65
                }
            },
            {
                'id': 'user_002',
                'name': 'Sarah Johnson',
                'email': 'sarah@example.com',
                'age': 34,
                'location': 'Austin, TX',
                'occupation': 'Marketing Manager',
                'household_size': 4,
                'income_level': 78000,
                'engagement_level': 'medium',
                'motivation': 'cost_savings',
                'baseline_emissions': {
                    'transport': 180,
                    'food': 140,
                    'energy': 220,
                    'consumption': 95
                }
            },
            {
                'id': 'user_003',
                'name': 'Mike Rodriguez',
                'email': 'mike@example.com',
                'age': 42,
                'location': 'Denver, CO',
                'occupation': 'Construction Manager',
                'household_size': 3,
                'income_level': 68000,
                'engagement_level': 'low',
                'motivation': 'family_future',
                'baseline_emissions': {
                    'transport': 240,
                    'food': 165,
                    'energy': 190,
                    'consumption': 110
                }
            },
            {
                'id': 'user_004',
                'name': 'Emma Wilson',
                'email': 'emma@example.com',
                'age': 26,
                'location': 'Portland, OR',
                'occupation': 'Environmental Scientist',
                'household_size': 1,
                'income_level': 52000,
                'engagement_level': 'very_high',
                'motivation': 'environmental_impact',
                'baseline_emissions': {
                    'transport': 45,
                    'food': 35,
                    'energy': 85,
                    'consumption': 25
                }
            }
        ]
    
    def _create_demo_companies(self) -> List[Dict[str, Any]]:
        """Create demo company profiles"""
        return [
            {
                'id': 'company_001',
                'name': 'TechCorp Solutions',
                'industry': 'Technology',
                'size': 'medium',
                'employee_count': 250,
                'location': 'San Francisco, CA',
                'sustainability_tier': 'advanced',
                'annual_revenue': 50000000,
                'esg_score': 78,
                'carbon_intensity': 2.3  # tons CO2/employee/year
            },
            {
                'id': 'company_002',
                'name': 'GreenEnergy Co',
                'industry': 'Renewable Energy',
                'size': 'large',
                'employee_count': 850,
                'location': 'Austin, TX',
                'sustainability_tier': 'leader',
                'annual_revenue': 200000000,
                'esg_score': 92,
                'carbon_intensity': 0.8
            },
            {
                'id': 'company_003',
                'name': 'ManufacturingPlus',
                'industry': 'Manufacturing',
                'size': 'large',
                'employee_count': 1200,
                'location': 'Detroit, MI',
                'sustainability_tier': 'developing',
                'annual_revenue': 300000000,
                'esg_score': 54,
                'carbon_intensity': 5.2
            }
        ]
    
    def generate_user_carbon_timeline(self, user_id: str, days: int = 365) -> List[Dict[str, Any]]:
        """Generate realistic carbon footprint timeline for a user"""
        
        user = next((u for u in self.demo_users if u['id'] == user_id), self.demo_users[0])
        baseline = user['baseline_emissions']
        engagement = user['engagement_level']
        
        # Engagement multipliers affect improvement over time
        engagement_factors = {
            'very_high': 0.85,  # 15% reduction over time
            'high': 0.90,       # 10% reduction
            'medium': 0.95,     # 5% reduction
            'low': 0.98         # 2% reduction
        }
        
        improvement_factor = engagement_factors.get(engagement, 0.95)
        
        timeline = []
        current_date = self.start_date
        
        for day in range(days):
            # Apply gradual improvement
            progress = day / days
            daily_factor = 1 - (1 - improvement_factor) * progress
            
            # Add seasonal variations
            month = current_date.month
            seasonal_transport = 1.0
            seasonal_energy = 1.0
            
            if month in [12, 1, 2]:  # Winter
                seasonal_energy = 1.3
                seasonal_transport = 0.9
            elif month in [6, 7, 8]:  # Summer
                seasonal_energy = 1.2
                seasonal_transport = 1.1
            
            # Add weekly patterns
            weekday = current_date.weekday()
            weekly_transport = 1.2 if weekday < 5 else 0.6  # Work vs weekend
            weekly_consumption = 0.8 if weekday < 5 else 1.3
            
            # Calculate daily emissions with realistic variations
            daily_emissions = {
                'transport': max(0, baseline['transport'] / 30 * daily_factor * 
                               seasonal_transport * weekly_transport * 
                               random.gauss(1, 0.2)),
                'food': max(0, baseline['food'] / 30 * daily_factor * 
                          random.gauss(1, 0.15)),
                'energy': max(0, baseline['energy'] / 30 * daily_factor * 
                            seasonal_energy * random.gauss(1, 0.25)),
                'consumption': max(0, baseline['consumption'] / 30 * daily_factor * 
                                 weekly_consumption * random.gauss(1, 0.3))
            }
            
            total_daily = sum(daily_emissions.values())
            
            timeline.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'user_id': user_id,
                'emissions': daily_emissions,
                'total': round(total_daily, 2),
                'weather_factor': random.uniform(0.9, 1.1),
                'verified_percentage': min(95, 60 + progress * 35)
            })
            
            current_date += timedelta(days=1)
        
        return timeline
    
    def generate_challenge_participation_data(self) -> List[Dict[str, Any]]:
        """Generate realistic challenge participation and completion data"""
        
        challenges = [
            {
                'id': 'challenge_001',
                'title': 'Car-Free Week',
                'type': 'individual',
                'difficulty': 'medium',
                'category': 'transport',
                'duration': 7,
                'points': 500,
                'completion_rate': 68,
                'participants': 1247,
                'carbon_impact': 15.2  # avg kg CO2 saved per participant
            },
            {
                'id': 'challenge_002',
                'title': 'Plant-Based Month',
                'type': 'individual',
                'difficulty': 'easy',
                'category': 'food',
                'duration': 30,
                'points': 800,
                'completion_rate': 82,
                'participants': 2156,
                'carbon_impact': 22.5
            },
            {
                'id': 'challenge_003',
                'title': 'Team Zero Waste',
                'type': 'team',
                'difficulty': 'hard',
                'category': 'consumption',
                'duration': 30,
                'points': 1200,
                'completion_rate': 45,
                'participants': 89,
                'carbon_impact': 35.8
            },
            {
                'id': 'challenge_004',
                'title': 'Energy Efficiency Sprint',
                'type': 'individual',
                'difficulty': 'medium',
                'category': 'energy',
                'duration': 14,
                'points': 600,
                'completion_rate': 71,
                'participants': 892,
                'carbon_impact': 18.3
            }
        ]
        
        participation_data = []
        
        for challenge in challenges:
            # Generate individual participation records
            for i in range(min(challenge['participants'], 100)):  # Limit for demo
                user_id = random.choice([u['id'] for u in self.demo_users])
                start_date = self.start_date + timedelta(days=random.randint(0, 300))
                
                # Determine completion based on challenge completion rate
                completed = random.random() < (challenge['completion_rate'] / 100)
                progress = 100 if completed else random.randint(20, 95)
                
                participation_data.append({
                    'challenge_id': challenge['id'],
                    'user_id': user_id,
                    'start_date': start_date.strftime('%Y-%m-%d'),
                    'end_date': (start_date + timedelta(days=challenge['duration'])).strftime('%Y-%m-%d'),
                    'progress': progress,
                    'completed': completed,
                    'points_earned': challenge['points'] if completed else int(challenge['points'] * progress / 100),
                    'carbon_saved': challenge['carbon_impact'] if completed else challenge['carbon_impact'] * progress / 100
                })
        
        return participation_data
    
    def generate_corporate_engagement_data(self, company_id: str) -> Dict[str, Any]:
        """Generate corporate engagement metrics"""
        
        company = next((c for c in self.demo_companies if c['id'] == company_id), self.demo_companies[0])
        employee_count = company['employee_count']
        
        # Generate monthly engagement data
        monthly_data = []
        current_date = self.start_date
        
        for month in range(12):
            participation_rate = min(85, 30 + month * 4 + random.randint(-5, 5))
            active_users = int(employee_count * participation_rate / 100)
            
            monthly_data.append({
                'month': current_date.strftime('%Y-%m'),
                'participation_rate': participation_rate,
                'active_users': active_users,
                'challenges_completed': random.randint(5, 25),
                'carbon_saved': random.uniform(1200, 4500),  # kg CO2
                'cost_savings': random.uniform(8000, 25000),  # USD
                'engagement_score': min(95, 60 + month * 3 + random.randint(-5, 10))
            })
            
            current_date += timedelta(days=30)
        
        # Department breakdown
        departments = [
            {'name': 'Engineering', 'size': 0.35, 'engagement': 'high'},
            {'name': 'Sales', 'size': 0.20, 'engagement': 'medium'},
            {'name': 'Marketing', 'size': 0.15, 'engagement': 'high'},
            {'name': 'Operations', 'size': 0.15, 'engagement': 'medium'},
            {'name': 'HR', 'size': 0.08, 'engagement': 'very_high'},
            {'name': 'Finance', 'size': 0.07, 'engagement': 'low'}
        ]
        
        department_data = []
        for dept in departments:
            dept_size = int(employee_count * dept['size'])
            engagement_multipliers = {
                'very_high': 1.4,
                'high': 1.2,
                'medium': 1.0,
                'low': 0.7
            }
            base_participation = 55
            dept_participation = min(95, base_participation * engagement_multipliers[dept['engagement']])
            
            department_data.append({
                'department': dept['name'],
                'employee_count': dept_size,
                'participation_rate': round(dept_participation, 1),
                'active_users': int(dept_size * dept_participation / 100),
                'avg_carbon_reduction': random.uniform(15, 45),
                'top_performer': f"{dept['name']} Employee #{random.randint(1, dept_size)}"
            })
        
        return {
            'company_id': company_id,
            'company_name': company['name'],
            'total_employees': employee_count,
            'overall_participation': round(sum(d['participation_rate'] for d in department_data) / len(department_data), 1),
            'total_carbon_saved': sum(d['carbon_saved'] for d in monthly_data),
            'total_cost_savings': sum(d['cost_savings'] for d in monthly_data),
            'monthly_trends': monthly_data,
            'department_breakdown': department_data,
            'top_achievements': [
                'Reached 80% employee participation',
                'Saved 28.5 tons CO2 this quarter',
                'Ranked #3 in industry sustainability',
                'Achieved carbon neutral office operations'
            ],
            'esg_impact': {
                'carbon_intensity_reduction': 22,  # percentage
                'renewable_energy_adoption': 85,
                'waste_diversion_rate': 78,
                'employee_satisfaction': 92
            }
        }
    
    def generate_impact_visualization_data(self) -> Dict[str, Any]:
        """Generate data for impact visualizations and charts"""
        
        # Global platform statistics
        platform_stats = {
            'total_users': 125847,
            'total_companies': 342,
            'carbon_saved_tons': 15623,
            'challenges_completed': 45892,
            'trees_planted': 23456,
            'renewable_energy_kwh': 892341,
            'countries': 23,
            'verified_offsets_tons': 8934
        }
        
        # Carbon reduction by category (global)
        category_reductions = {
            'transport': {
                'total_reduction': 6234,  # tons CO2
                'percentage': 40,
                'top_methods': [
                    {'method': 'Public transit adoption', 'impact': 2145},
                    {'method': 'Remote work increase', 'impact': 1678},
                    {'method': 'Cycling/walking', 'impact': 1234},
                    {'method': 'Electric vehicle adoption', 'impact': 1177}
                ]
            },
            'food': {
                'total_reduction': 3789,
                'percentage': 24,
                'top_methods': [
                    {'method': 'Plant-based meals', 'impact': 1567},
                    {'method': 'Local food sourcing', 'impact': 892},
                    {'method': 'Reduced food waste', 'impact': 756},
                    {'method': 'Sustainable agriculture', 'impact': 574}
                ]
            },
            'energy': {
                'total_reduction': 3845,
                'percentage': 25,
                'top_methods': [
                    {'method': 'Renewable energy switch', 'impact': 1923},
                    {'method': 'Energy efficiency upgrades', 'impact': 967},
                    {'method': 'Smart home technology', 'impact': 542},
                    {'method': 'Behavioral changes', 'impact': 413}
                ]
            },
            'consumption': {
                'total_reduction': 1755,
                'percentage': 11,
                'top_methods': [
                    {'method': 'Waste reduction', 'impact': 678},
                    {'method': 'Sustainable products', 'impact': 445},
                    {'method': 'Circular economy practices', 'impact': 389},
                    {'method': 'Minimalism adoption', 'impact': 243}
                ]
            }
        }
        
        # Geographic distribution
        geographic_data = [
            {'country': 'United States', 'users': 45234, 'carbon_saved': 5678, 'rank': 1},
            {'country': 'Canada', 'users': 12456, 'carbon_saved': 1567, 'rank': 2},
            {'country': 'United Kingdom', 'users': 11789, 'carbon_saved': 1445, 'rank': 3},
            {'country': 'Germany', 'users': 9876, 'carbon_saved': 1234, 'rank': 4},
            {'country': 'Australia', 'users': 8234, 'carbon_saved': 1123, 'rank': 5},
            {'country': 'Netherlands', 'users': 6789, 'carbon_saved': 987, 'rank': 6},
            {'country': 'Sweden', 'users': 5432, 'carbon_saved': 876, 'rank': 7},
            {'country': 'France', 'users': 4567, 'carbon_saved': 743, 'rank': 8}
        ]
        
        # Monthly growth trends
        growth_data = []
        base_date = datetime.now() - timedelta(days=365)
        base_users = 15000
        
        for month in range(12):
            growth_rate = random.uniform(0.08, 0.15)  # 8-15% monthly growth
            base_users = int(base_users * (1 + growth_rate))
            
            growth_data.append({
                'month': (base_date + timedelta(days=month*30)).strftime('%Y-%m'),
                'total_users': base_users,
                'new_users': int(base_users * growth_rate),
                'active_users': int(base_users * 0.78),
                'carbon_saved': int(base_users * random.uniform(0.12, 0.18)),
                'revenue': int(base_users * random.uniform(8, 12))
            })
        
        return {
            'platform_statistics': platform_stats,
            'category_reductions': category_reductions,
            'geographic_distribution': geographic_data,
            'growth_trends': growth_data,
            'impact_projections': {
                '2024_target': 50000,  # tons CO2
                '2025_target': 120000,
                '2030_target': 500000,
                'paris_agreement_contribution': 0.0012  # percentage
            },
            'real_world_equivalents': {
                'cars_off_road': int(platform_stats['carbon_saved_tons'] / 4.6),
                'homes_powered': int(platform_stats['renewable_energy_kwh'] / 10000),
                'flights_offset': int(platform_stats['carbon_saved_tons'] / 0.9),
                'forests_preserved': int(platform_stats['carbon_saved_tons'] / 2.2)
            }
        }
    
    def export_all_demo_data(self, output_dir: str = './demo_data'):
        """Export all generated demo data to files"""
        
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate and save user timelines
        user_timelines = {}
        for user in self.demo_users:
            timeline = self.generate_user_carbon_timeline(user['id'])
            user_timelines[user['id']] = timeline
        
        # Generate challenge data
        challenge_data = self.generate_challenge_participation_data()
        
        # Generate corporate data
        corporate_data = {}
        for company in self.demo_companies:
            corporate_data[company['id']] = self.generate_corporate_engagement_data(company['id'])
        
        # Generate impact visualization data
        impact_data = self.generate_impact_visualization_data()
        
        # Save all data
        datasets = {
            'users': self.demo_users,
            'companies': self.demo_companies,
            'user_timelines': user_timelines,
            'challenges': challenge_data,
            'corporate_engagement': corporate_data,
            'impact_visualizations': impact_data
        }
        
        for filename, data in datasets.items():
            filepath = os.path.join(output_dir, f'{filename}.json')
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            print(f"Exported {filename} data to {filepath}")
        
        # Generate summary statistics
        summary = {
            'generation_date': datetime.now().isoformat(),
            'total_users': len(self.demo_users),
            'total_companies': len(self.demo_companies),
            'total_data_points': sum(len(timeline) for timeline in user_timelines.values()),
            'challenge_participations': len(challenge_data),
            'data_files': list(datasets.keys())
        }
        
        summary_path = os.path.join(output_dir, 'summary.json')
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        print(f"Demo data generation complete! Summary saved to {summary_path}")
        return summary

def main():
    """Generate comprehensive demo data for CarbonSense"""
    
    generator = CarbonSenseDemoDataGenerator()
    
    print("🌍 Generating CarbonSense Demo Data...")
    print("=" * 50)
    
    # Generate and display sample data
    print("\n📊 Sample User Carbon Timeline:")
    timeline_sample = generator.generate_user_carbon_timeline('user_001', days=30)
    for i, day in enumerate(timeline_sample[:5]):
        print(f"Day {i+1}: {day['total']:.1f} kg CO2 (Transport: {day['emissions']['transport']:.1f})")
    
    print("\n🏆 Sample Challenge Data:")
    challenge_sample = generator.generate_challenge_participation_data()[:3]
    for challenge in challenge_sample:
        print(f"Challenge {challenge['challenge_id']}: {challenge['progress']}% complete")
    
    print("\n🏢 Sample Corporate Engagement:")
    corporate_sample = generator.generate_corporate_engagement_data('company_001')
    print(f"Company: {corporate_sample['company_name']}")
    print(f"Participation: {corporate_sample['overall_participation']}%")
    print(f"Carbon Saved: {corporate_sample['total_carbon_saved']:.1f} kg")
    
    print("\n📈 Platform Impact Data:")
    impact_sample = generator.generate_impact_visualization_data()
    stats = impact_sample['platform_statistics']
    print(f"Total Users: {stats['total_users']:,}")
    print(f"Carbon Saved: {stats['carbon_saved_tons']:,} tons")
    print(f"Challenges Completed: {stats['challenges_completed']:,}")
    
    # Export all data
    print("\n💾 Exporting Complete Dataset...")
    summary = generator.export_all_demo_data()
    
    print(f"\n✅ Generated {summary['total_data_points']:,} data points")
    print(f"📁 Files created: {', '.join(summary['data_files'])}")
    print("\n🚀 Demo data ready for showcase!")

if __name__ == "__main__":
    main()