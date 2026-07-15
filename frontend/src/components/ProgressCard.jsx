import useAgentStore from '../store/agentStore'
import { motion } from 'framer-motion'
import { Clock } from 'lucide-react'

export default function ProgressCard() {
  const { step, maxSteps, progress, status } = useAgentStore()
  const percentage = Math.round(progress * 100)

  // Elapsed time — simple display from step count (real timer would need backend support)
  const elapsed = step > 0 ? `${(step * 1.5).toFixed(0)}s est.` : '—'

  return (
    <div className="bg-card rounded-xl border border-border p-5 shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <div className="flex flex-col">
          <span className="text-sm font-medium text-muted-foreground">Execution Progress</span>
          <span className="text-2xl font-bold">
            {step > 0 ? `Step ${step} of ${maxSteps}` : 'Not started'}
          </span>
        </div>
        <div className="flex items-center gap-2 text-muted-foreground bg-surface px-3 py-1.5 rounded-lg border border-border">
          <Clock size={16} />
          <span className="text-sm font-mono">{elapsed}</span>
        </div>
      </div>

      <div className="relative h-2 w-full bg-surface rounded-full overflow-hidden border border-border/50">
        <motion.div
          className="absolute top-0 left-0 h-full bg-primary"
          initial={{ width: 0 }}
          animate={{ width: `${percentage}%` }}
          transition={{ duration: 0.4, ease: 'easeInOut' }}
        />
        {/* Shimmer on active states */}
        {(status === 'running' || status === 'starting') && percentage > 0 && (
          <motion.div
            className="absolute top-0 h-full w-8 bg-gradient-to-r from-transparent via-white/20 to-transparent"
            animate={{ left: ['-10%', '110%'] }}
            transition={{ duration: 1.5, repeat: Infinity, ease: 'linear' }}
          />
        )}
      </div>

      <div className="mt-2 text-right text-xs text-muted-foreground font-mono">
        {percentage}%
      </div>
    </div>
  )
}
