import { ReactNode } from 'react'
import { cn } from '@/lib/utils'

interface CardProps {
  children: ReactNode
  className?: string
  title?: string
  subtitle?: string
}

export function Card({ children, className, title, subtitle }: CardProps) {
  return (
    <div className={cn(
      'bg-bitcoin-card/50 backdrop-blur-sm rounded-xl border border-white/10 p-6',
      className
    )}>
      {(title || subtitle) && (
        <div className="mb-4">
          {title && <h3 className="text-lg font-semibold text-white">{title}</h3>}
          {subtitle && <p className="text-sm text-gray-400">{subtitle}</p>}
        </div>
      )}
      {children}
    </div>
  )
}

export function StatCard({ 
  label, 
  value, 
  subtext,
  trend,
  className 
}: { 
  label: string
  value: string
  subtext?: string
  trend?: 'up' | 'down' | 'neutral'
  className?: string
}) {
  const trendColors = {
    up: 'text-green-400',
    down: 'text-red-400',
    neutral: 'text-gray-400'
  }

  return (
    <div className={cn(
      'bg-bitcoin-card/50 backdrop-blur-sm rounded-xl border border-white/10 p-6',
      className
    )}>
      <p className="text-sm text-gray-400 mb-1">{label}</p>
      <p className={cn("text-2xl font-bold text-white", trend && trendColors[trend])}>
        {value}
      </p>
      {subtext && <p className="text-xs text-gray-500 mt-1">{subtext}</p>}
    </div>
  )
}

export function SignalCard({ 
  signal, 
  price, 
  nav,
  deviation 
}: { 
  signal: string
  price: string
  nav: string
  deviation: number
}) {
  const colors = {
    overvalued: 'from-red-500/20 to-red-600/10 border-red-500/30',
    undervalued: 'from-green-500/20 to-green-600/10 border-green-500/30',
    fair_value: 'from-amber-500/20 to-amber-600/10 border-amber-500/30',
    unknown: 'from-gray-500/20 to-gray-600/10 border-gray-500/30'
  }

  const labels = {
    overvalued: '🔴 Overvalued',
    undervalued: '🟢 Undervalued',
    fair_value: '🟡 Fair Value',
    unknown: '⚪ Unknown'
  }

  return (
    <div className={cn(
      'rounded-xl border p-6 bg-gradient-to-br',
      colors[signal as keyof typeof colors] || colors.unknown
    )}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-white">Current Valuation</h3>
        <span className="text-2xl font-bold text-white">
          {labels[signal as keyof typeof labels] || labels.unknown}
        </span>
      </div>
      
      <div className="grid grid-cols-3 gap-4">
        <div>
          <p className="text-sm text-gray-400">BTC Price</p>
          <p className="text-xl font-bold text-white">{price}</p>
        </div>
        <div>
          <p className="text-sm text-gray-400">Fundamental NAV</p>
          <p className="text-xl font-bold text-white">{nav}</p>
        </div>
        <div>
          <p className="text-sm text-gray-400">Deviation</p>
          <p className={cn(
            "text-xl font-bold",
            deviation > 0 ? 'text-red-400' : deviation < 0 ? 'text-green-400' : 'text-gray-400'
          )}>
            {deviation > 0 ? '+' : ''}{deviation.toFixed(2)}%
          </p>
        </div>
      </div>
    </div>
  )
}
