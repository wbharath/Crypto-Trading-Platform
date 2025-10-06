import React, { useState, useEffect } from 'react'
import { BarChart3, TrendingUp, TrendingDown, DollarSign } from 'lucide-react'
import { getPrices } from '../services/api'

const MarketOverview = () => {
  const [marketData, setMarketData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchMarketData = async () => {
      try {
        const response = await getPrices()
        const prices = response.data

        // Calculate market stats
        const totalVolume = Object.values(prices).reduce((sum, coin) => {
          return sum + (coin.data?.volume_24h || 0)
        }, 0)

        const gainers = Object.values(prices).filter(
          (coin) => coin.data?.change_24h_percent > 0
        ).length

        const losers = Object.values(prices).filter(
          (coin) => coin.data?.change_24h_percent < 0
        ).length

        const totalCoins = Object.keys(prices).length

        setMarketData({
          totalCoins,
          totalVolume,
          gainers,
          losers,
          topGainer: Object.values(prices).reduce(
            (max, coin) =>
              (coin.data?.change_24h_percent || -Infinity) >
              (max?.data?.change_24h_percent || -Infinity)
                ? coin
                : max,
            {}
          )
        })
      } catch (error) {
        console.error('Failed to fetch market overview:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchMarketData()
    const interval = setInterval(fetchMarketData, 60000) // Update every minute
    return () => clearInterval(interval)
  }, [])

  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="bg-secondary rounded-lg p-6 animate-pulse">
            <div className="h-4 bg-gray-600 rounded mb-2"></div>
            <div className="h-8 bg-gray-600 rounded"></div>
          </div>
        ))}
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
      <div className="bg-secondary rounded-lg p-6 border border-gray-600">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-gray-400 text-sm">Total Markets</p>
            <p className="text-2xl font-bold text-white">
              {marketData?.totalCoins || 0}
            </p>
          </div>
          <BarChart3 className="text-accent" size={24} />
        </div>
      </div>

      <div className="bg-secondary rounded-lg p-6 border border-gray-600">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-gray-400 text-sm">24h Volume</p>
            <p className="text-2xl font-bold text-white">
              ${(marketData?.totalVolume / 1000000).toFixed(1)}M
            </p>
          </div>
          <DollarSign className="text-accent" size={24} />
        </div>
      </div>

      <div className="bg-secondary rounded-lg p-6 border border-gray-600">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-gray-400 text-sm">Gainers</p>
            <p className="text-2xl font-bold text-green-400">
              {marketData?.gainers || 0}
            </p>
          </div>
          <TrendingUp className="text-green-400" size={24} />
        </div>
      </div>

      <div className="bg-secondary rounded-lg p-6 border border-gray-600">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-gray-400 text-sm">Losers</p>
            <p className="text-2xl font-bold text-red-400">
              {marketData?.losers || 0}
            </p>
          </div>
          <TrendingDown className="text-red-400" size={24} />
        </div>
      </div>
    </div>
  )
}

export default MarketOverview
