import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import Dashboard from './pages/Dashboard'
import LeadDetail from './pages/LeadDetail'
import './index.css'

const qc = new QueryClient()

export default function App() {
  return (
    <QueryClientProvider client={qc}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/leads/:id" element={<LeadDetail />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  )
}
