import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Dimensions,
  Alert,
} from 'react-native';

interface CarbonData {
  daily: number;
  weekly: number;
  monthly: number;
  yearly: number;
  goal: number;
}

interface Achievement {
  id: string;
  title: string;
  description: string;
  completed: boolean;
  points: number;
}

const DashboardScreen = () => {
  const [carbonData, setCarbonData] = useState<CarbonData>({
    daily: 0,
    weekly: 0,
    monthly: 0,
    yearly: 0,
    goal: 1000, // kg CO2 yearly goal
  });

  const [achievements, setAchievements] = useState<Achievement[]>([
    {
      id: '1',
      title: 'First Week',
      description: 'Complete your first week of tracking',
      completed: false,
      points: 50,
    },
    {
      id: '2',
      title: 'Low Carbon Day',
      description: 'Achieve less than 5kg CO2 in a day',
      completed: true,
      points: 100,
    },
    {
      id: '3',
      title: 'Public Transport Hero',
      description: 'Use public transport 5 times this week',
      completed: false,
      points: 75,
    },
  ]);

  useEffect(() => {
    // Simulate loading carbon data
    loadCarbonData();
  }, []);

  const loadCarbonData = async () => {
    try {
      // Simulate API call with realistic data
      const today = new Date();
      const dayOfYear = Math.floor((today.getTime() - new Date(today.getFullYear(), 0, 0).getTime()) / (1000 * 60 * 60 * 24));
      
      // Calculate realistic carbon footprint based on average data
      const baseDaily = 12.5; // kg CO2 per day average
      const variation = Math.sin(dayOfYear * 0.017) * 3; // Seasonal variation
      const daily = Math.max(0, baseDaily + variation + (Math.random() - 0.5) * 4);
      
      setCarbonData({
        daily: Math.round(daily * 10) / 10,
        weekly: Math.round(daily * 7 * 10) / 10,
        monthly: Math.round(daily * 30 * 10) / 10,
        yearly: Math.round(daily * 365 * 10) / 10,
        goal: 1000,
      });
    } catch (error) {
      Alert.alert('Error', 'Failed to load carbon data');
    }
  };

  const getProgressPercentage = () => {
    return Math.min((carbonData.yearly / carbonData.goal) * 100, 100);
  };

  const getProgressColor = () => {
    const percentage = getProgressPercentage();
    if (percentage < 50) return '#4CAF50'; // Green
    if (percentage < 80) return '#FF9800'; // Orange
    return '#F44336'; // Red
  };

  const addCarbonEntry = () => {
    Alert.alert(
      'Add Carbon Entry',
      'This would open the carbon tracking form',
      [
        { text: 'Cancel', style: 'cancel' },
        { text: 'Add Entry', onPress: () => console.log('Navigate to tracking') },
      ]
    );
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Carbon Dashboard</Text>
        <Text style={styles.subtitle}>Track your environmental impact</Text>
      </View>

      {/* Carbon Footprint Overview */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Your Carbon Footprint</Text>
        
        <View style={styles.carbonRow}>
          <View style={styles.carbonItem}>
            <Text style={styles.carbonValue}>{carbonData.daily}kg</Text>
            <Text style={styles.carbonLabel}>Today</Text>
          </View>
          <View style={styles.carbonItem}>
            <Text style={styles.carbonValue}>{carbonData.weekly}kg</Text>
            <Text style={styles.carbonLabel}>This Week</Text>
          </View>
        </View>

        <View style={styles.carbonRow}>
          <View style={styles.carbonItem}>
            <Text style={styles.carbonValue}>{carbonData.monthly}kg</Text>
            <Text style={styles.carbonLabel}>This Month</Text>
          </View>
          <View style={styles.carbonItem}>
            <Text style={styles.carbonValue}>{carbonData.yearly}kg</Text>
            <Text style={styles.carbonLabel}>This Year</Text>
          </View>
        </View>

        {/* Progress Bar */}
        <View style={styles.progressContainer}>
          <Text style={styles.progressLabel}>
            Annual Goal Progress: {Math.round(getProgressPercentage())}%
          </Text>
          <View style={styles.progressBar}>
            <View
              style={[
                styles.progressFill,
                {
                  width: `${getProgressPercentage()}%`,
                  backgroundColor: getProgressColor(),
                },
              ]}
            />
          </View>
          <Text style={styles.goalText}>Goal: {carbonData.goal}kg CO2/year</Text>
        </View>
      </View>

      {/* Quick Actions */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Quick Actions</Text>
        <TouchableOpacity style={styles.actionButton} onPress={addCarbonEntry}>
          <Text style={styles.actionButtonText}>+ Add Carbon Entry</Text>
        </TouchableOpacity>
        <TouchableOpacity style={[styles.actionButton, styles.secondaryButton]}>
          <Text style={[styles.actionButtonText, styles.secondaryButtonText]}>
            View Detailed Report
          </Text>
        </TouchableOpacity>
      </View>

      {/* Recent Achievements */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Recent Achievements</Text>
        {achievements.map((achievement) => (
          <View key={achievement.id} style={styles.achievementItem}>
            <View style={styles.achievementInfo}>
              <Text style={[
                styles.achievementTitle,
                achievement.completed && styles.completedAchievement
              ]}>
                {achievement.completed ? '✅' : '🎯'} {achievement.title}
              </Text>
              <Text style={styles.achievementDescription}>
                {achievement.description}
              </Text>
            </View>
            <Text style={styles.achievementPoints}>
              +{achievement.points}pts
            </Text>
          </View>
        ))}
      </View>

      {/* Environmental Impact */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Environmental Impact</Text>
        <View style={styles.impactRow}>
          <View style={styles.impactItem}>
            <Text style={styles.impactValue}>2.3</Text>
            <Text style={styles.impactLabel}>Trees Planted Equivalent</Text>
          </View>
          <View style={styles.impactItem}>
            <Text style={styles.impactValue}>156km</Text>
            <Text style={styles.impactLabel}>Car Miles Saved</Text>
          </View>
        </View>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    padding: 20,
    backgroundColor: '#2E7D32',
    paddingTop: 50,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: 'white',
    marginBottom: 5,
  },
  subtitle: {
    fontSize: 16,
    color: 'rgba(255, 255, 255, 0.9)',
  },
  card: {
    backgroundColor: 'white',
    margin: 15,
    padding: 20,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 15,
  },
  carbonRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 15,
  },
  carbonItem: {
    flex: 1,
    alignItems: 'center',
    padding: 10,
    backgroundColor: '#f8f9fa',
    borderRadius: 8,
    marginHorizontal: 5,
  },
  carbonValue: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#2E7D32',
    marginBottom: 5,
  },
  carbonLabel: {
    fontSize: 12,
    color: '#666',
    textAlign: 'center',
  },
  progressContainer: {
    marginTop: 20,
  },
  progressLabel: {
    fontSize: 14,
    color: '#333',
    marginBottom: 8,
    fontWeight: '500',
  },
  progressBar: {
    height: 8,
    backgroundColor: '#e0e0e0',
    borderRadius: 4,
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    borderRadius: 4,
  },
  goalText: {
    fontSize: 12,
    color: '#666',
    marginTop: 5,
    textAlign: 'center',
  },
  actionButton: {
    backgroundColor: '#2E7D32',
    padding: 15,
    borderRadius: 8,
    marginBottom: 10,
    alignItems: 'center',
  },
  actionButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '500',
  },
  secondaryButton: {
    backgroundColor: 'transparent',
    borderWidth: 1,
    borderColor: '#2E7D32',
  },
  secondaryButtonText: {
    color: '#2E7D32',
  },
  achievementItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  achievementInfo: {
    flex: 1,
  },
  achievementTitle: {
    fontSize: 15,
    fontWeight: '500',
    color: '#333',
    marginBottom: 3,
  },
  completedAchievement: {
    color: '#4CAF50',
  },
  achievementDescription: {
    fontSize: 13,
    color: '#666',
  },
  achievementPoints: {
    fontSize: 14,
    color: '#2E7D32',
    fontWeight: 'bold',
  },
  impactRow: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  impactItem: {
    alignItems: 'center',
    flex: 1,
  },
  impactValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#4CAF50',
    marginBottom: 5,
  },
  impactLabel: {
    fontSize: 12,
    color: '#666',
    textAlign: 'center',
  },
});

export default DashboardScreen;