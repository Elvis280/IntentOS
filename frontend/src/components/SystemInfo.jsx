import useAgentStore from '../store/agentStore'
import { Cpu, Database, Network, BrainCircuit } from 'lucide-react'

export default function SystemInfo() {
  const { systemInfo } = useAgentStore()

  // Parse CPU percentage for the ring (e.g. "14%" -> 14)
  const cpuPercent = parseInt(systemInfo.cpu.replace('%', '')) || 0
  const memPercent = 60 // Mocked for visuals

  const metrics = [
    { label: 'CPU', value: systemInfo.cpu, icon: Cpu, percent: cpuPercent },
    { label: 'RAM', value: systemInfo.memory, icon: Database, percent: memPercent },
    { label: 'Latency', value: systemInfo.latency, icon: Network, percent: null },
    { label: 'Model', value: systemInfo.model, icon: BrainCircuit, percent: null },
  ]

  const ProgressRing = ({ percentage }) => {
    const radius = 12
    const circumference = 2 * Math.PI * radius
    const strokeDashoffset = circumference - (percentage / 100) * circumference
    
    return (
      <svg className="w-8 h-8 -rotate-90">
        <circle cx="16" cy="16" r={radius} stroke="currentColor" strokeWidth="3" fill="transparent" className="text-surface border-border" />
        <circle 
          cx="16" cy="16" r={radius} 
          stroke="currentColor" strokeWidth="3" fill="transparent" 
          strokeDasharray={circumference} 
          strokeDashoffset={strokeDashoffset}
          className="text-primary transition-all duration-1000 ease-in-out" 
        />
      </svg>
    )
  }

  return (
    <div className="bg-card rounded-xl border border-border shadow-sm p-4">
      <h3 className="font-medium text-foreground mb-3 text-sm">System Information</h3>
      <div className="grid grid-cols-2 gap-3">
        {metrics.map((metric) => {
          const Icon = metric.icon
          return (
            <div key={metric.label} className="bg-surface border border-border rounded-lg p-3 flex items-center justify-between gap-2">
              <div className="flex flex-col gap-1">
                <span className="text-muted-foreground text-[10px] flex items-center gap-1.5 font-bold uppercase tracking-wider">
                  <Icon size={12} className="text-primary" />
                  {metric.label}
                </span>
                <span className="text-foreground font-mono text-sm">
                  {metric.value}
                </span>
              </div>
              {metric.percent !== null && (
                <div className="flex-shrink-0">
                  <ProgressRing percentage={metric.percent} />
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
