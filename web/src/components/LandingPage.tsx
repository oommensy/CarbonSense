import { useState } from 'react'

interface LandingPageProps {
  onAuthClick: () => void
}

export default function LandingPage({ onAuthClick }: LandingPageProps) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-gray-900">CarbonSense</h1>
            </div>
            <button
              onClick={onAuthClick}
              className="bg-green-600 text-white px-6 py-2 rounded-md hover:bg-green-700 transition-colors"
            >
              Get Started
            </button>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-gray-900 sm:text-5xl md:text-6xl">
            Track Your{' '}
            <span className="text-green-600">Carbon Footprint</span>
          </h1>
          <p className="mt-3 max-w-md mx-auto text-base text-gray-500 sm:text-lg md:mt-5 md:text-xl md:max-w-3xl">
            AI-powered carbon tracking that helps you understand and reduce your environmental impact. 
            Make every action count towards a sustainable future.
          </p>
          <div className="mt-5 max-w-md mx-auto sm:flex sm:justify-center md:mt-8">
            <button
              onClick={onAuthClick}
              className="w-full flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-white bg-green-600 hover:bg-green-700 md:py-4 md:text-lg md:px-10 transition-colors"
            >
              Start Tracking Today
            </button>
          </div>
        </div>

        {/* Features Section */}
        <div className="mt-20">
          <div className="grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3">
            {/* Feature 1 */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">Smart Tracking</h3>
              <p className="text-gray-600">Automatically track your daily activities and calculate their carbon impact with AI-powered analysis.</p>
            </div>

            {/* Feature 2 */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">AI Recommendations</h3>
              <p className="text-gray-600">Get personalized suggestions to reduce your carbon footprint based on your lifestyle patterns.</p>
            </div>

            {/* Feature 3 */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
                </svg>
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">Achievement System</h3>
              <p className="text-gray-600">Stay motivated with gamified achievements and track your progress towards sustainability goals.</p>
            </div>
          </div>
        </div>

        {/* Stats Section */}
        <div className="mt-20 bg-white rounded-lg shadow-lg p-8">
          <div className="text-center mb-8">
            <h2 className="text-3xl font-bold text-gray-900">Making a Real Impact</h2>
            <p className="mt-2 text-gray-600">Join thousands of users reducing their carbon footprint</p>
          </div>
          <div className="grid grid-cols-1 gap-8 sm:grid-cols-3">
            <div className="text-center">
              <div className="text-3xl font-bold text-green-600">2.5M</div>
              <div className="text-gray-600">kg CO₂ Reduced</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600">15K+</div>
              <div className="text-gray-600">Active Users</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-purple-600">98%</div>
              <div className="text-gray-600">User Satisfaction</div>
            </div>
          </div>
        </div>

        {/* CTA Section */}
        <div className="mt-20 text-center">
          <h2 className="text-3xl font-bold text-gray-900">Ready to Make a Difference?</h2>
          <p className="mt-4 text-xl text-gray-600 max-w-2xl mx-auto">
            Start your journey towards carbon neutrality today. Every small action adds up to create a big impact.
          </p>
          <button
            onClick={onAuthClick}
            className="mt-8 inline-flex items-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-white bg-green-600 hover:bg-green-700 transition-colors"
          >
            Join CarbonSense Now
          </button>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-gray-900 text-white mt-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="text-center">
            <h3 className="text-2xl font-bold mb-4">CarbonSense</h3>
            <p className="text-gray-400 mb-8">Building a sustainable future, one carbon footprint at a time.</p>
            <div className="flex justify-center space-x-6">
              <a href="#" className="text-gray-400 hover:text-white transition-colors">Privacy Policy</a>
              <a href="#" className="text-gray-400 hover:text-white transition-colors">Terms of Service</a>
              <a href="#" className="text-gray-400 hover:text-white transition-colors">Contact Us</a>
            </div>
            <div className="mt-8 pt-8 border-t border-gray-800 text-gray-400">
              <p>&copy; 2024 CarbonSense. All rights reserved.</p>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}