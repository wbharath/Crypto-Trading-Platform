import React, { useState, useEffect } from 'react'
import { TrendingUp, TrendingDown, Minus } from 'lucide-react'
import { getPrice } from '../services/api'
import MiniChart from './MiniChart'

const PriceCard = ({ base, quote }) => {
  const [priceData, setPriceData] = useState(null)
  const [previousPrice, setPreviousPrice] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [priceChange, setPriceChange] = useState(null)

  useEffect(() => {
    const fetchPrice = async () => {
      try {
        const response = await getPrice(base, quote)
        const currentPrice = response.data.data.price

        // Calculate price change if we have a previous price
        if (previousPrice !== null) {
          const change = ((currentPrice - previousPrice) / previousPrice) * 100
          setPriceChange(change)
        }

        setPreviousPrice(currentPrice)
        setPriceData(response.data)
        setError(null)
      } catch (err) {
        setError(`Failed to fetch ${base}/${quote} price`)
      } finally {
        setLoading(false)
      }
    }

    fetchPrice()
    // Normal refresh interval - every 30 seconds
    const interval = setInterval(fetchPrice, 30000)
    return () => clearInterval(interval)
  }, [base, quote])

  if (loading && !priceData) {
    return (
      <div className="bg-secondary rounded-lg p-6 animate-pulse">
        <div className="h-6 bg-gray-600 rounded mb-2"></div>
        <div className="h-8 bg-gray-600 rounded mb-2"></div>
        <div className="h-16 bg-gray-600 rounded mb-2"></div>
        <div className="h-4 bg-gray-600 rounded"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-900 rounded-lg p-6 border border-red-600">
        <p className="text-red-300">{error}</p>
      </div>
    )
  }

  const formatPrice = (price) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 8
    }).format(price)
  }

  const getPriceChangeColor = () => {
    if (priceChange === null || Math.abs(priceChange) < 0.001)
      return 'text-gray-400'
    return priceChange > 0 ? 'text-green-400' : 'text-red-400'
  }

  const getPriceChangeIcon = () => {
    if (priceChange === null || Math.abs(priceChange) < 0.001)
      return <Minus size={16} />
    return priceChange > 0 ? (
      <TrendingUp size={16} />
    ) : (
      <TrendingDown size={16} />
    )
  }

  return (
    <div className="bg-secondary rounded-lg p-6 border border-gray-600 hover:border-accent transition-colors">
      <div className="flex justify-between items-start mb-2">
        <h3 className="text-xl font-bold text-white">{priceData.symbol}</h3>
        <span className="text-sm text-gray-400">
          {new Date(priceData.data.timestamp).toLocaleTimeString()}
        </span>
      </div>

      <div className="flex items-center gap-3 mb-4">
        <div className="text-3xl font-bold text-accent">
          {formatPrice(priceData.data.price)}
        </div>

        <div className={`flex items-center gap-1 ${getPriceChangeColor()}`}>
          {getPriceChangeIcon()}
          <span className="text-sm font-medium">
            {priceChange !== null
              ? `${priceChange > 0 ? '+' : ''}${priceChange.toFixed(3)}%`
              : '—'}
          </span>
        </div>
      </div>

      {/* Mini Chart */}
      <div className="mb-4 bg-gray-800 rounded p-2">
        <MiniChart base={base} quote={quote} />
      </div>

      {priceData.data.volume_24h && (
        <div className="text-sm text-gray-400">
          Volume: {priceData.data.volume_24h.toLocaleString()}
        </div>
      )}
    </div>
  )
}

export default PriceCard
