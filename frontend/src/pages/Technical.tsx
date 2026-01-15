import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import apiClient from '../api/client';
import { Play, Settings, Filter, Download, AlertCircle, Loader2 } from 'lucide-react';
import { useTranslation } from '../contexts/LanguageContext';

interface Strategy {
  key: string;
  name: string;
  description: string;
  category: string;
}

interface ScanResult {
  code: string;
  name: string;
  date: string;
  matches: Record<string, boolean>; // or similar structure depending on engine output
  [key: string]: any;
}

interface LogMessage {
  type: 'info' | 'error' | 'success';
  message: string;
  timestamp: string;
}

const Technical: React.FC = () => {
  const { t } = useTranslation();
  // State
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [selectedStrategies, setSelectedStrategies] = useState<string[]>([]);
  const [poolType, setPoolType] = useState<string>('hs300');
  const [customStocks, setCustomStocks] = useState<string>('');
  const [date, setDate] = useState<string>(new Date().toISOString().split('T')[0]);
  
  const [isScanning, setIsScanning] = useState(false);
  const [scanResults, setScanResults] = useState<ScanResult[]>([]);
  const [progress, setProgress] = useState<{ current: number; total: number } | null>(null);
  const [logs, setLogs] = useState<LogMessage[]>([]);

  // Effects
  useEffect(() => {
    fetchStrategies();
  }, []);

  const fetchStrategies = async () => {
    try {
      const data = await apiClient.get<Strategy[]>('/strategies');
      // axios returns data directly due to interceptor in client.ts
      // but let's double check if client.ts returns response.data or response
      // client.ts: return response.data;
      // So 'data' is the array.
      if (Array.isArray(data)) {
        setStrategies(data as any);
      }
    } catch (error) {
      addLog('error', t('technical.loadStrategiesFailed'));
    }
  };

  const addLog = (type: 'info' | 'error' | 'success', message: string) => {
    setLogs(prev => [{ type, message, timestamp: new Date().toLocaleTimeString() }, ...prev].slice(0, 50));
  };

  const toggleStrategy = (key: string) => {
    setSelectedStrategies(prev => 
      prev.includes(key) ? prev.filter(k => k !== key) : [...prev, key]
    );
  };

  const handleScan = async () => {
    if (selectedStrategies.length === 0) {
      addLog('error', t('technical.selectStrategy'));
      return;
    }

    // 验证自定义股票池
    let customPool: string[] | undefined;
    if (poolType === 'custom') {
      const codes = customStocks
        .split(/[,\n\s]+/)
        .map(s => s.trim())
        .filter(s => s.length > 0);
      
      if (codes.length === 0) {
        addLog('error', t('technical.enterStockCodes'));
        return;
      }
      customPool = codes;
    }

    setIsScanning(true);
    setScanResults([]);
    setProgress(null);
    addLog('info', t('technical.startingScan'));

    try {
      const requestBody: any = {
        date,
        strategies: selectedStrategies,
        pool_type: poolType
      };
      
      if (poolType === 'custom' && customPool) {
        requestBody.custom_pool = customPool;
      }

      const response = await fetch('http://localhost:8000/api/scan/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody)
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) {
        throw new Error('No reader available');
      }

      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        
        // Process all complete lines
        buffer = lines.pop() || ''; // Keep the last incomplete line in buffer

        for (const line of lines) {
          if (!line.trim()) continue;
          
          try {
            const msg = JSON.parse(line);
            
            if (msg.type === 'meta') {
              addLog('info', msg.message);
              if (msg.total) setProgress({ current: 0, total: msg.total });
            } else if (msg.type === 'progress') {
              setProgress(prev => prev ? { ...prev, current: msg.current } : null);
            } else if (msg.type === 'match') {
              setScanResults(prev => [...prev, msg.data]);
            } else if (msg.type === 'error') {
              addLog('error', `${t('error')}: ${msg.message}`);
            } else if (msg.type === 'done') {
              addLog('success', `${t('technical.scanComplete')} ${scanResults.length + (msg.type === 'match' ? 1 : 0)} ${t('technical.matches')}`);
              setIsScanning(false);
            }
          } catch (e) {
            console.error('Error parsing JSON line:', line, e);
          }
        }
      }
      
    } catch (error: any) {
      addLog('error', `${t('technical.scanFailed')}: ${error.message}`);
      setIsScanning(false);
    } finally {
      setIsScanning(false);
    }
  };

  // Helper to get strategy name
  const getStratName = (key: string) => strategies.find(s => s.key === key)?.name || key;

  return (
    <div className="flex flex-col md:flex-row h-full gap-6">
      {/* Sidebar / Configuration Panel */}
      <div className="w-full md:w-80 flex-shrink-0 bg-white p-4 rounded-lg shadow-sm border border-gray-200 h-fit">
        <div className="flex items-center gap-2 mb-4">
          <Settings className="w-5 h-5 text-blue-600" />
          <h2 className="text-lg font-semibold text-gray-800">{t('technical.config')}</h2>
        </div>

        <div className="space-y-4">
          {/* Date Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">{t('technical.tradingDate')}</label>
            <input 
              type="date" 
              value={date} 
              onChange={(e) => setDate(e.target.value)}
              className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          {/* Pool Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">{t('technical.stockPool')}</label>
            <select 
              value={poolType} 
              onChange={(e) => setPoolType(e.target.value)}
              className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="hs300">{t('technical.hs300')}</option>
              <option value="zz1000">{t('technical.zz1000')}</option>
              <option value="test">{t('technical.test')}</option>
              <option value="custom">{t('technical.custom')}</option>
            </select>
          </div>

          {/* Custom Stock Input */}
          {poolType === 'custom' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">{t('technical.customStocks')}</label>
              <textarea
                value={customStocks}
                onChange={(e) => setCustomStocks(e.target.value)}
                placeholder={t('technical.customStocksPlaceholder')}
                className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 h-24 text-sm font-mono"
              />
              <p className="text-xs text-gray-500 mt-1">{t('technical.customStocksHint')}</p>
            </div>
          )}

          {/* Strategies */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">{t('technical.strategies')}</label>
            <div className="space-y-2 max-h-60 overflow-y-auto border border-gray-100 rounded-md p-2 bg-gray-50">
              {strategies.map((strategy) => (
                <div key={strategy.key} className="flex items-start gap-2">
                  <input
                    type="checkbox"
                    id={strategy.key}
                    checked={selectedStrategies.includes(strategy.key)}
                    onChange={() => toggleStrategy(strategy.key)}
                    className="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <label htmlFor={strategy.key} className="text-sm text-gray-700 cursor-pointer select-none">
                    <span className="font-medium block">{strategy.name}</span>
                    <span className="text-xs text-gray-500">{strategy.description}</span>
                  </label>
                </div>
              ))}
              {strategies.length === 0 && <p className="text-sm text-gray-400">{t('technical.loadingStrategies')}</p>}
            </div>
          </div>

          {/* Action Button */}
          <button
            onClick={handleScan}
            disabled={isScanning}
            className={`w-full py-2 px-4 rounded-md flex items-center justify-center gap-2 text-white font-medium transition-colors ${isScanning ? 'bg-blue-400 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700'}`}
          >
            {isScanning ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" /> {t('technical.scanning')}
              </>
            ) : (
              <>
                <Play className="w-4 h-4" /> {t('technical.startScan')}
              </>
            )}
          </button>
        </div>

        {/* Mini Logs */}
        <div className="mt-6 border-t pt-4">
            <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">{t('technical.activityLog')}</h3>
            <div className="h-32 overflow-y-auto text-xs space-y-1 font-mono bg-gray-900 text-gray-300 p-2 rounded">
                {logs.map((log, i) => (
                    <div key={i} className={`${log.type === 'error' ? 'text-red-400' : log.type === 'success' ? 'text-green-400' : ''}`}>
                        [{log.timestamp}] {log.message}
                    </div>
                ))}
            </div>
        </div>
      </div>

      {/* Main Content / Results */}
      <div className="flex-1 flex flex-col min-w-0">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 flex-1 flex flex-col overflow-hidden">
            {/* Header */}
            <div className="p-4 border-b border-gray-200 flex justify-between items-center bg-gray-50">
                <div>
                    <h2 className="text-lg font-semibold text-gray-800">{t('technical.scanResults')}</h2>
                    <p className="text-sm text-gray-500">
                        {scanResults.length} {t('technical.stocksFound')}
                        {progress && isScanning && ` • ${t('technical.scanned')} ${progress.current}/${progress.total}`}
                    </p>
                </div>
                <div className="flex gap-2">
                    <button className="p-2 text-gray-600 hover:bg-gray-200 rounded-md" title="Filter">
                        <Filter className="w-4 h-4" />
                    </button>
                    <button className="p-2 text-gray-600 hover:bg-gray-200 rounded-md" title="Export">
                        <Download className="w-4 h-4" />
                    </button>
                </div>
            </div>

            {/* Progress Bar */}
            {isScanning && progress && (
                <div className="w-full bg-gray-200 h-1">
                    <div 
                        className="bg-blue-600 h-1 transition-all duration-300"
                        style={{ width: `${Math.min((progress.current / progress.total) * 100, 100)}%` }}
                    />
                </div>
            )}

            {/* Table */}
            <div className="flex-1 overflow-auto p-0">
                {scanResults.length === 0 ? (
                    <div className="h-full flex flex-col items-center justify-center text-gray-400">
                        {isScanning ? (
                            <p>{t('technical.scanningProgress')}</p>
                        ) : (
                            <>
                                <AlertCircle className="w-12 h-12 mb-2 opacity-20" />
                                <p>{t('technical.noResults')}</p>
                            </>
                        )}
                    </div>
                ) : (
                    <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50 sticky top-0">
                            <tr>
                                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{t('technical.code')}</th>
                                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{t('technical.name')}</th>
                                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{t('technical.strategiesMatched')}</th>
                                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{t('technical.details')}</th>
                            </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                            {scanResults.map((result, idx) => (
                                <tr key={`${result.code}-${idx}`} className="hover:bg-gray-50">
                                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{result.code}</td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{result.name}</td>
                                    <td className="px-6 py-4 text-sm text-gray-500">
                                        <div className="flex flex-wrap gap-1">
                                            {/* Assuming result might have a list of matched strategies or we infer it */}
                                            {/* Since the engine result structure might vary, we just display what we can */}
                                            {selectedStrategies.map(stratKey => (
                                                <span key={stratKey} className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800">
                                                    {getStratName(stratKey)}
                                                </span>
                                            ))}
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                        <Link to={`/stock/${result.code}`} className="text-blue-600 hover:text-blue-900">{t('technical.view')}</Link>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}
            </div>
        </div>
      </div>
    </div>
  );
};

export default Technical;