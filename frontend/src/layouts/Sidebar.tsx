import { NavLink } from 'react-router-dom'
import { LayoutDashboard, Radio, Archive, Settings } from 'lucide-react'

const NAV = [
  { to: '/', icon: <LayoutDashboard size={16} />, label: 'Dashboard', id: 'nav-dashboard' },
  { to: '/runtime', icon: <Radio size={16} />, label: 'Runtime', id: 'nav-runtime' },
  { to: '/sessions', icon: <Archive size={16} />, label: 'Sessions', id: 'nav-sessions' },
  { to: '/settings', icon: <Settings size={16} />, label: 'Settings', id: 'nav-settings' },
]

export function Sidebar() {
  return (
    <aside className="w-14 flex-shrink-0 flex flex-col items-center py-4 gap-1 bg-[#0a0b0c] border-r border-white/[0.06]">
      {/* Logo mark */}
      <div className="w-7 h-7 rounded-lg bg-sky-600 flex items-center justify-center mb-4">
        <span className="text-white text-xs font-bold leading-none">I</span>
      </div>

      {NAV.map(({ to, icon, label, id }) => (
        <NavLink
          key={to}
          id={id}
          to={to}
          end={to === '/'}
          title={label}
          className={({ isActive }) =>
            `w-9 h-9 flex items-center justify-center rounded-lg transition-all ${
              isActive
                ? 'bg-sky-600/20 text-sky-400 border border-sky-500/30'
                : 'text-zinc-600 hover:text-zinc-300 hover:bg-white/[0.05]'
            }`
          }
        >
          {icon}
        </NavLink>
      ))}
    </aside>
  )
}
