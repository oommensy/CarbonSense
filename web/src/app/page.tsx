'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import Dashboard from '@/components/Dashboard'
import LandingPage from '@/components/LandingPage'
import AuthModal from '@/components/AuthModal'

export default function Home() {
  const { user, isLoading } = useAuth()
  const [showAuthModal, setShowAuthModal] = useState(false)

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-green-500"></div>
      </div>
    )
  }

  if (user) {
    return <Dashboard />
  }

  return (
    <>
      <LandingPage onOpenAuth={() => setShowAuthModal(true)} />
      {showAuthModal && (
        <AuthModal onClose={() => setShowAuthModal(false)} />
      )}
    </>
  )
}