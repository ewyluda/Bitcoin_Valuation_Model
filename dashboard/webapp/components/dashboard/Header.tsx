'use client'

import { Bitcoin, TrendingUp, Info } from 'lucide-react'

export function Header() {
  return (
    <header className="border-b border-white/10 bg-bitcoin-card/30 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-bitcoin-orange/20 rounded-lg">
              <Bitcoin className="w-8 h-8 text-bitcoin-orange" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-white">
                Bitcoin Valuation Dashboard
              </h1>
              <p className="text-sm text-gray-400">
                Based on Metcalfe&apos;s Law
              </p>
            </div>
          </div>

          <nav className="hidden md:flex items-center gap-6">
            <a 
              href="#overview" 
              className="text-sm text-gray-400 hover:text-white transition-colors"
            >
              Overview
            </a>
            <a 
              href="#charts" 
              className="text-sm text-gray-400 hover:text-white transition-colors"
            >
              Charts
            </a>
            <a 
              href="#methodology" 
              className="text-sm text-gray-400 hover:text-white transition-colors"
            >
              Methodology
            </a>
          </nav>

          <a
            href="https://github.com/bitcoin/bitcoin"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 text-sm text-gray-400 hover:text-white transition-colors"
          >
            <TrendingUp className="w-4 h-4" />
            <span className="hidden sm:inline">Live Data</span>
          </a>
        </div>
      </div>
    </header>
  )
}
