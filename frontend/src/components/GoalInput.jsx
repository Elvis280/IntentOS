import { Play, Square, Pause, RotateCcw, Trash2, Loader2 } from 'lucide-react'
import { useState } from 'react'
import { motion } from 'framer-motion'
import { cn } from '../lib/utils'
import useAgentStore from '../store/agentStore'

const ACTIVE = new Set(['running', 'starting', 'paused'])
const TERMINAL = new Set(['completed', 'failed', 'stopped', 'idle'])

export default function GoalInput() {
  const [goal, setGoal] = useState('')
  const [isFocused, setIsFocused] = useState(false)

  const { status, run, pause, resume, stop, reset } = useAgentStore()

  const isActive   = ACTIVE.has(status)
  const isRunning  = status === 'running' || status === 'starting'
  const isPaused   = status === 'paused'
  const isFinished = TERMINAL.has(status) && status !== 'idle'

  const handleRun = () => {
    if (goal.trim()) run(goal.trim())
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey) && !isActive) {
      handleRun()
    }
  }

  return (
    <div className={cn(
      "bg-card rounded-xl border overflow-hidden shadow-sm transition-all duration-300",
      isFocused && !isActive ? "border-primary shadow-[0_0_15px_rgba(59,130,246,0.15)]" : "border-border"
    )}>
      <textarea
        value={goal}
        onChange={(e) => setGoal(e.target.value)}
        onFocus={() => setIsFocused(true)}
        onBlur={() => setIsFocused(false)}
        onKeyDown={handleKeyDown}
        disabled={isActive}
        placeholder={isActive ? 'Agent is running...' : 'What would you like IntentOS to do?'}
        className={cn(
          "w-full h-24 p-4 bg-transparent resize-none focus:outline-none placeholder:text-muted-foreground text-sm leading-relaxed",
          isActive ? "text-muted-foreground cursor-not-allowed" : "text-foreground"
        )}
      />

      <div className="flex items-center justify-between p-3 bg-surface/50 border-t border-border">
        <div className="flex items-center gap-1">
          {/* Clear / Reset */}
          {(isFinished) && (
            <motion.button
              whileTap={{ scale: 0.95 }}
              onClick={reset}
              className="text-muted-foreground hover:text-foreground p-2 rounded-lg transition-colors flex items-center gap-2 text-sm"
            >
              <RotateCcw size={14} />
              New task
            </motion.button>
          )}
          {!isActive && !isFinished && (
            <button
              onClick={() => setGoal('')}
              className="text-muted-foreground hover:text-foreground p-2 rounded-lg transition-colors flex items-center gap-2 text-sm"
            >
              <Trash2 size={14} />
              Clear
            </button>
          )}
        </div>

        <div className="flex items-center gap-2">
          {/* Pause */}
          {isRunning && (
            <motion.button
              whileTap={{ scale: 0.95 }}
              onClick={pause}
              className="bg-warning/10 hover:bg-warning/20 text-warning border border-warning/30 px-4 py-2 rounded-lg font-medium text-sm flex items-center gap-2 transition-colors"
            >
              <Pause size={14} className="fill-current" />
              Pause
            </motion.button>
          )}

          {/* Resume */}
          {isPaused && (
            <motion.button
              whileTap={{ scale: 0.95 }}
              onClick={resume}
              className="bg-primary/10 hover:bg-primary/20 text-primary border border-primary/30 px-4 py-2 rounded-lg font-medium text-sm flex items-center gap-2 transition-colors"
            >
              <Play size={14} className="fill-current" />
              Resume
            </motion.button>
          )}

          {/* Stop */}
          {isActive && (
            <motion.button
              whileTap={{ scale: 0.95 }}
              onClick={stop}
              className="bg-danger/10 hover:bg-danger/20 text-danger border border-danger/30 px-4 py-2 rounded-lg font-medium text-sm flex items-center gap-2 transition-colors"
            >
              <Square size={14} className="fill-current" />
              Stop
            </motion.button>
          )}

          {/* Run */}
          {!isActive && (
            <motion.button
              whileTap={{ scale: 0.95 }}
              onClick={handleRun}
              disabled={!goal.trim()}
              className={cn(
                "px-4 py-2 rounded-lg font-medium text-sm flex items-center gap-2 shadow-sm transition-colors",
                goal.trim()
                  ? "bg-primary hover:bg-primary/90 text-primary-foreground"
                  : "bg-muted text-muted-foreground cursor-not-allowed"
              )}
            >
              {status === 'starting' ? (
                <><Loader2 size={14} className="animate-spin" /> Starting...</>
              ) : (
                <><Play size={14} className="fill-current" /> Run Agent</>
              )}
            </motion.button>
          )}
        </div>
      </div>
    </div>
  )
}
