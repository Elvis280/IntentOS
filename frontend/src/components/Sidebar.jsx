import { LayoutDashboard, Eye, History, Settings, Activity, BrainCircuit, Cpu } from 'lucide-react'
import { Link, useLocation } from 'react-router-dom'
import useAgentStore from '../store/agentStore'
import { motion } from 'framer-motion'
import { cn } from '../lib/utils'

export default function Sidebar() {
  const location = useLocation()
  const { systemInfo } = useAgentStore()

  const links = [
    { name: 'Overview', path: '/', icon: LayoutDashboard },
    { name: 'Vision', path: '/vision', icon: Eye },
    { name: 'History', path: '/history', icon: History },
    { name: 'Settings', path: '/settings', icon: Settings },
  ]

  return (
    <aside className="w-64 bg-surface border-r border-border h-screen flex flex-col justify-between">
      {/* Logo & Navigation */}
      <div>
        <div className="flex items-center gap-3 p-6">
          <div className="bg-primary p-2 rounded-lg">
            <BrainCircuit className="text-primary-foreground" size={24} />
          </div>
          <h1 className="text-xl font-bold tracking-wide">IntentOS</h1>
        </div>

        <nav className="px-4 mt-2 space-y-1">
          {links.map((link) => {
            const isActive = location.pathname === link.path
            const Icon = link.icon
            return (
              <Link
                key={link.name}
                to={link.path}
                className={cn(
                  "flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-colors relative",
                  isActive ? "text-foreground bg-card" : "text-muted-foreground hover:bg-card/50 hover:text-foreground"
                )}
              >
                {isActive && (
                  <motion.div
                    layoutId="active-nav"
                    className="absolute inset-0 bg-card rounded-lg -z-10"
                    transition={{ type: "spring", stiffness: 300, damping: 30 }}
                  />
                )}
                <Icon size={18} />
                {link.name}
              </Link>
            )
          })}
        </nav>
      </div>

      {/* System Status Footer */}
      <div className="p-6 border-t border-border">
        <div className="space-y-4">
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground flex items-center gap-2">
              <Activity size={14} /> Backend
            </span>
            <span className="flex items-center gap-2 text-success">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-success opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-success"></span>
              </span>
              Connected
            </span>
          </div>
          
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground flex items-center gap-2">
              <BrainCircuit size={14} /> Model
            </span>
            <span className="font-medium">{systemInfo.model}</span>
          </div>

          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground flex items-center gap-2">
              <Cpu size={14} /> Memory
            </span>
            <span className="font-medium">{systemInfo.memory}</span>
          </div>
        </div>
      </div>
    </aside>
  )
}
