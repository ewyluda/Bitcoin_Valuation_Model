import { 
  LatestMetrics, 
  HistoricalData, 
  ValuationStatus, 
  Correlations, 
  Stats,
  SignalHistoryItem 
} from '@/types'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

async function fetchApi<T>(endpoint: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${endpoint}`)
  if (!response.ok) {
    throw new Error(`API error: ${response.status}`)
  }
  return response.json()
}

export const api = {
  getLatestMetrics: () => fetchApi<LatestMetrics>('/api/metrics/latest'),
  
  getHistoricalData: (days?: number) => 
    fetchApi<HistoricalData>(`/api/metrics/historical${days ? `?days=${days}` : ''}`),
  
  getValuationStatus: () => fetchApi<ValuationStatus>('/api/valuation/status'),
  
  getCorrelations: (days?: number) => 
    fetchApi<Correlations>(`/api/correlations${days ? `?days=${days}` : ''}`),
  
  getStats: () => fetchApi<Stats>('/api/stats'),
  
  getSignalHistory: (limit?: number) => 
    fetchApi<SignalHistoryItem[]>(`/api/signals/history${limit ? `?limit=${limit}` : ''}`),
}

export function formatCurrency(value: number | null): string {
  if (value === null || value === undefined) return 'N/A'
  
  if (value >= 1e12) return `$${(value / 1e12).toFixed(2)}T`
  if (value >= 1e9) return `$${(value / 1e9).toFixed(2)}B`
  if (value >= 1e6) return `$${(value / 1e6).toFixed(2)}M`
  if (value >= 1e3) return `$${(value / 1e3).toFixed(2)}K`
  return `$${value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
}

export function formatNumber(value: number | null): string {
  if (value === null || value === undefined) return 'N/A'
  
  if (value >= 1e12) return `${(value / 1e12).toFixed(2)}T`
  if (value >= 1e9) return `${(value / 1e9).toFixed(2)}B`
  if (value >= 1e6) return `${(value / 1e6).toFixed(2)}M`
  if (value >= 1e3) return `${(value / 1e3).toFixed(2)}K`
  return value.toLocaleString()
}

export function getSignalColor(signal: string): string {
  switch (signal) {
    case 'overvalued': return 'text-red-500'
    case 'undervalued': return 'text-green-500'
    case 'fair_value': return 'text-amber-500'
    default: return 'text-gray-500'
  }
}

export function getSignalBgColor(signal: string): string {
  switch (signal) {
    case 'overvalued': return 'bg-red-500/10 border-red-500/30'
    case 'undervalued': return 'bg-green-500/10 border-green-500/30'
    case 'fair_value': return 'bg-amber-500/10 border-amber-500/30'
    default: return 'bg-gray-500/10 border-gray-500/30'
  }
}

export function getSignalLabel(signal: string): string {
  switch (signal) {
    case 'overvalued': return 'Overvalued'
    case 'undervalued': return 'Undervalued'
    case 'fair_value': return 'Fair Value'
    default: return 'Unknown'
  }
}
