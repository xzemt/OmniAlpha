import { Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/layout/Layout'
import Home from './pages/Home'
import Technical from './pages/Technical'
import Alpha from './pages/Alpha'
import AI from './pages/AI'
import StockDetail from './pages/StockDetail'
import NotFound from './pages/NotFound'

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/technical" element={<Technical />} />
        <Route path="/alpha" element={<Alpha />} />
        <Route path="/ai" element={<AI />} />
        <Route path="/stock/:code" element={<StockDetail />} />
        <Route path="/404" element={<NotFound />} />
        <Route path="*" element={<Navigate to="/404" replace />} />
      </Routes>
    </Layout>
  )
}

export default App
