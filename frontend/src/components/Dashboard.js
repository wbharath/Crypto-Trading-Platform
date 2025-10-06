import React from 'react'
import Navbar from './Navbar'
import MarketOverview from './MarketOverview'
import PriceCard from './PriceCard'

const tradingPairs = [
  { base: 'BTC', quote: 'USDT' },
  { base: 'ETH', quote: 'USDT' },
  { base: 'SOL', quote: 'USDT' },
  { base: 'ADA', quote: 'USDT' },
  { base: 'DOT', quote: 'USDT' },
  { base: 'AVAX', quote: 'USDT' }
]

const Dashboard = () => {
  return (
    <div className="min-h-screen bg-primary">
      {/* Navigation Bar */}
      <Navbar />

      {/* Main Content */}
      <div className="p-6">
        <header className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">
            Crypto Trading Platform
          </h1>
          <p className="text-gray-400">
            Real-time cryptocurrency prices and market data
          </p>
        </header>

        <MarketOverview />

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {tradingPairs.map(({ base, quote }) => (
            <PriceCard key={`${base}-${quote}`} base={base} quote={quote} />
          ))}
        </div>
      </div>
    </div>
  )
}

export default Dashboard
