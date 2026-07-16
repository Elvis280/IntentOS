import { Routes, Route, useLocation } from 'react-router-dom'
import { Sidebar } from '../layouts/Sidebar'
import { RuntimePage } from '../features/runtime/RuntimePage'
import { OverlayPage } from '../features/overlay/OverlayPage'
import { DashboardPage } from '../features/dashboard/DashboardPage'
import { SessionsPage } from '../features/sessions/SessionsPage'
import { SettingsPage } from '../features/settings/SettingsPage'

function MainLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex h-screen w-screen overflow-hidden bg-[#080909] text-zinc-100 font-sans antialiased">
      <Sidebar />
      <main className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {children}
      </main>
    </div>
  )
}

export function App() {
  const location = useLocation()
  const isOverlay = location.pathname === '/overlay'

  if (isOverlay) {
    return (
      <div className="h-screen w-screen overflow-hidden text-zinc-100 font-sans antialiased bg-transparent">
        <Routes>
          <Route path="/overlay" element={<OverlayPage />} />
        </Routes>
      </div>
    )
  }

  return (
    <MainLayout>
      <Routes>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/runtime" element={<RuntimePage />} />
        <Route path="/sessions" element={<SessionsPage />} />
        <Route path="/settings" element={<SettingsPage />} />
      </Routes>
    </MainLayout>
  )
}
