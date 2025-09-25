import React, { useState, useEffect } from 'react'
import { LineChart, Line, ResponsiveContainer, YAxis } from 'recharts'
import { getPrice } from '../services/api'

const MiniChart = ({ base, quote }) => {
  const [chartData, setChartData] = useState([])
  const [trend, setTrend] = useState('neutral')

  useEffect(() => {
    const collectPriceData = async () => {
      try {
        const response = await getPrice(base, quote)
        const currentPrice = response.data.data.price
        const timestamp = new Date().getTime()

        setChartData((prevData) => {
          const newData = [
            ...prevData,
            {
              timestamp,
              price: currentPrice,
              time: new Date().toLocaleTimeString()
            }
          ]

          // Keep only last 20 data points
          const limitedData = newData.slice(-20)

          // Calculate trend
          if (limitedData.length >= 2) {
            const firstPrice = limitedData[0].price
            const lastPrice = limitedData[limitedData.length - 1].price
            const change = ((lastPrice - firstPrice) / firstPrice) * 100

            if (change > 0.1) setTrend('up')
            else if (change < -0.1) setTrend('down')
            else setTrend('neutral')
          }

          return limitedData
        })
      } catch (error) {
        console.error(`Failed to fetch chart data for ${base}/${quote}:`, error)
      }
    }

    // Initial data collection
    collectPriceData()

    // Collect data every 30 seconds
    const interval = setInterval(collectPriceData, 30000)
    return () => clearInterval(interval)
  }, [base, quote])

  const getLineColor = () => {
    switch (trend) {
      case 'up':
        return '#22c55e'
      case 'down':
        return '#ef4444'
      default:
        return '#10b981'
    }
  }

  if (chartData.length < 2) {
    return (
      <div className="h-16 flex items-center justify-center text-gray-500 text-sm">
        Collecting data...
      </div>
    )
  }

  return (
    <div className="h-16 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData}>
          <YAxis domain={['dataMin', 'dataMax']} hide />
          <Line
            type="monotone"
            dataKey="price"
            stroke={getLineColor()}
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 3, fill: getLineColor() }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}

export default MiniChart
