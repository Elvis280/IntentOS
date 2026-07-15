import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Sidebar from './components/Sidebar'
import Overview from './pages/Overview'
import Vision from './pages/Vision'
import History from './pages/History'
import Settings from './pages/Settings'

function App() {
  return (
    <Router>
      <div className="flex h-screen w-full bg-background text-foreground overflow-hidden font-sans">
        <Sidebar />
        <main className="flex-1 flex overflow-hidden relative">
          <Routes>
            <Route path="/" element={<Overview />} />
            <Route path="/vision" element={<Vision />} />
            <Route path="/history" element={<History />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

export default App