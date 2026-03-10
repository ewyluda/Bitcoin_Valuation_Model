'use client'

import { StatCard, SignalCard } from '@/components/ui/Card'
import { LatestMetrics, Stats } from '@/types'
import { formatCurrency, formatNumber } from '@/lib/api'
import { Activity, DollarSign, Users, TrendingUp } from 'lucide-react'

interface StatsGridProps {
  metrics: LatestMetrics | null
  stats: Stats | null
}

export function StatsGrid({ metrics, stats }: StatsGridProps) {
  if (!metrics) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 animate-pulse">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="h-24 bg-bitcoin-card/50 rounded-xl" />
        ))}
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Signal Card */}
      <SignalCard
        signal={metrics.valuation_signal}
        price={metrics.price_formatted}
        nav={metrics.fundamental_nav_formatted}
        deviation={metrics.deviation_percent}
      />

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-bitcoin-card/50 backdrop-blur-sm rounded-xl border border-white/10 p-5">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-bitcoin-orange/20 rounded-lg">
              <DollarSign className="w-5 h-5 text-bitcoin-orange" />
            </div>
            <span className="text-sm text-gray-400">BTC Price</span>
          </div>
          <p className="text-2xl font-bold text-white">{metrics.price_formatted}</p>
          <p className="text-xs text-gray-500 mt-1">
            As of {new Date(metrics.date).toLocaleDateString()}
          </p>
        </div>

        <div className="bg-bitcoin-card/50 backdrop-blur-sm rounded-xl border border-white/10 p-5">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-purple-500/20 rounded-lg">
              <TrendingUp className="w-5 h-5 text-purple-400" />
            </div>
            <span className="text-sm text-gray-400">Market Cap</span>
          </div>
          <p className="text-2xl font-bold text-white">{metrics.market_cap_formatted}</p>
          <p className="text-xs text-gray-500 mt-1">
            Network Value
          </p>
        </div>

        <div className="bg-bitcoin-card/50 backdrop-blur-sm rounded-xl border border-white/10 p-5">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-blue-500/20 rounded-lg">
              <Users className="w-5 h-5 text-blue-400" />
            </div>
            <span className="text-sm text-gray-400">Daily Active</span>
          </div>
          <p className="text-2xl font-bold text-white">{metrics.active_addresses_formatted}</p>
          <p className="text-xs text-gray-500 mt-1">
            Active Addresses
          </p>
        </div>

        <div className="bg-bitcoin-card/50 backdrop-blur-sm rounded-xl border border-white/10 p-5">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-emerald-500/20 rounded-lg">
              <Activity className="w-5 h-5 text-emerald-400" />
            </div>
            <span className="text-sm text-gray-400">Fundamental NAV</span>
          </div>
          <p className="text-2xl font-bold text-white">{metrics.fundamental_nav_formatted}</p>
          <p className="text-xs text-gray-500 mt-1">
            Based on Metcalfe&apos;s Law
          </p>
        </div>
      </div>

      {/* Database Stats */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-bitcoin-card/30 rounded-lg border border-white/5 p-4">
            <p className="text-xs text-gray-500 mb-1">Data Points</p>
            <p className="text-lg font-semibold text-white">{stats.total_records.toLocaleString()}</p>
          </div>
          <div className="bg-bitcoin-card/30 rounded-lg border border-white/5 p-4">
            <p className="text-xs text-gray-500 mb-1">Date Range</p>
            <p className="text-sm font-semibold text-white">
              {stats.date_range_start ? new Date(stats.date_range_start).getFullYear() : 'N/A'} - 
              {stats.date_range_end ? new Date(stats.date_range_end).getFullYear() : 'N/A'}
            </p>
          </div>
          <div className="bg-bitcoin-card/30 rounded-lg border border-white/5 p-4">
            <p className="text-xs text-gray-500 mb-1">Avg DAA</p>
            <p className="text-lg font-semibold text-white">
              {stats.avg_daily_active_addresses ? formatNumber(stats.avg_daily_active_addresses) : 'N/A'}
            </p>
          </div>
          <div className="bg-bitcoin-card/30 rounded-lg border border-white/5 p-4">
            <p className="text-xs text-gray-500 mb-1">ATH Price</p>
            <p className="text-lg font-semibold text-white">
              {stats.max_price ? formatCurrency(stats.max_price) : 'N/A'}
            </p>
          </div>
        </div>
      )}
    </div>
  )
}
