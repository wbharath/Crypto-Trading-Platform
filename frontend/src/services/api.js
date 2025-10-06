import axios from 'axios'

const API_BASE_URL = 'http://localhost:8083/api/v1'
const USER_API_URL = 'http://localhost:8081/api/users'

export const marketDataApi = axios.create({
  baseURL: API_BASE_URL
})

export const userApi = axios.create({
  baseURL: USER_API_URL
})

// Add token to requests if it exists
userApi.interceptors.request.use((config) => {
  const token = localStorage.getItem('accessToken')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Market data endpoints
export const getPrices = () => marketDataApi.get('/prices')
export const getPrice = (base, quote) =>
  marketDataApi.get(`/price/${base}/${quote}`)
export const getSymbols = () => marketDataApi.get('/symbols')
export const getHealth = () => marketDataApi.get('/health')

// Auth endpoints
export const registerUser = (userData) => userApi.post('/register', userData)
export const loginUser = (credentials) => userApi.post('/login', credentials)
