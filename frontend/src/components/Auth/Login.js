import React, { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { toast } from 'react-toastify'
import { useAuth } from '../../context/AuthContext'
import { Lock, Mail, TrendingUp } from 'lucide-react'

const Login = () => {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const { login } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    const result = await login(email, password)

    if (result.success) {
      toast.success(`Welcome back, ${result.user.firstName}!`)
      navigate('/dashboard')
    } else {
      setError(result.error)
      toast.error(result.error)
    }

    setLoading(false)
  }

  return (
    <div className="min-h-screen bg-primary flex items-center justify-center p-6">
      <div className="max-w-md w-full">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex justify-center mb-4">
            <TrendingUp size={48} className="text-accent" />
          </div>
          <h1 className="text-3xl font-bold text-white mb-2">
            Crypto Trading Platform
          </h1>
          <p className="text-gray-400">Sign in to your account</p>
        </div>

        {/* Login Form */}
        <div className="bg-secondary rounded-lg p-8 border border-gray-600">
          <form onSubmit={handleSubmit}>
            {error && (
              <div className="bg-red-900/50 border border-red-600 text-red-300 px-4 py-3 rounded mb-4">
                {error}
              </div>
            )}

            {/* Email */}
            <div className="mb-4">
              <label className="block text-gray-300 mb-2">Email</label>
              <div className="relative">
                <Mail
                  className="absolute left-3 top-3 text-gray-400"
                  size={20}
                />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full bg-primary border border-gray-600 rounded-lg pl-10 pr-4 py-3 text-white focus:outline-none focus:border-accent"
                  placeholder="your@email.com"
                  required
                />
              </div>
            </div>

            {/* Password */}
            <div className="mb-6">
              <label className="block text-gray-300 mb-2">Password</label>
              <div className="relative">
                <Lock
                  className="absolute left-3 top-3 text-gray-400"
                  size={20}
                />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full bg-primary border border-gray-600 rounded-lg pl-10 pr-4 py-3 text-white focus:outline-none focus:border-accent"
                  placeholder="••••••••"
                  required
                />
              </div>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-accent hover:bg-green-600 text-white font-semibold py-3 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Signing in...' : 'Sign In'}
            </button>
          </form>

          {/* Register Link */}
          <div className="mt-6 text-center">
            <p className="text-gray-400">
              Don't have an account?{' '}
              <Link to="/register" className="text-accent hover:underline">
                Create one
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Login
