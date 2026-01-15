import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import apiClient from '../api/client';
import { ArrowLeft, TrendingUp, TrendingDown, Activity, Calendar } from 'lucide-react';

interface StockData {
  code: string;
  name?: string;
  data: Array<{
    date: string;
    open: number;
    high: number;
    low: number;
    close: number;
    volume: number;
    amount: number;
    turn: number;
    pctChg: number;
  }>;
}

const StockDetail: React.FC = () => {
  const { code } = useParams<{ code: string }>();
  const navigate = useNavigate();
  const [stock, setStock] = useState<StockData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStock = async () => {
      if (!code) return;
      try {
        setLoading(true);
        // Assuming API returns { code: string, data: [...] }
        const data = await apiClient.get<StockData>(`/stock/${code}`);
        setStock(data as any);
      } catch (err: any) {
        console.error(err);
        setError('Failed to load stock data.');
      } finally {
        setLoading(false);
      }
    };
    fetchStock();
  }, [code]);

  // --- Visualization Helpers ---
  const Chart = ({ data }: { data: StockData['data'] }) => {
    if (!data || data.length === 0) return <div className="text-center text-gray-400 py-10">No Data</div>;

    // Use last 100 days for better visibility if dataset is large
    const viewData = data.slice(-60); 
    
    const width = 800;
    const height = 400;
    const padding = { top: 20, right: 50, bottom: 30, left: 50 };
    const chartWidth = width - padding.left - padding.right;
    const chartHeight = height - padding.top - padding.bottom;

    const minPrice = Math.min(...viewData.map(d => d.low));
    const maxPrice = Math.max(...viewData.map(d => d.high));
    const priceRange = maxPrice - minPrice || 1;

    const getX = (i: number) => padding.left + (i / (viewData.length)) * chartWidth + (chartWidth / viewData.length) / 2;
    const getY = (price: number) => padding.top + chartHeight - ((price - minPrice) / priceRange) * chartHeight;

    const candleWidth = (chartWidth / viewData.length) * 0.6;

    // Y Axis Ticks
    const ticks = 5;
    const yTicks = Array.from({ length: ticks }).map((_, i) => {
        const val = minPrice + (i / (ticks - 1)) * priceRange;
        return { val, y: getY(val) };
    });

    return (
      <div className="w-full overflow-x-auto">
        <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-auto bg-white border border-gray-100 rounded">
          {/* Grid & Axis */}
          {yTicks.map(tick => (
             <g key={tick.val}>
                 <line x1={padding.left} y1={tick.y} x2={width - padding.right} y2={tick.y} stroke="#f0f0f0" />
                 <text x={width - padding.right + 5} y={tick.y + 4} fontSize="10" fill="#9ca3af">{tick.val.toFixed(2)}</text>
             </g>
          ))}

          {/* Candles */}
          {viewData.map((d, i) => {
             const x = getX(i);
             const isUp = d.close >= d.open;
             const color = isUp ? '#ef4444' : '#22c55e'; // Red for up, Green for down (China market style)
             
             return (
               <g key={d.date} className="hover:opacity-80">
                 {/* High-Low Line */}
                 <line x1={x} y1={getY(d.high)} x2={x} y2={getY(d.low)} stroke={color} strokeWidth="1" />
                 {/* Open-Close Box */}
                 <rect 
                    x={x - candleWidth / 2} 
                    y={Math.min(getY(d.open), getY(d.close))} 
                    width={candleWidth} 
                    height={Math.abs(getY(d.open) - getY(d.close)) || 1} 
                    fill={color} 
                 />
                 {/* Date Label (Sparse) */}
                 {i % 10 === 0 && (
                    <text x={x} y={height - 10} fontSize="10" fill="#9ca3af" textAnchor="middle">{d.date.slice(5)}</text>
                 )}
               </g>
             );
          })}
        </svg>
      </div>
    );
  };

  if (loading) return <div className="flex h-full items-center justify-center text-gray-500">Loading stock data...</div>;
  if (error || !stock) return (
      <div className="flex flex-col items-center justify-center h-full gap-4">
          <div className="text-red-500">{error || 'Stock not found'}</div>
          <button onClick={() => navigate(-1)} className="text-blue-600 hover:underline flex items-center gap-1">
              <ArrowLeft className="w-4 h-4" /> Go Back
          </button>
      </div>
  );

  const lastDay = stock.data[stock.data.length - 1];
  const prevDay = stock.data.length > 1 ? stock.data[stock.data.length - 2] : null;
  const change = prevDay ? lastDay.close - prevDay.close : 0;
  
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <button onClick={() => navigate(-1)} className="p-2 hover:bg-gray-100 rounded-full transition-colors">
            <ArrowLeft className="w-5 h-5 text-gray-600" />
        </button>
        <div>
            <h1 className="text-2xl font-bold text-gray-800 flex items-center gap-3">
                {code} 
                <span className={`text-lg px-2 py-0.5 rounded font-mono ${change >= 0 ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'}`}>
                    {lastDay.close.toFixed(2)}
                </span>
            </h1>
            <p className="text-gray-500 text-sm">Daily K-Line Data • Source: Baostock</p>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-100">
              <div className="text-sm text-gray-500 mb-1">Change</div>
              <div className={`text-lg font-semibold flex items-center gap-1 ${change >= 0 ? 'text-red-600' : 'text-green-600'}`}>
                  {change >= 0 ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
                  {change.toFixed(2)} ({lastDay.pctChg.toFixed(2)}%)
              </div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-100">
              <div className="text-sm text-gray-500 mb-1">Volume</div>
              <div className="text-lg font-semibold text-gray-800">
                  {(lastDay.volume / 10000).toFixed(2)} 万
              </div>
          </div>
           <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-100">
              <div className="text-sm text-gray-500 mb-1">Turnover</div>
              <div className="text-lg font-semibold text-gray-800">
                  {lastDay.turn.toFixed(2)}%
              </div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-100">
              <div className="text-sm text-gray-500 mb-1">Date</div>
              <div className="text-lg font-semibold text-gray-800 flex items-center gap-2">
                  <Calendar className="w-4 h-4 text-gray-400" /> {lastDay.date}
              </div>
          </div>
      </div>

      {/* Chart */}
      <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
              <Activity className="w-5 h-5 text-blue-600" /> Price Action
          </h3>
          <Chart data={stock.data} />
      </div>
    </div>
  );
};

export default StockDetail;
