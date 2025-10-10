import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Provider } from 'react-redux';
import { PaperProvider } from 'react-native-paper';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';

import { store } from './src/store/store';
import { theme } from './src/styles/theme';

// Screen imports
import DashboardScreen from './src/screens/DashboardScreen';
import CarbonTrackerScreen from './src/screens/CarbonTrackerScreen';
import ChallengesScreen from './src/screens/ChallengesScreen';
import ImpactScreen from './src/screens/ImpactScreen';
import ProfileScreen from './src/screens/ProfileScreen';

const Tab = createBottomTabNavigator();

export default function App() {
  return (
    <Provider store={store}>
      <PaperProvider theme={theme}>
        <SafeAreaProvider>
          <NavigationContainer>
            <Tab.Navigator
              screenOptions={({ route }) => ({
                tabBarIcon: ({ focused, color, size }) => {
                  let iconName: keyof typeof Ionicons.glyphMap;

                  if (route.name === 'Dashboard') {
                    iconName = focused ? 'home' : 'home-outline';
                  } else if (route.name === 'Tracker') {
                    iconName = focused ? 'leaf' : 'leaf-outline';
                  } else if (route.name === 'Challenges') {
                    iconName = focused ? 'trophy' : 'trophy-outline';
                  } else if (route.name === 'Impact') {
                    iconName = focused ? 'bar-chart' : 'bar-chart-outline';
                  } else if (route.name === 'Profile') {
                    iconName = focused ? 'person' : 'person-outline';
                  } else {
                    iconName = 'help-outline';
                  }

                  return <Ionicons name={iconName} size={size} color={color} />;
                },
                tabBarActiveTintColor: theme.colors.primary,
                tabBarInactiveTintColor: '#666',
                tabBarStyle: {
                  backgroundColor: '#fff',
                  borderTopWidth: 1,
                  borderTopColor: '#e0e0e0',
                  paddingBottom: 8,
                  height: 65,
                },
                headerShown: false,
              })}
            >
              <Tab.Screen 
                name="Dashboard" 
                component={DashboardScreen}
                options={{ title: 'Home' }}
              />
              <Tab.Screen 
                name="Tracker" 
                component={CarbonTrackerScreen}
                options={{ title: 'Track' }}
              />
              <Tab.Screen 
                name="Challenges" 
                component={ChallengesScreen}
                options={{ title: 'Challenges' }}
              />
              <Tab.Screen 
                name="Impact" 
                component={ImpactScreen}
                options={{ title: 'Impact' }}
              />
              <Tab.Screen 
                name="Profile" 
                component={ProfileScreen}
                options={{ title: 'Profile' }}
              />
            </Tab.Navigator>
          </NavigationContainer>
        </SafeAreaProvider>
      </PaperProvider>
    </Provider>
  );
}