import React, { useEffect, useState } from 'react';
import apiClient from '../api/client';
import { TrendingUp, TrendingDown, Activity, Zap, BarChart3, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';

interface MarketData {
  code: string;
  latest_date: string;
  latest_close: number;
  change: number;
  pct_change: number;
  data: Array<{ date: string; close: number; open: number; high: number; low: number; }>;
}

const Home: React.FC = () => {
  const [marketData, setMarketData] = useState<MarketData | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchMarket = async () => {
      try {
        // apiClient interceptor returns response.data directly
        const data = await apiClient.get<MarketData>('/market/index?code=sh.000001&days=30');
        setMarketData(data as any);
      } catch (error) {
        console.error('Failed to fetch market data', error);
      } finally {
        setIsLoading(false);
      }
    };
    fetchMarket();
  }, []);

  // Simple Sparkline
  const Sparkline = ({ data, color }: { data: number[]; color: string }) => {
    if (!data.length) return null;
    const height = 60;
    const width = 150;
    const min = Math.min(...data);
    const max = Math.max(...data);
    const range = max - min || 1;
    
    const points = data.map((d, i) => {
      const x = (i / (data.length - 1)) * width;
      const y = height - ((d - min) / range) * height;
      return `${x},${y}`;
    }).join(' ');

    return (
      <svg width={width} height={height} className="overflow-visible">
        <polyline points={points} fill="none" stroke={color} strokeWidth="2" />
      </svg>
    );
  };

  return (
    <div className="space-y-8">
      {/* Welcome Section */}
      <div className="flex justify-between items-center">
        <div>
           <h1 className="text-2xl font-bold text-gray-800">Market Overview</h1>
           <p className="text-gray-500">Welcome back to OmniAlpha. Here's what's happening today.</p>
        </div>
        <div className="text-sm text-gray-400">
           Data updated: {marketData?.latest_date || new Date().toLocaleDateString()}
        </div>
      </div>

      {/* Market Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Main Index Card */}
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100 relative overflow-hidden">
          <div className="relative z-10">
            <h3 className="text-lg font-semibold text-gray-700 flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-blue-500" /> SSE Composite
            </h3>
            
            {isLoading ? (
              <div className="h-20 flex items-center text-gray-400">Loading...</div>
            ) : marketData ? (
              <div className="mt-4">
                <div className="text-3xl font-bold text-gray-900">
                  {marketData.latest_close.toFixed(2)}
                </div>
                <div className={`flex items-center gap-2 mt-1 ${marketData.change >= 0 ? 'text-red-500' : 'text-green-500'}`}>
                  {marketData.change >= 0 ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
                  <span className="font-medium">{marketData.change > 0 ? '+' : ''}{marketData.change.toFixed(2)}</span>
                  <span className="text-sm">({marketData.change > 0 ? '+' : ''}{marketData.pct_change.toFixed(2)}%)</span>
                </div>
              </div>
            ) : (
              <div className="text-red-400 mt-2">Unavailable</div>
            )}
          </div>
          
          {/* Background Sparkline */}
          {marketData && (
            <div className="absolute right-0 bottom-4 opacity-20">
              <Sparkline 
                data={marketData.data.map(d => Number(d.close))} 
                color={marketData.change >= 0 ? '#ef4444' : '#22c55e'} 
              />
            </div>
          )}
        </div>

        {/* System Status Card */}
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100">
          <h3 className="text-lg font-semibold text-gray-700 flex items-center gap-2">
            <Activity className="w-5 h-5 text-purple-500" /> System Status
          </h3>
          <div className="mt-4 space-y-3">
            <div className="flex justify-between items-center text-sm">
              <span className="text-gray-500">API Connection</span>
              <span className="flex items-center gap-1 text-green-600 font-medium"><span className="w-2 h-2 rounded-full bg-green-500"></span> Active</span>
            </div>
            <div className="flex justify-between items-center text-sm">
              <span className="text-gray-500">Data Feed</span>
              <span className="flex items-center gap-1 text-green-600 font-medium"><span className="w-2 h-2 rounded-full bg-green-500"></span> Baostock</span>
            </div>
             <div className="flex justify-between items-center text-sm">
              <span className="text-gray-500">Last Sync</span>
              <span className="text-gray-700 font-mono">10:05:23</span>
            </div>
          </div>
        </div>

        {/* Quick Actions Card */}
        <div className="bg-gradient-to-br from-blue-600 to-indigo-700 p-6 rounded-lg shadow-sm text-white">
          <h3 className="text-lg font-semibold flex items-center gap-2">
            <Zap className="w-5 h-5" /> Quick Actions
          </h3>
          <div className="mt-4 space-y-2">
            <Link to="/technical" className="block w-full py-2 px-3 bg-white/10 hover:bg-white/20 rounded text-sm transition-colors flex justify-between items-center">
              Run Daily Scan <ArrowRight className="w-4 h-4" />
            </Link>
            <Link to="/ai" className="block w-full py-2 px-3 bg-white/10 hover:bg-white/20 rounded text-sm transition-colors flex justify-between items-center">
              Ask AI Assistant <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      </div>

      {/* Recent Activity Placeholder */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="p-4 border-b border-gray-200 bg-gray-50">
           <h3 className="font-semibold text-gray-800">Recent Signals</h3>
        </div>
        <div className="p-8 text-center text-gray-400 text-sm">
           No recent signals generated. Go to <Link to="/technical" className="text-blue-600 hover:underline">Technical Analysis</Link> to start a scan.
        </div>
      </div>
    </div>
  );
};

export default Home;