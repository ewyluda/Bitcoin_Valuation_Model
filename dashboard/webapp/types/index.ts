export interface LatestMetrics {
  date: string
  price_usd: number
  price_formatted: string
  market_cap_usd: number
  market_cap_formatted: string
  active_addresses: number
  active_addresses_formatted: string
  fundamental_nav: number
  fundamental_nav_formatted: string
  valuation_signal: 'overvalued' | 'undervalued' | 'fair_value'
  deviation_percent: number
}

export interface HistoricalData {
  dates: string[]
  prices: (number | null)[]
  market_caps: (number | null)[]
  active_addresses: (number | null)[]
  metcalfe_upper: (number | null)[]
  metcalfe_lower: (number | null)[]
  fundamental_nav: (number | null)[]
}

export interface ValuationStatus {
  current_price: number
  fundamental_nav: number
  status: 'overvalued' | 'undervalued' | 'fair_value'
  deviation_percent: number
  upper_boundary: number
  lower_boundary: number
  recommendation: string
}

export interface Correlations {
  metcalfe_law: number
  generalized_metcalfe: number
  odlyzko_law: number
}

export interface Stats {
  total_records: number
  date_range_start: string | null
  date_range_end: string | null
  latest_price: number | null
  latest_market_cap: number | null
  latest_active_addresses: number | null
  avg_daily_active_addresses: number | null
  max_price: number | null
  min_price: number | null
}

export interface SignalHistoryItem {
  date: string
  signal: string
  price: number
  deviation_percent: number
}

export interface ChartDataPoint {
  date: string
  price: number | null
  marketCap: number | null
  activeAddresses: number | null
  upperBound: number | null
  lowerBound: number | null
  fundamentalNav: number | null
}
