'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import SocialFeed from './SocialFeed'

interface DashboardData {
  totalEmissions: number
  weeklyEmissions: number
  monthlyEmissions: number
  recommendations: string[]
  recentActivities: Array<{
    id: string
    type: string
    emissions: number
    date: string
  }>
  achievements: Array<{
    id: string
    title: string
    description: string
    achieved: boolean
  }>
}

export default function Dashboard() {
  const { user, logout } = useAuth()
  const [data, setData] = useState<DashboardData | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    if (user) {
      fetchDashboardData()
    }
  }, [user])

  const fetchDashboardData = async () => {
    try {
      // Simulated data for now - in production, this would come from the API
      const mockData: DashboardData = {
        totalEmissions: 125.6,
        weeklyEmissions: 18.3,
        monthlyEmissions: 75.2,
        recommendations: [
          'Switch to public transport 2 days per week',
          'Reduce meat consumption by 1 meal per day',
          'Use energy-efficient appliances'
        ],
        recentActivities: [
          { id: '1', type: 'Transportation - Car', emissions: 12.5, date: '2024-01-15' },
          { id: '2', type: 'Energy - Electricity', emissions: 8.3, date: '2024-01-14' },
          { id: '3', type: 'Food - Meat', emissions: 6.7, date: '2024-01-14' }
        ],
        achievements: [
          { id: '1', title: 'First Steps', description: 'Track your first carbon activity', achieved: true },
          { id: '2', title: 'Week Warrior', description: 'Log activities for 7 consecutive days', achieved: false },
          { id: '3', title: 'Carbon Reducer', description: 'Reduce weekly emissions by 10%', achieved: false }
        ]
      }
      setData(mockData)
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error)
    } finally {
      setIsLoading(false)
    }
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-xl text-gray-600">Loading dashboard...</div>
      </div>
    )
  }

  if (!data) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-xl text-red-600">Failed to load dashboard data</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-gray-900">CarbonSense</h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-gray-700">Welcome, {user?.full_name}</span>
              <button
                onClick={logout}
                className="bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Overview Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-2">Total Emissions</h3>
            <p className="text-3xl font-bold text-red-600">{data.totalEmissions} kg CO₂</p>
            <p className="text-sm text-gray-500 mt-1">This month</p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-2">Weekly Average</h3>
            <p className="text-3xl font-bold text-orange-600">{data.weeklyEmissions} kg CO₂</p>
            <p className="text-sm text-gray-500 mt-1">Last 7 days</p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-2">Monthly Target</h3>
            <p className="text-3xl font-bold text-green-600">{data.monthlyEmissions} kg CO₂</p>
            <p className="text-sm text-gray-500 mt-1">Goal: 100 kg CO₂</p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Recent Activities */}
          <div className="bg-white rounded-lg shadow">
            <div className="p-6 border-b">
              <h3 className="text-lg font-medium text-gray-900">Recent Activities</h3>
            </div>
            <div className="p-6">
              <div className="space-y-4">
                {data.recentActivities.map((activity) => (
                  <div key={activity.id} className="flex justify-between items-center">
                    <div>
                      <p className="font-medium text-gray-900">{activity.type}</p>
                      <p className="text-sm text-gray-500">{activity.date}</p>
                    </div>
                    <span className="text-lg font-semibold text-red-600">
                      {activity.emissions} kg CO₂
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Recommendations */}
          <div className="bg-white rounded-lg shadow">
            <div className="p-6 border-b">
              <h3 className="text-lg font-medium text-gray-900">AI Recommendations</h3>
            </div>
            <div className="p-6">
              <div className="space-y-3">
                {data.recommendations.map((recommendation, index) => (
                  <div key={index} className="flex items-start">
                    <div className="flex-shrink-0 w-2 h-2 bg-green-500 rounded-full mt-2 mr-3"></div>
                    <p className="text-gray-700">{recommendation}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Achievements */}
        <div className="mt-8 bg-white rounded-lg shadow">
          <div className="p-6 border-b">
            <h3 className="text-lg font-medium text-gray-900">Achievements</h3>
          </div>
          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {data.achievements.map((achievement) => (
                <div
                  key={achievement.id}
                  className={`p-4 rounded-lg border-2 ${
                    achievement.achieved
                      ? 'border-green-500 bg-green-50'
                      : 'border-gray-300 bg-gray-50'
                  }`}
                >
                  <div className="flex items-center mb-2">
                    <div
                      className={`w-6 h-6 rounded-full mr-2 ${
                        achievement.achieved ? 'bg-green-500' : 'bg-gray-300'
                      }`}
                    >
                      {achievement.achieved && (
                        <svg className="w-4 h-4 text-white ml-1 mt-1" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                        </svg>
                      )}
                    </div>
                    <h4 className="font-medium text-gray-900">{achievement.title}</h4>
                  </div>
                  <p className="text-sm text-gray-600">{achievement.description}</p>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Climate Community Feed */}
        <div className="mt-8">
          <div className="mb-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-2">🌍 Climate Community</h2>
            <p className="text-gray-600">Connect with fellow climate warriors, share achievements, and get inspired</p>
          </div>
          <SocialFeed />
        </div>
      </main>
    </div>
  )
}