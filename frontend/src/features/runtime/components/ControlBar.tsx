import { Play, Pause, Square, RotateCcw } from 'lucide-react'
import type { JobStatus } from '../../../types/agent'

interface ControlBarProps {
  status: JobStatus | null
  isLoading: boolean
  goal: string
  onGoalChange: (value: string) => void
  onStart: () => void
  onPause: () => void
  onResume: () => void
  onStop: () => void
}

interface Btn {
  id: string
  label: string
  icon: React.ReactNode
  onClick: () => void
  variant: 'primary' | 'amber' | 'red' | 'ghost'
  disabled?: boolean
}

const VARIANT_STYLES: Record<Btn['variant'], string> = {
  primary:
    'bg-sky-600 hover:bg-sky-500 text-white border border-sky-500/40',
  amber:
    'bg-amber-900/60 hover:bg-amber-800/70 text-amber-300 border border-amber-500/30',
  red:
    'bg-red-950/60 hover:bg-red-900/70 text-red-400 border border-red-500/30',
  ghost:
    'bg-white/[0.03] hover:bg-white/[0.07] text-zinc-400 border border-white/[0.08]',
}

export function ControlBar({
  status,
  isLoading,
  goal,
  onGoalChange,
  onStart,
  onPause,
  onResume,
  onStop,
}: ControlBarProps) {
  const isRunning = status === 'running'
  const isPaused = status === 'paused'
  const isTerminal = status === 'completed' || status === 'failed' || status === 'stopped'
  const isIdle = status === null || isTerminal

  const buttons: Btn[] = [
    ...(isIdle
      ? [
          {
            id: 'start-btn',
            label: isTerminal ? 'Restart' : 'Start',
            icon: isTerminal ? <RotateCcw size={14} /> : <Play size={14} />,
            onClick: onStart,
            variant: 'primary' as const,
            disabled: !goal.trim() || isLoading,
          },
        ]
      : []),
    ...(isRunning
      ? [
          {
            id: 'pause-btn',
            label: 'Pause',
            icon: <Pause size={14} />,
            onClick: onPause,
            variant: 'amber' as const,
          },
        ]
      : []),
    ...(isPaused
      ? [
          {
            id: 'resume-btn',
            label: 'Resume',
            icon: <Play size={14} />,
            onClick: onResume,
            variant: 'primary' as const,
          },
        ]
      : []),
    ...(!isIdle && !isTerminal
      ? [
          {
            id: 'stop-btn',
            label: 'Stop',
            icon: <Square size={14} />,
            onClick: onStop,
            variant: 'red' as const,
          },
        ]
      : []),
  ]

  return (
    <div className="flex items-center gap-2 px-4 py-3 border-t border-white/[0.06] bg-[#0a0b0c]">
      {/* Goal input */}
      <input
        id="goal-input"
        type="text"
        value={goal}
        onChange={(e) => onGoalChange(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === 'Enter' && isIdle && goal.trim()) onStart()
        }}
        placeholder="What would you like IntentOS to do?"
        disabled={isRunning || isPaused}
        className="flex-1 bg-white/[0.03] border border-white/[0.08] rounded-md px-3 py-1.5 text-sm text-zinc-200 placeholder-zinc-600 outline-none focus:border-sky-500/50 focus:bg-sky-950/10 transition disabled:opacity-40 disabled:cursor-not-allowed"
      />

      {/* Control buttons */}
      {buttons.map((btn) => (
        <button
          key={btn.id}
          id={btn.id}
          onClick={btn.onClick}
          disabled={btn.disabled || isLoading}
          title={btn.label}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition disabled:opacity-40 disabled:cursor-not-allowed ${VARIANT_STYLES[btn.variant]}`}
        >
          {btn.icon}
          <span className="hidden sm:inline">{btn.label}</span>
        </button>
      ))}
    </div>
  )
}
