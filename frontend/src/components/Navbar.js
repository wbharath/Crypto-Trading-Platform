import React, { useState, useRef, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'
import { TrendingUp, User, LogOut, ChevronDown } from 'lucide-react'

const Navbar = () => {
  const { user, logout } = useAuth()
  const [dropdownOpen, setDropdownOpen] = useState(false)
  const dropdownRef = useRef(null)

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setDropdownOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const handleLogout = () => {
    logout()
    window.location.href = '/login'
  }

  return (
    <nav className="bg-secondary border-b border-gray-600 px-6 py-4">
      <div className="flex justify-between items-center">
        {/* Logo/Brand */}
        <div className="flex items-center gap-3">
          <TrendingUp size={32} className="text-accent" />
          <h1 className="text-2xl font-bold text-white">
            Crypto Trading Platform
          </h1>
        </div>

        {/* User Menu */}
        <div className="relative" ref={dropdownRef}>
          <button
            onClick={() => setDropdownOpen(!dropdownOpen)}
            className="flex items-center gap-3 bg-primary hover:bg-gray-700 px-4 py-2 rounded-lg transition-colors border border-gray-600"
          >
            <div className="flex items-center gap-2">
              <div className="bg-accent rounded-full p-2">
                <User size={18} className="text-white" />
              </div>
              <div className="text-left">
                <p className="text-white text-sm font-medium">
                  {user?.firstName} {user?.lastName}
                </p>
                <p className="text-gray-400 text-xs">{user?.email}</p>
              </div>
            </div>
            <ChevronDown
              size={20}
              className={`text-gray-400 transition-transform ${
                dropdownOpen ? 'rotate-180' : ''
              }`}
            />
          </button>

          {/* Dropdown Menu */}
          {dropdownOpen && (
            <div className="absolute right-0 mt-2 w-56 bg-secondary border border-gray-600 rounded-lg shadow-lg z-50">
              {/* User Info */}
              <div className="px-4 py-3 border-b border-gray-600">
                <p className="text-sm text-gray-400">Signed in as</p>
                <p className="text-white font-medium truncate">{user?.email}</p>
                <p className="text-xs text-gray-500 mt-1">Role: {user?.role}</p>
              </div>

              {/* Logout Button */}
              <button
                onClick={handleLogout}
                className="w-full flex items-center gap-3 px-4 py-3 text-left text-red-400 hover:bg-red-900/20 transition-colors"
              >
                <LogOut size={18} />
                <span>Logout</span>
              </button>
            </div>
          )}
        </div>
      </div>
    </nav>
  )
}

export default Navbar
