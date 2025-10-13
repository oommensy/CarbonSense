// Enhanced Landing Page with Social Media Features
import { useState, useEffect } from 'react'

interface LandingPageProps {
  onAuthClick: () => void
}

export default function SocialLandingPage({ onAuthClick }: LandingPageProps) {
  const [liveStats, setLiveStats] = useState({
    carbonSaved: 2500000,
    activeUsers: 15234,
    todayActions: 1847
  });

  const [recentAchievements, setRecentAchievements] = useState([
    { user: "Sarah", action: "went car-free for a week", time: "2 min ago", co2: 45 },
    { user: "Mike", action: "installed solar panels", time: "5 min ago", co2: 120 },
    { user: "Emma", action: "started composting", time: "8 min ago", co2: 15 },
    { user: "Alex", action: "biked to work", time: "12 min ago", co2: 8 }
  ]);

  const [trendingChallenges, setTrendingChallenges] = useState([
    { name: "Car-Free Week", participants: 2847, icon: "🚲" },
    { name: "Plant-Based Month", participants: 1923, icon: "🌱" },
    { name: "Zero Waste Challenge", participants: 1456, icon: "♻️" }
  ]);

  // Simulate live updates
  useEffect(() => {
    const interval = setInterval(() => {
      setLiveStats(prev => ({
        carbonSaved: prev.carbonSaved + Math.floor(Math.random() * 10),
        activeUsers: prev.activeUsers + Math.floor(Math.random() * 3),
        todayActions: prev.todayActions + Math.floor(Math.random() * 5)
      }));

      // Rotate recent achievements
      setRecentAchievements(prev => {
        const newAchievements = [...prev];
        newAchievements.unshift({
          user: ["John", "Lisa", "David", "Grace"][Math.floor(Math.random() * 4)],
          action: ["saved energy", "chose public transport", "reduced food waste"][Math.floor(Math.random() * 3)],
          time: "just now",
          co2: Math.floor(Math.random() * 30) + 5
        });
        return newAchievements.slice(0, 4);
      });
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50">
      {/* Header with Live Activity Ticker */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Live Activity Ticker */}
          <div className="bg-green-100 px-4 py-2 text-center">
            <div className="flex items-center justify-center space-x-6 text-sm text-green-800">
              <div className="flex items-center">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse mr-2"></div>
                <span>{liveStats.todayActions} climate actions today!</span>
              </div>
              <div className="hidden md:block">•</div>
              <div className="hidden md:flex items-center">
                <span>🌱 {liveStats.carbonSaved.toLocaleString()} kg CO₂ saved by our community</span>
              </div>
            </div>
          </div>

          <div className="flex justify-between items-center py-4">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-gray-900">🌍 CarbonSense</h1>
              <span className="ml-2 bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full">
                {liveStats.activeUsers.toLocaleString()} online
              </span>
            </div>
            <button
              onClick={onAuthClick}
              className="bg-green-600 text-white px-6 py-2 rounded-md hover:bg-green-700 transition-colors shadow-lg"
            >
              Join Community
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Hero Section with Social Proof */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center mb-16">
          <div>
            <h1 className="text-4xl font-bold text-gray-900 sm:text-5xl">
              Join the Climate
              <span className="text-green-600"> Social Movement</span>
            </h1>
            <p className="mt-4 text-xl text-gray-600">
              Connect with 15,000+ climate warriors. Share achievements, compete in challenges, and make saving the planet social and fun! 🎯
            </p>
            
            {/* Social Proof Pills */}
            <div className="mt-6 flex flex-wrap gap-2">
              <div className="bg-yellow-100 text-yellow-800 px-3 py-1 rounded-full text-sm">
                🏆 #1 Climate App
              </div>
              <div className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm">
                ⭐ 4.9/5 Rating
              </div>
              <div className="bg-purple-100 text-purple-800 px-3 py-1 rounded-full text-sm">
                🔥 Trending #ClimateAction
              </div>
            </div>

            <div className="mt-8 flex flex-col sm:flex-row gap-4">
              <button
                onClick={onAuthClick}
                className="flex-1 bg-green-600 text-white px-8 py-3 rounded-lg hover:bg-green-700 transition-colors shadow-lg font-semibold"
              >
                Start Your Climate Journey 🚀
              </button>
              <button className="flex-1 bg-white text-green-600 border-2 border-green-600 px-8 py-3 rounded-lg hover:bg-green-50 transition-colors font-semibold">
                Watch How It Works 📺
              </button>
            </div>
          </div>

          {/* Live Community Feed */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-bold text-gray-900">🌟 Live Community</h3>
              <span className="text-green-600 text-sm font-medium">Real-time updates</span>
            </div>
            
            <div className="space-y-3">
              {recentAchievements.map((achievement, index) => (
                <div key={index} className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                  <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                    <span className="text-green-600 font-semibold text-sm">
                      {achievement.user[0]}
                    </span>
                  </div>
                  <div className="flex-1">
                    <p className="text-sm text-gray-800">
                      <span className="font-semibold">{achievement.user}</span> {achievement.action}
                    </p>
                    <p className="text-xs text-gray-500">{achievement.time} • Saved {achievement.co2}kg CO₂</p>
                  </div>
                  <div className="text-green-600">
                    <span className="text-xs">🌱</span>
                  </div>
                </div>
              ))}
            </div>

            <button
              onClick={onAuthClick}
              className="w-full mt-4 bg-gray-100 text-gray-700 py-2 rounded-lg hover:bg-gray-200 transition-colors text-sm font-medium"
            >
              Join the conversation 💬
            </button>
          </div>
        </div>

        {/* Trending Challenges Section */}
        <div className="mb-16">
          <div className="text-center mb-8">
            <h2 className="text-3xl font-bold text-gray-900">🔥 Trending Climate Challenges</h2>
            <p className="mt-2 text-gray-600">Join thousands taking action right now!</p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {trendingChallenges.map((challenge, index) => (
              <div key={index} className="bg-white rounded-xl shadow-lg p-6 border-l-4 border-green-500">
                <div className="flex items-center justify-between mb-3">
                  <span className="text-2xl">{challenge.icon}</span>
                  <span className="bg-red-100 text-red-800 text-xs px-2 py-1 rounded-full font-semibold">
                    🔥 HOT
                  </span>
                </div>
                <h3 className="font-bold text-gray-900 mb-2">{challenge.name}</h3>
                <p className="text-green-600 font-semibold text-sm mb-3">
                  {challenge.participants.toLocaleString()} people joined today
                </p>
                <button
                  onClick={onAuthClick}
                  className="w-full bg-green-600 text-white py-2 rounded-lg hover:bg-green-700 transition-colors font-medium text-sm"
                >
                  Join Challenge 🎯
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Social Features Preview */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 mb-16">
          <div>
            <h2 className="text-3xl font-bold text-gray-900 mb-6">📱 Like Instagram, but for Climate</h2>
            <div className="space-y-4">
              <div className="flex items-start space-x-3">
                <div className="w-6 h-6 bg-green-100 rounded-full flex items-center justify-center mt-1">
                  <span className="text-green-600 text-sm">📸</span>
                </div>
                <div>
                  <h4 className="font-semibold text-gray-900">Share Your Climate Wins</h4>
                  <p className="text-gray-600 text-sm">Post photos of your bike rides, plant-based meals, and solar panels</p>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center mt-1">
                  <span className="text-blue-600 text-sm">👥</span>
                </div>
                <div>
                  <h4 className="font-semibold text-gray-900">Follow Climate Warriors</h4>
                  <p className="text-gray-600 text-sm">Connect with friends and discover inspiring climate leaders</p>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <div className="w-6 h-6 bg-purple-100 rounded-full flex items-center justify-center mt-1">
                  <span className="text-purple-600 text-sm">🎮</span>
                </div>
                <div>
                  <h4 className="font-semibold text-gray-900">Compete & Get Rewards</h4>
                  <p className="text-gray-600 text-sm">Climb leaderboards, earn badges, unlock achievements</p>
                </div>
              </div>
            </div>
          </div>

          {/* Mock Phone Interface */}
          <div className="flex justify-center">
            <div className="w-64 bg-white rounded-3xl shadow-2xl p-4">
              <div className="bg-gray-100 rounded-2xl p-4 space-y-3">
                <div className="flex items-center space-x-2">
                  <div className="w-8 h-8 bg-green-200 rounded-full"></div>
                  <div>
                    <div className="w-20 h-2 bg-gray-300 rounded"></div>
                    <div className="w-16 h-1 bg-gray-200 rounded mt-1"></div>
                  </div>
                </div>
                <div className="w-full h-32 bg-gradient-to-r from-green-200 to-blue-200 rounded-lg"></div>
                <div className="flex justify-between">
                  <div className="flex space-x-2">
                    <span>❤️</span>
                    <span>💬</span>
                    <span>🔄</span>
                  </div>
                  <span>🌱</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* FOMO Section */}
        <div className="bg-gradient-to-r from-green-600 to-blue-600 rounded-xl shadow-lg p-8 text-white text-center mb-16">
          <h2 className="text-3xl font-bold mb-4">⏰ Don't Miss Out!</h2>
          <p className="text-xl mb-6">
            This month: Join the <span className="font-bold">Car-Free Challenge</span> with 5,000+ participants
          </p>
          <div className="flex justify-center space-x-8 mb-6">
            <div>
              <div className="text-2xl font-bold">12</div>
              <div className="text-sm opacity-90">Days Left</div>
            </div>
            <div>
              <div className="text-2xl font-bold">2,847</div>
              <div className="text-sm opacity-90">Joined Today</div>
            </div>
            <div>
              <div className="text-2xl font-bold">456k</div>
              <div className="text-sm opacity-90">kg CO₂ Saved</div>
            </div>
          </div>
          <button
            onClick={onAuthClick}
            className="bg-white text-green-600 px-8 py-3 rounded-lg hover:bg-gray-100 transition-colors font-bold text-lg shadow-lg"
          >
            Join Before It's Too Late! 🚀
          </button>
        </div>

        {/* Social Proof Testimonials */}
        <div className="mb-16">
          <h2 className="text-3xl font-bold text-gray-900 text-center mb-8">💬 What Climate Warriors Say</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white rounded-xl shadow-lg p-6">
              <div className="flex items-center mb-4">
                <div className="w-12 h-12 bg-gradient-to-r from-green-400 to-blue-400 rounded-full flex items-center justify-center text-white font-bold">
                  S
                </div>
                <div className="ml-3">
                  <h4 className="font-semibold text-gray-900">Sarah K.</h4>
                  <div className="flex text-yellow-400 text-sm">⭐⭐⭐⭐⭐</div>
                </div>
              </div>
              <p className="text-gray-700 italic">
                "The community challenges motivated me to reduce my carbon footprint by 40%! Love competing with friends 🏆"
              </p>
            </div>

            <div className="bg-white rounded-xl shadow-lg p-6">
              <div className="flex items-center mb-4">
                <div className="w-12 h-12 bg-gradient-to-r from-purple-400 to-pink-400 rounded-full flex items-center justify-center text-white font-bold">
                  M
                </div>
                <div className="ml-3">
                  <h4 className="font-semibold text-gray-900">Mike R.</h4>
                  <div className="flex text-yellow-400 text-sm">⭐⭐⭐⭐⭐</div>
                </div>
              </div>
              <p className="text-gray-700 italic">
                "Finally, an app that makes climate action social and fun! My whole family is now competing 😄"
              </p>
            </div>

            <div className="bg-white rounded-xl shadow-lg p-6">
              <div className="flex items-center mb-4">
                <div className="w-12 h-12 bg-gradient-to-r from-orange-400 to-red-400 rounded-full flex items-center justify-center text-white font-bold">
                  E
                </div>
                <div className="ml-3">
                  <h4 className="font-semibold text-gray-900">Emma L.</h4>
                  <div className="flex text-yellow-400 text-sm">⭐⭐⭐⭐⭐</div>
                </div>
              </div>
              <p className="text-gray-700 italic">
                "Sharing my solar panel installation got 200 likes! Inspiring others feels amazing 🌞"
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}