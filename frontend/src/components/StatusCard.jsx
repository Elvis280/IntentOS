import { motion } from 'framer-motion'
import useAgentStore from '../store/agentStore'
import {
  Activity, Brain, Eye, CheckCircle2, AlertCircle,
  PlayCircle, PauseCircle, StopCircle, Loader2
} from 'lucide-react'
import { cn } from '../lib/utils'

// Must be declared BEFORE STATUS_CONFIG so the reference is valid
function SpinnerIcon({ size }) {
  return <Loader2 size={size} className="animate-spin" />
}

const STATUS_CONFIG = {
  'idle':      { label: 'Idle',      icon: Activity,     color: 'text-muted-foreground', bg: 'bg-muted/20' },
  'starting':  { label: 'Starting',  icon: SpinnerIcon,  color: 'text-primary',          bg: 'bg-primary/10' },
  'Observing': { label: 'Observing', icon: Eye,          color: 'text-primary',          bg: 'bg-primary/10' },
  'Reasoning': { label: 'Reasoning', icon: Brain,        color: 'text-warning',          bg: 'bg-warning/10' },
  'Policy':    { label: 'Policy',    icon: Activity,     color: 'text-primary',          bg: 'bg-primary/10' },
  'Executing': { label: 'Executing', icon: PlayCircle,   color: 'text-success',          bg: 'bg-success/10' },
  'Verifying': { label: 'Verifying', icon: Activity,     color: 'text-primary',          bg: 'bg-primary/10' },
  'Completed': { label: 'Completed', icon: CheckCircle2, color: 'text-success',          bg: 'bg-success/10' },
  'completed': { label: 'Completed', icon: CheckCircle2, color: 'text-success',          bg: 'bg-success/10' },
  'running':   { label: 'Running',   icon: PlayCircle,   color: 'text-success',          bg: 'bg-success/10' },
  'paused':    { label: 'Paused',    icon: PauseCircle,  color: 'text-warning',          bg: 'bg-warning/10' },
  'stopped':   { label: 'Stopped',   icon: StopCircle,   color: 'text-muted-foreground', bg: 'bg-muted/20' },
  'failed':    { label: 'Failed',    icon: AlertCircle,  color: 'text-danger',           bg: 'bg-danger/10' },
}

const ACTIVE_STAGES = new Set([
  'Observing', 'Reasoning', 'Policy', 'Executing', 'Verifying', 'running', 'starting'
])

const getShadow = (status, stage) => {
  const key = status === 'running' || status === 'starting' ? (stage || status) : status
  if (key === 'Reasoning')                          return 'shadow-[0_0_20px_rgba(245,158,11,0.15)] border-warning/30'
  if (['Executing', 'completed', 'Completed', 'running'].includes(key))
                                                    return 'shadow-[0_0_20px_rgba(34,197,94,0.15)] border-success/30'
  if (['failed'].includes(key))                     return 'shadow-[0_0_20px_rgba(239,68,68,0.15)] border-danger/30'
  if (ACTIVE_STAGES.has(key))                       return 'shadow-[0_0_20px_rgba(59,130,246,0.15)] border-primary/30'
  return ''
}

export default function StatusCard() {
  const { status, stage } = useAgentStore()

  const isRunning  = status === 'running' || status === 'starting'
  const displayKey = isRunning ? (stage || status) : status
  const config     = STATUS_CONFIG[displayKey] ?? STATUS_CONFIG['idle']
  const Icon       = config.icon
  const isPulsing  = ACTIVE_STAGES.has(displayKey)

  return (
    <div className={cn(
      'flex items-center justify-between bg-card rounded-xl border border-border p-4 transition-all duration-700',
      getShadow(status, stage)
    )}>
      <div>
        <p className="text-sm font-medium text-muted-foreground mb-1">Current Status</p>
        <div className="flex items-center gap-3">
          <motion.div
            key={displayKey}
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: 0.2 }}
            className={cn('p-2 rounded-lg', config.bg)}
          >
            <Icon size={22} className={config.color} />
          </motion.div>

          <motion.h2
            key={`${displayKey}-text`}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.2 }}
            className="text-2xl font-bold"
          >
            {config.label}
          </motion.h2>
        </div>
      </div>

      {isPulsing && (
        <span className="relative flex h-4 w-4 mr-2 flex-shrink-0">
          <span className={cn(
            'animate-ping absolute inline-flex h-full w-full rounded-full opacity-60',
            config.bg
          )} />
          <span className={cn(
            'relative inline-flex rounded-full h-4 w-4',
            config.bg
          )} />
        </span>
      )}
    </div>
  )
}
