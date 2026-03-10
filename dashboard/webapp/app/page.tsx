'use client'

import { useState, useEffect } from 'react'
import { Header } from '@/components/dashboard/Header'
import { StatsGrid } from '@/components/dashboard/StatsGrid'
import { Methodology } from '@/components/dashboard/Methodology'
import { MetcalfeChart, PriceVsNavChart } from '@/components/charts/MetcalfeChart'
import { Card } from '@/components/ui/Card'
import { api, formatCurrency } from '@/lib/api'
import { LatestMetrics, HistoricalData, Stats, Correlations, ChartDataPoint } from '@/types'
import { Activity, BarChart3, RefreshCw, TrendingUp } from 'lucide-react'

export default function Home() {
  const [metrics, setMetrics] = useState<LatestMetrics | null>(null)
  const [historicalData, setHistoricalData] = useState<HistoricalData | null>(null)
  const [stats, setStats] = useState<Stats | null>(null)
  const [correlations, setCorrelations] = useState<Correlations | null>(null)
  const [loading, setLoading] = useState(true)
  const [daysRange, setDaysRange] = useState(365)
  const [error, setError] = useState<string | null>(null)

  const fetchData = async () => {
    setLoading(true)
    setError(null)
    try {
      const [metricsData, historicalDataRes, statsData, corrData] = await Promise.all([
        api.getLatestMetrics(),
        api.getHistoricalData(daysRange),
        api.getStats(),
        api.getCorrelations(daysRange)
      ])
      setMetrics(metricsData)
      setHistoricalData(historicalDataRes)
      setStats(statsData)
      setCorrelations(corrData)
    } catch (err) {
      setError('Failed to fetch data. Please ensure the API server is running.')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
    // Refresh every 5 minutes
    const interval = setInterval(fetchData, 5 * 60 * 1000)
    return () => clearInterval(interval)
  }, [daysRange])

  const chartData: ChartDataPoint[] = historicalData 
    ? historicalData.dates.map((date, i) => ({
        date,
        price: historicalData.prices[i],
        marketCap: historicalData.market_caps[i],
        activeAddresses: historicalData.active_addresses[i],
        upperBound: historicalData.metcalfe_upper[i],
        lowerBound: historicalData.metcalfe_lower[i],
        fundamentalNav: historicalData.fundamental_nav[i]
      }))
    : []

  return (
    <div className="min-h-screen bg-gradient-to-b from-[#1a1a2e] to-[#16213e]">
      <Header />
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Error Message */}
        {error && (
          <div className="mb-6 p-4 bg-red-500/10 border border-red-500/30 rounded-lg text-red-400">
            {error}
          </div>
        )}

        {/* Stats Section */}
        <section id="overview" className="mb-10">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-2">
              <Activity className="w-5 h-5 text-bitcoin-orange" />
              <h2 className="text-xl font-bold text-white">Market Overview</h2>
            </div>
            <button
              onClick={fetchData}
              disabled={loading}
              className="flex items-center gap-2 px-4 py-2 bg-bitcoin-card/50 hover:bg-bitcoin-card 
                       rounded-lg text-sm text-gray-300 transition-colors disabled:opacity-50"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </button>
          </div>

          <StatsGrid metrics={metrics} stats={stats} />
        </section>

        {/* Charts Section */}
        <section id="charts" className="mb-10">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
            <div className="flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-bitcoin-orange" />
              <h2 className="text-xl font-bold text-white">Analysis Charts</h2>
            </div>
            
            {/* Time Range Selector */}
            <div className="flex items-center gap-2">
              {[30, 90, 180, 365].map((days) => (
                <button
                  key={days}
                  onClick={() => setDaysRange(days)}
                  className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors
                    ${daysRange === days 
                      ? 'bg-bitcoin-orange text-white' 
                      : 'bg-bitcoin-card/50 text-gray-400 hover:text-white'
                    }`}
                >
                  {days}D
                </button>
              ))}
              <button
                onClick={() => setDaysRange(2000)}
                className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors
                  ${daysRange === 2000 
                    ? 'bg-bitcoin-orange text-white' 
                    : 'bg-bitcoin-card/50 text-gray-400 hover:text-white'
                  }`}
              >
                ALL
              </button>
            </div>
          </div>

          <div className="grid grid-cols-1 gap-6">
            {/* Metcalfe Chart */}
            <Card 
              title="Metcalfe's Law Boundaries" 
              subtitle="Market Cap vs Daily Active Addresses with Fundamental Boundaries"
            >
              {loading ? (
                <div className="h-[400px] flex items-center justify-center">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-bitcoin-orange" />
                </div>
              ) : (
                <MetcalfeChart data={chartData} height={400} showBoundaries={true} />
              )}
            </Card>

            {/* Price vs NAV Chart */}
            <Card 
              title="Actual vs Fundamental NAV" 
              subtitle="Market Cap compared to Metcalfe-derived Fundamental Value"
            >
              {loading ? (
                <div className="h-[350px] flex items-center justify-center">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-bitcoin-orange" />
                </div>
              ) : (
                <PriceVsNavChart data={chartData} height={350} />
              )}
            </Card>
          </div>
        </section>

        {/* Correlations Section */}
        {correlations && (
          <section className="mb-10">
            <div className="flex items-center gap-2 mb-6">
              <TrendingUp className="w-5 h-5 text-bitcoin-orange" />
              <h2 className="text-xl font-bold text-white">Model Correlations</h2>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-bitcoin-card/50 rounded-xl border border-white/10 p-5">
                <p className="text-sm text-gray-400 mb-2">Metcalfe&apos;s Law (n²)</p>
                <div className="flex items-end gap-2">
                  <p className="text-3xl font-bold text-white">
                    {(correlations.metcalfe_law * 100).toFixed(2)}%
                  </p>
                  <p className="text-xs text-gray-500 mb-1">correlation</p>
                </div>
                <div className="mt-3 h-2 bg-gray-700 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-bitcoin-orange rounded-full"
                    style={{ width: `${correlations.metcalfe_law * 100}%` }}
                  />
                </div>
              </div>

              <div className="bg-bitcoin-card/50 rounded-xl border border-white/10 p-5">
                <p className="text-sm text-gray-400 mb-2">Generalized (n^1.5)</p>
                <div className="flex items-end gap-2">
                  <p className="text-3xl font-bold text-white">
                    {(correlations.generalized_metcalfe * 100).toFixed(2)}%
                  </p>
                  <p className="text-xs text-gray-500 mb-1">correlation</p>
                </div>
                <div className="mt-3 h-2 bg-gray-700 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-purple-500 rounded-full"
                    style={{ width: `${correlations.generalized_metcalfe * 100}%` }}
                  />
                </div>
              </div>

              <div className="bg-bitcoin-card/50 rounded-xl border border-white/10 p-5">
                <p className="text-sm text-gray-400 mb-2">Odlyzko&apos;s Law (n×ln n)</p>
                <div className="flex items-end gap-2">
                  <p className="text-3xl font-bold text-white">
                    {(correlations.odlyzko_law * 100).toFixed(2)}%
                  </p>
                  <p className="text-xs text-gray-500 mb-1">correlation</p>
                </div>
                <div className="mt-3 h-2 bg-gray-700 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-green-500 rounded-full"
                    style={{ width: `${correlations.odlyzko_law * 100}%` }}
                  />
                </div>
              </div>
            </div>
          </section>
        )}

        {/* Methodology Section */}
        <Methodology />

        {/* Footer */}
        <footer className="mt-16 py-8 border-t border-white/10 text-center">
          <p className="text-sm text-gray-500">
            Data sourced from BGeometrics API. Valuation model based on Metcalfe&apos;s Law.
          </p>
          <p className="text-xs text-gray-600 mt-2">
            Not financial advice. For educational purposes only.
          </p>
        </footer>
      </main>
    </div>
  )
}
