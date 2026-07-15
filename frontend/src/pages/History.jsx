import { History as HistoryIcon, Play } from 'lucide-react'
import { motion } from 'framer-motion'

export default function History() {
  const dummyRuns = [
    { id: 'run-1', goal: 'Open YouTube', status: 'Completed', time: '10:45 AM', steps: 8 },
    { id: 'run-2', goal: 'Search for React Router', status: 'Completed', time: '09:20 AM', steps: 12 },
    { id: 'run-3', goal: 'Download VS Code', status: 'Error', time: 'Yesterday', steps: 15 },
  ]

  return (
    <div className="p-8 flex-1 overflow-y-auto custom-scrollbar">
      <div className="flex items-center gap-3 mb-8">
        <div className="bg-primary/10 p-3 rounded-xl border border-primary/20">
          <HistoryIcon className="text-primary" size={24} />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-foreground">Execution History</h1>
          <p className="text-muted-foreground">Review previous agent runs and outcomes.</p>
        </div>
      </div>

      <div className="space-y-4">
        {dummyRuns.map(run => (
          <motion.div 
            key={run.id} 
            whileHover={{ scale: 1.01, y: -2 }}
            whileTap={{ scale: 0.99 }}
            className="bg-card rounded-xl border border-border p-5 flex items-center justify-between hover:border-primary/50 hover:shadow-[0_4px_20px_rgba(59,130,246,0.1)] transition-all cursor-pointer group"
          >
            <div className="flex items-center gap-4">
              <div className="bg-surface h-10 w-10 rounded-full flex items-center justify-center border border-border group-hover:bg-primary/10 transition-colors">
                <Play size={16} className="text-muted-foreground group-hover:text-primary transition-colors" />
              </div>
              <div>
                <h3 className="text-foreground font-medium text-lg">{run.goal}</h3>
                <p className="text-muted-foreground text-sm">{run.time} • {run.steps} steps</p>
              </div>
            </div>
            
            <div className="flex items-center gap-4">
              <span className={`px-3 py-1 rounded-full text-xs font-semibold border ${
                run.status === 'Completed' ? 'bg-success/10 text-success border-success/30' : 'bg-danger/10 text-danger border-danger/30'
              }`}>
                {run.status}
              </span>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  )
}
