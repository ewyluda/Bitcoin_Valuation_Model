'use client'

import { useMemo } from 'react'
import {
  ComposedChart,
  Line,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
  ReferenceLine
} from 'recharts'
import { ChartDataPoint } from '@/types'
import { formatCurrency, formatNumber } from '@/lib/api'

interface MetcalfeChartProps {
  data: ChartDataPoint[]
  height?: number
  showBoundaries?: boolean
}

export function MetcalfeChart({ 
  data, 
  height = 400,
  showBoundaries = true 
}: MetcalfeChartProps) {
  const chartData = useMemo(() => data, [data])

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr)
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric',
      year: '2-digit'
    })
  }

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-bitcoin-card border border-white/20 rounded-lg p-3 shadow-lg">
          <p className="text-sm text-gray-300 mb-2">{formatDate(label)}</p>
          {payload.map((entry: any, idx: number) => (
            <p key={idx} className="text-sm" style={{ color: entry.color }}>
              {entry.name}: {entry.name === 'Active Addresses' 
                ? formatNumber(entry.value)
                : formatCurrency(entry.value)
              }
            </p>
          ))}
        </div>
      )
    }
    return null
  }

  return (
    <ResponsiveContainer width="100%" height={height}>
      <ComposedChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
        <XAxis 
          dataKey="date" 
          tick={{ fill: '#9ca3af', fontSize: 12 }}
          tickFormatter={formatDate}
          stroke="rgba(255,255,255,0.2)"
        />
        <YAxis 
          yAxisId="left"
          tick={{ fill: '#9ca3af', fontSize: 12 }}
          tickFormatter={(value) => `$${(value / 1e9).toFixed(0)}B`}
          stroke="rgba(255,255,255,0.2)"
        />
        <YAxis 
          yAxisId="right"
          orientation="right"
          tick={{ fill: '#9ca3af', fontSize: 12 }}
          tickFormatter={(value) => formatNumber(value)}
          stroke="rgba(255,255,255,0.2)"
        />
        <Tooltip content={<CustomTooltip />} />
        <Legend />

        {showBoundaries && (
          <>
            <Area
              yAxisId="left"
              type="monotone"
              dataKey="upperBound"
              name="Upper Boundary"
              stroke="#ef4444"
              fill="#ef4444"
              fillOpacity={0.1}
              strokeWidth={2}
              strokeDasharray="5 5"
              dot={false}
            />
            <Area
              yAxisId="left"
              type="monotone"
              dataKey="lowerBound"
              name="Lower Boundary"
              stroke="#22c55e"
              fill="#22c55e"
              fillOpacity={0.1}
              strokeWidth={2}
              strokeDasharray="5 5"
              dot={false}
            />
          </>
        )}

        <Line
          yAxisId="left"
          type="monotone"
          dataKey="marketCap"
          name="Market Cap"
          stroke="#F7931A"
          strokeWidth={3}
          dot={false}
          activeDot={{ r: 6, fill: '#F7931A' }}
        />

        <Line
          yAxisId="right"
          type="monotone"
          dataKey="activeAddresses"
          name="Active Addresses"
          stroke="#3b82f6"
          strokeWidth={2}
          dot={false}
        />
      </ComposedChart>
    </ResponsiveContainer>
  )
}

export function PriceVsNavChart({ 
  data, 
  height = 350 
}: { 
  data: ChartDataPoint[]
  height?: number 
}) {
  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr)
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric' 
    })
  }

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-bitcoin-card border border-white/20 rounded-lg p-3 shadow-lg">
          <p className="text-sm text-gray-300 mb-2">{formatDate(label)}</p>
          {payload.map((entry: any, idx: number) => (
            <p key={idx} className="text-sm" style={{ color: entry.color }}>
              {entry.name}: {formatCurrency(entry.value)}
            </p>
          ))}
        </div>
      )
    }
    return null
  }

  return (
    <ResponsiveContainer width="100%" height={height}>
      <ComposedChart data={data} margin={{ top: 10, right: 30, left: 20, bottom: 20 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
        <XAxis 
          dataKey="date" 
          tick={{ fill: '#9ca3af', fontSize: 12 }}
          tickFormatter={formatDate}
          stroke="rgba(255,255,255,0.2)"
        />
        <YAxis 
          tick={{ fill: '#9ca3af', fontSize: 12 }}
          tickFormatter={(value) => `$${(value / 1e9).toFixed(0)}B`}
          stroke="rgba(255,255,255,0.2)"
        />
        <Tooltip content={<CustomTooltip />} />
        <Legend />

        <Line
          type="monotone"
          dataKey="marketCap"
          name="Actual Market Cap"
          stroke="#F7931A"
          strokeWidth={2}
          dot={false}
        />

        <Line
          type="monotone"
          dataKey="fundamentalNav"
          name="Fundamental NAV"
          stroke="#8b5cf6"
          strokeWidth={2}
          strokeDasharray="5 5"
          dot={false}
        />
      </ComposedChart>
    </ResponsiveContainer>
  )
}
