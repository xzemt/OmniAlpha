import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Layout from './components/layout/Layout';
import Home from './pages/Home';
import Technical from './pages/Technical';
import Alpha from './pages/Alpha';
import AI from './pages/AI';
import StockDetail from './pages/StockDetail';
import NotFound from './pages/NotFound';
import Settings from './pages/Settings';
import { LanguageProvider } from './contexts/LanguageContext';

const App: React.FC = () => {
  return (
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
  );
};

export default App;
