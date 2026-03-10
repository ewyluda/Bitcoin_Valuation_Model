'use client'

import { Card } from '@/components/ui/Card'
import { BookOpen, Calculator, TrendingUp } from 'lucide-react'

export function Methodology() {
  return (
    <section id="methodology" className="py-8">
      <div className="flex items-center gap-2 mb-6">
        <BookOpen className="w-5 h-5 text-bitcoin-orange" />
        <h2 className="text-xl font-bold text-white">Methodology</h2>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card 
          title="Metcalfe's Law" 
          subtitle="Upper Boundary (NV ~ n²)"
          className="lg:col-span-1"
        >
          <div className="space-y-4">
            <div className="bg-black/30 rounded-lg p-4 font-mono text-sm text-center">
              <p className="text-bitcoin-orange">Network Value ∝ n²</p>
              <p className="text-gray-400 text-xs mt-2">n = Daily Active Addresses</p>
            </div>
            <p className="text-sm text-gray-300">
              Metcalfe&apos;s Law states that the value of a network is proportional 
              to the square of the number of connected users. We use this as the 
              <span className="text-red-400"> upper fundamental boundary</span>.
            </p>
            <div className="text-xs text-gray-500">
              <p>Constants: a₁ = 0, b₁ = 1</p>
            </div>
          </div>
        </Card>

        <Card 
          title="Odlyzko's Law" 
          subtitle="Lower Boundary (NV ~ n×ln(n))"
          className="lg:col-span-1"
        >
          <div className="space-y-4">
            <div className="bg-black/30 rounded-lg p-4 font-mono text-sm text-center">
              <p className="text-green-400">Network Value ∝ n×ln(n)</p>
              <p className="text-gray-400 text-xs mt-2">n = Daily Active Addresses</p>
            </div>
            <p className="text-sm text-gray-300">
              Odlyzko proposed a more conservative variation accounting for 
              unequal user contributions. We use this as the 
              <span className="text-green-400"> lower fundamental boundary</span>.
            </p>
            <div className="text-xs text-gray-500">
              <p>Constants: a₂ = -3.48, b₂ = 1.65</p>
            </div>
          </div>
        </Card>

        <Card 
          title="Fundamental NAV" 
          subtitle="Fair Value Estimate"
          className="lg:col-span-1"
        >
          <div className="space-y-4">
            <div className="bg-black/30 rounded-lg p-4 font-mono text-sm text-center">
              <p className="text-purple-400">NAV = (Upper + Lower) / 2</p>
              <p className="text-gray-400 text-xs mt-2">Midpoint of boundaries</p>
            </div>
            <p className="text-sm text-gray-300">
              The fundamental NAV is calculated as the midpoint between the 
              upper and lower boundaries. When price deviates significantly 
              from NAV, it may indicate over/undervaluation.
            </p>
            <div className="text-xs text-gray-500">
              <p>SMA Window: 30 days</p>
            </div>
          </div>
        </Card>
      </div>

      {/* Signal Legend */}
      <div className="mt-6 bg-bitcoin-card/30 rounded-xl border border-white/10 p-6">
        <h3 className="text-lg font-semibold text-white mb-4">Valuation Signals</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="flex items-start gap-3 p-4 bg-red-500/10 rounded-lg border border-red-500/20">
            <div className="w-3 h-3 rounded-full bg-red-500 mt-1.5" />
            <div>
              <p className="font-medium text-red-400">Overvalued</p>
              <p className="text-sm text-gray-400">
                Market cap exceeds Metcalfe upper boundary. Network value is 
                not fully supported by on-chain activity.
              </p>
            </div>
          </div>
          <div className="flex items-start gap-3 p-4 bg-amber-500/10 rounded-lg border border-amber-500/20">
            <div className="w-3 h-3 rounded-full bg-amber-500 mt-1.5" />
            <div>
              <p className="font-medium text-amber-400">Fair Value</p>
              <p className="text-sm text-gray-400">
                Market cap is within fundamental boundaries. Price is reasonably 
                aligned with network activity.
              </p>
            </div>
          </div>
          <div className="flex items-start gap-3 p-4 bg-green-500/10 rounded-lg border border-green-500/20">
            <div className="w-3 h-3 rounded-full bg-green-500 mt-1.5" />
            <div>
              <p className="font-medium text-green-400">Undervalued</p>
              <p className="text-sm text-gray-400">
                Market cap falls below Odlyzko lower boundary. Network activity 
                suggests higher potential value.
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
