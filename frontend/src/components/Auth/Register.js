import React, { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { toast } from 'react-toastify'
import { Lock, Mail, User, TrendingUp } from 'lucide-react'
import { registerUser } from '../../services/api'

const Register = () => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    firstName: '',
    lastName: ''
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const navigate = useNavigate()

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')

    // Validation
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match')
      return
    }

    if (formData.password.length < 8) {
      setError('Password must be at least 8 characters')
      return
    }

    setLoading(true)

    try {
      // Remove confirmPassword before sending to API
      const { confirmPassword, ...userData } = formData

      const response = await registerUser(userData)

      if (response.data) {
        // Show success toast
        toast.success('Registration successful! Please login to continue.', {
          position: 'top-right',
          autoClose: 3000
        })

        // Redirect to login after 1 second
        setTimeout(() => {
          navigate('/login')
        }, 1000)
      }
    } catch (err) {
      const errorMessage =
        err.response?.data?.message || 'Registration failed. Please try again.'
      setError(errorMessage)
      toast.error(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-primary flex items-center justify-center p-6">
      <div className="max-w-md w-full">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex justify-center mb-4">
            <TrendingUp size={48} className="text-accent" />
          </div>
          <h1 className="text-3xl font-bold text-white mb-2">Create Account</h1>
          <p className="text-gray-400">Join the crypto trading platform</p>
        </div>

        {/* Register Form */}
        <div className="bg-secondary rounded-lg p-8 border border-gray-600">
          <form onSubmit={handleSubmit}>
            {error && (
              <div className="bg-red-900/50 border border-red-600 text-red-300 px-4 py-3 rounded mb-4">
                {error}
              </div>
            )}

            {/* First Name & Last Name */}
            <div className="grid grid-cols-2 gap-4 mb-4">
              <div>
                <label className="block text-gray-300 mb-2">First Name</label>
                <div className="relative">
                  <User
                    className="absolute left-3 top-3 text-gray-400"
                    size={20}
                  />
                  <input
                    type="text"
                    name="firstName"
                    value={formData.firstName}
                    onChange={handleChange}
                    className="w-full bg-primary border border-gray-600 rounded-lg pl-10 pr-4 py-3 text-white focus:outline-none focus:border-accent"
                    placeholder="John"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="block text-gray-300 mb-2">Last Name</label>
                <input
                  type="text"
                  name="lastName"
                  value={formData.lastName}
                  onChange={handleChange}
                  className="w-full bg-primary border border-gray-600 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-accent"
                  placeholder="Doe"
                  required
                />
              </div>
            </div>

            {/* Username */}
            <div className="mb-4">
              <label className="block text-gray-300 mb-2">Username</label>
              <div className="relative">
                <User
                  className="absolute left-3 top-3 text-gray-400"
                  size={20}
                />
                <input
                  type="text"
                  name="username"
                  value={formData.username}
                  onChange={handleChange}
                  className="w-full bg-primary border border-gray-600 rounded-lg pl-10 pr-4 py-3 text-white focus:outline-none focus:border-accent"
                  placeholder="johndoe"
                  required
                />
              </div>
            </div>

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
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  className="w-full bg-primary border border-gray-600 rounded-lg pl-10 pr-4 py-3 text-white focus:outline-none focus:border-accent"
                  placeholder="your@email.com"
                  required
                />
              </div>
            </div>

            {/* Password */}
            <div className="mb-4">
              <label className="block text-gray-300 mb-2">Password</label>
              <div className="relative">
                <Lock
                  className="absolute left-3 top-3 text-gray-400"
                  size={20}
                />
                <input
                  type="password"
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  className="w-full bg-primary border border-gray-600 rounded-lg pl-10 pr-4 py-3 text-white focus:outline-none focus:border-accent"
                  placeholder="••••••••"
                  required
                />
              </div>
            </div>

            {/* Confirm Password */}
            <div className="mb-6">
              <label className="block text-gray-300 mb-2">
                Confirm Password
              </label>
              <div className="relative">
                <Lock
                  className="absolute left-3 top-3 text-gray-400"
                  size={20}
                />
                <input
                  type="password"
                  name="confirmPassword"
                  value={formData.confirmPassword}
                  onChange={handleChange}
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
              {loading ? 'Creating account...' : 'Create Account'}
            </button>
          </form>

          {/* Login Link */}
          <div className="mt-6 text-center">
            <p className="text-gray-400">
              Already have an account?{' '}
              <Link to="/login" className="text-accent hover:underline">
                Sign in
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Register
