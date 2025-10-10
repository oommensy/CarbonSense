'use client'

import React, { createContext, useContext, useState, useEffect } from 'react'

interface User {
  id: number
  email: string
  username: string
  full_name: string
  role: 'individual' | 'corporate' | 'admin'
  is_active: boolean
  is_verified: boolean
  carbon_goal: number
  avatar_url?: string
  created_at: string
}

interface AuthContextType {
  user: User | null
  isLoading: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  register: (userData: RegisterData) => Promise<void>
}

interface RegisterData {
  email: string
  username: string
  password: string
  full_name: string
  role?: 'individual' | 'corporate'
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Check for existing token and validate
    const token = localStorage.getItem('access_token')
    if (token) {
      // In a real app, validate token with backend
      // For demo purposes, we'll create a mock user
      setUser({
        id: 1,
        email: 'demo@carbonsense.com',
        username: 'demo_user',
        full_name: 'Demo User',
        role: 'individual',
        is_active: true,
        is_verified: true,
        carbon_goal: 1000,
        created_at: new Date().toISOString(),
      })
    }
    setIsLoading(false)
  }, [])

  const login = async (email: string, password: string) => {
    try {
      // Mock login - in real app, call API
      const mockUser: User = {
        id: 1,
        email,
        username: email.split('@')[0],
        full_name: 'Demo User',
        role: 'individual',
        is_active: true,
        is_verified: true,
        carbon_goal: 1000,
        created_at: new Date().toISOString(),
      }
      
      localStorage.setItem('access_token', 'mock_token')
      setUser(mockUser)
    } catch (error) {
      throw new Error('Login failed')
    }
  }

  const logout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    setUser(null)
  }

  const register = async (userData: RegisterData) => {
    try {
      // Mock registration - in real app, call API
      const mockUser: User = {
        id: 1,
        email: userData.email,
        username: userData.username,
        full_name: userData.full_name,
        role: userData.role || 'individual',
        is_active: true,
        is_verified: false,
        carbon_goal: 1000,
        created_at: new Date().toISOString(),
      }
      
      localStorage.setItem('access_token', 'mock_token')
      setUser(mockUser)
    } catch (error) {
      throw new Error('Registration failed')
    }
  }

  return (
    <AuthContext.Provider value={{ user, isLoading, login, logout, register }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}