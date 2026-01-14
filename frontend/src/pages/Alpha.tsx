import React, { useState, useEffect } from 'react';
import apiClient from '../api/client';
import { Search, Play, Activity, Info, TrendingUp, TrendingDown } from 'lucide-react';

// Types
interface AlphaFactor {
  key: string;
  name: string;
  description: string;
  category: string;
}

interface AlphaDataPoint {
  date: string;
  close: number;
  value: number;
}

interface AlphaResult {
  code: string;
  factor: string;
  data: AlphaDataPoint[];
}

const Alpha: React.FC = () => {
  // State
  const [factors, setFactors] = useState<AlphaFactor[]>([]);
  const [selectedFactor, setSelectedFactor] = useState<AlphaFactor | null>(null);
  const [stockCode, setStockCode] = useState<string>('sh.600000');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [result, setResult] = useState<AlphaResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Load factors on mount
  useEffect(() => {
    const fetchFactors = async () => {
      try {
        const response = await apiClient.get<AlphaFactor[]>('/alpha/factors');
        // apiClient returns data directly
        if (Array.isArray(response)) {
          setFactors(response as any);
          if (response.length > 0) {
            setSelectedFactor((response as any)[0]);
          }
        }
      } catch (err) {
        console.error('Failed to fetch factors', err);
        setError('Failed to load factor list.');
      }
    };
    fetchFactors();
  }, []);

  // Calculate Handler
  const handleCalculate = async () => {
    if (!selectedFactor || !stockCode) return;
    
    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await apiClient.get<AlphaResult>('/alpha/calculate', {
        params: {
          code: stockCode,
          factor: selectedFactor.key,
          days: 365
        }
      });
      setResult(data as any);
    } catch (err: any) {
      console.error(err);
      setError(err.response?.data?.detail || 'Calculation failed');
    } finally {
      setIsLoading(false);
    }
  };

  // Simple Chart Component using SVG
  const SimpleChart = ({ data }: { data: AlphaDataPoint[] }) => {
    if (!data || data.length === 0) return null;

    const width = 800;
    const height = 300;
    const padding = 40;
    const graphWidth = width - padding * 2;
    const graphHeight = height - padding * 2;

    // Scales
    const minVal = Math.min(...data.map(d => d.value));
    const maxVal = Math.max(...data.map(d => d.value));
    const minPrice = Math.min(...data.map(d => d.close));
    const maxPrice = Math.max(...data.map(d => d.close));
    
    // Helper to normalize
    const getX = (i: number) => padding + (i / (data.length - 1)) * graphWidth;
    const getY = (val: number, min: number, max: number) => {
        const range = max - min || 1;
        return height - padding - ((val - min) / range) * graphHeight;
    };

    // Paths
    const factorPath = data.map((d, i) => 
      `${i === 0 ? 'M' : 'L'} ${getX(i)} ${getY(d.value, minVal, maxVal)}`
    ).join(' ');

    const pricePath = data.map((d, i) => 
      `${i === 0 ? 'M' : 'L'} ${getX(i)} ${getY(d.close, minPrice, maxPrice)}`
    ).join(' ');

    return (
      <div className="w-full overflow-x-auto">
        <svg width={width} height={height} className="border border-gray-100 rounded bg-white">
          {/* Grid lines */}
          <line x1={padding} y1={height - padding} x2={width - padding} y2={height - padding} stroke="#eee" />
          <line x1={padding} y1={padding} x2={padding} y2={height - padding} stroke="#eee" />
          
          {/* Price Line (Light Gray) */}
          <path d={pricePath} fill="none" stroke="#e5e7eb" strokeWidth="2" />
          
          {/* Factor Line (Blue) */}
          <path d={factorPath} fill="none" stroke="#2563eb" strokeWidth="2" />

          {/* Legend */}
          <g transform={`translate(${padding}, 20)`}>
            <line x1="0" y1="0" x2="20" y2="0" stroke="#2563eb" strokeWidth="2" />
            <text x="25" y="4" fontSize="12" fill="#666">Alpha Factor</text>
            <line x1="100" y1="0" x2="120" y2="0" stroke="#e5e7eb" strokeWidth="2" />
            <text x="125" y="4" fontSize="12" fill="#666">Stock Price</text>
          </g>
        </svg>
      </div>
    );
  };

  return (
    <div className="flex flex-col md:flex-row h-full gap-6">
      {/* Sidebar: Factor List */}
      <div className="w-full md:w-80 flex-shrink-0 bg-white p-4 rounded-lg shadow-sm border border-gray-200 flex flex-col h-[calc(100vh-100px)]">
        <div className="flex items-center gap-2 mb-4">
          <Activity className="w-5 h-5 text-purple-600" />
          <h2 className="text-lg font-semibold text-gray-800">Alpha Factors</h2>
        </div>

        {/* Search - Placeholder for now */}
        <div className="relative mb-4">
          <input 
            type="text" 
            placeholder="Search factors..." 
            className="w-full pl-9 pr-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
          />
          <Search className="w-4 h-4 text-gray-400 absolute left-3 top-2.5" />
        </div>

        <div className="flex-1 overflow-y-auto space-y-1 pr-1">
          {factors.map(factor => (
            <button
              key={factor.key}
              onClick={() => setSelectedFactor(factor)}
              className={`w-full text-left px-3 py-3 rounded-md transition-colors ${
                selectedFactor?.key === factor.key 
                  ? 'bg-purple-50 border-purple-200 border text-purple-900' 
                  : 'hover:bg-gray-50 text-gray-700 border border-transparent'
              }`}
            >
              <div className="font-medium text-sm flex justify-between">
                {factor.name}
                <span className="text-xs text-gray-400 font-normal">{factor.key}</span>
              </div>
              <div className="text-xs text-gray-500 mt-1 line-clamp-2" title={factor.description}>
                {factor.description}
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Main Content: Calculator */}
      <div className="flex-1 flex flex-col min-w-0 gap-6">
        
        {/* Controls */}
        <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
          <div className="flex flex-col md:flex-row gap-4 items-end md:items-center">
            <div className="flex-1 w-full">
              <label className="block text-sm font-medium text-gray-700 mb-1">Target Stock</label>
              <div className="flex gap-2">
                 <input
                  type="text"
                  value={stockCode}
                  onChange={(e) => setStockCode(e.target.value)}
                  className="flex-1 p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-purple-500 font-mono uppercase"
                  placeholder="sh.600000"
                />
              </div>
            </div>
            
            <button
              onClick={handleCalculate}
              disabled={isLoading || !selectedFactor}
              className={`px-6 py-2 rounded-md flex items-center gap-2 text-white font-medium transition-colors ${
                isLoading ? 'bg-purple-400' : 'bg-purple-600 hover:bg-purple-700'
              }`}
            >
              <Play className="w-4 h-4" /> 
              {isLoading ? 'Calculating...' : 'Calculate Alpha'}
            </button>
          </div>
          
          {selectedFactor && (
            <div className="mt-4 p-3 bg-gray-50 rounded text-sm text-gray-600 flex gap-2 items-start border border-gray-100">
              <Info className="w-4 h-4 mt-0.5 text-gray-400 flex-shrink-0" />
              <div>
                <span className="font-semibold text-gray-700">Formula/Logic: </span>
                {selectedFactor.description}
              </div>
            </div>
          )}

          {error && (
            <div className="mt-4 p-3 bg-red-50 text-red-600 text-sm rounded border border-red-100">
              {error}
            </div>
          )}
        </div>

        {/* Results */}
        {result && (
          <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200 flex-1 flex flex-col min-h-[400px]">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-lg font-semibold text-gray-800">Analysis Result</h3>
              <div className="flex gap-4 text-sm">
                <div className="flex items-center gap-1 text-gray-500">
                   <TrendingUp className="w-4 h-4" /> Latest: <span className="font-mono font-medium text-gray-900">{result.data[result.data.length-1].value.toFixed(4)}</span>
                </div>
                <div className="flex items-center gap-1 text-gray-500">
                   <span className="text-gray-400">|</span> Price: <span className="font-mono font-medium text-gray-900">{result.data[result.data.length-1].close.toFixed(2)}</span>
                </div>
              </div>
            </div>

            <div className="flex-1 flex items-center justify-center bg-gray-50 rounded border border-gray-100 p-4 overflow-hidden">
                <SimpleChart data={result.data} />
            </div>

            {/* Simple Stats Table */}
             <div className="mt-4 overflow-x-auto">
                <table className="min-w-full text-sm text-left text-gray-500">
                    <thead className="text-xs text-gray-700 uppercase bg-gray-50">
                        <tr>
                            <th className="px-4 py-2">Date</th>
                            <th className="px-4 py-2">Close</th>
                            <th className="px-4 py-2">Factor Value</th>
                        </tr>
                    </thead>
                    <tbody>
                        {result.data.slice().reverse().slice(0, 5).map((row, idx) => (
                            <tr key={idx} className="bg-white border-b hover:bg-gray-50">
                                <td className="px-4 py-2 font-mono">{row.date}</td>
                                <td className="px-4 py-2 font-mono">{row.close.toFixed(2)}</td>
                                <td className={`px-4 py-2 font-mono font-medium ${row.value > 0 ? 'text-red-600' : row.value < 0 ? 'text-green-600' : ''}`}>
                                    {row.value.toFixed(6)}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
                <p className="text-xs text-gray-400 mt-2 text-center">Showing last 5 records</p>
            </div>
          </div>
        )}

      </div>
    </div>
  );
};

export default Alpha;