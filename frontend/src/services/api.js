import axios from 'axios'

const API_BASE_URL = 'http://localhost:8083/api/v1'

export const marketDataApi = axios.create({
  baseURL: API_BASE_URL
})

// Market data endpoints
export const getPrices = () => marketDataApi.get('/prices')
export const getPrice = (base, quote) =>
  marketDataApi.get(`/price/${base}/${quote}`)
export const getSymbols = () => marketDataApi.get('/symbols')
export const getHealth = () => marketDataApi.get('/health')
