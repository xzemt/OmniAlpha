import React, { useEffect, useState } from 'react';
import { Routes, Route } from 'react-router-dom';
import Layout from './components/layout/Layout';
import ErrorBoundary from './components/ErrorBoundary';
import Home from './pages/Home';
import Technical from './pages/Technical';
import Alpha from './pages/Alpha';
import AI from './pages/AI';
import StockDetail from './pages/StockDetail';
import NotFound from './pages/NotFound';
import Settings from './pages/Settings';
import { LanguageProvider } from './contexts/LanguageContext';
import { apiUtils } from './api/client';

/**
 * 加载状态屏幕 - 用于初始化检查
 */
const LoadingScreen: React.FC = () => (
  <div className="flex items-center justify-center min-h-screen bg-gray-50">
    <div className="text-center">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
      <p className="text-gray-600">正在初始化应用...</p>
    </div>
  </div>
);

const App: React.FC = () => {
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    /**
     * 初始化应用 - 检查 API 可用性
     */
    const initializeApp = async () => {
      try {
        const available = await apiUtils.healthCheck();

        if (!available) {
          console.warn('[App] API not available, using offline mode');
        } else {
          console.info('[App] API is available');
        }
      } catch (error) {
        console.warn('[App] Failed to check API health:', error);
      } finally {
        setIsLoading(false);
      }
    };

    initializeApp();
  }, []);

  if (isLoading) {
    return <LoadingScreen />;
  }

  return (
    <ErrorBoundary>
      <LanguageProvider>
        <Layout>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/technical" element={<Technical />} />
            <Route path="/alpha" element={<Alpha />} />
            <Route path="/ai" element={<AI />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="/stock/:code" element={<StockDetail />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </Layout>
      </LanguageProvider>
    </ErrorBoundary>
  );
};

export default App;
