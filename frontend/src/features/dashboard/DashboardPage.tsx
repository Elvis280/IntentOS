import { useNavigate } from 'react-router-dom'
import { useState } from 'react'
import { motion } from 'framer-motion'
import {
  Activity, ChevronRight, Circle, CheckCircle2,
  XCircle, Clock, Archive, Zap,
} from 'lucide-react'
import { useRuntimeStore } from '../../store/runtimeStore'
import { agentApi } from '../../services/agentApi'
import type { PlanStep } from '../../types/agent'

const STEP_STATUS_STYLES: Record<string, string> = {
  Active:    'text-sky-400 bg-sky-950/60 border-sky-600/30',
  Completed: 'text-emerald-400 bg-emerald-950/50 border-emerald-700/30',
  Failed:    'text-red-400 bg-red-950/50 border-red-700/30',
  Pending:   'text-zinc-500 bg-zinc-900/60 border-zinc-700/30',
  Skipped:   'text-zinc-600 bg-zinc-900/40 border-zinc-700/20',
  Waiting:   'text-amber-400 bg-amber-950/50 border-amber-700/30',
}

const STEP_STATUS_ICON = (status: string) => {
  if (status === 'Completed') return <CheckCircle2 size={12} />
  if (status === 'Failed') return <XCircle size={12} />
  if (status === 'Active') return <Activity size={12} />
  return <Circle size={12} />
}

function PlanStepCard({ step, index }: { step: PlanStep; index: number }) {
  const style = STEP_STATUS_STYLES[step.status] ?? STEP_STATUS_STYLES.Pending
  return (
    <motion.div
      initial={{ opacity: 0, x: -8 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.04 }}
      className={`flex items-start gap-3 px-3 py-2.5 rounded-lg border ${style} mb-1.5`}
    >
      <span className="mt-0.5 flex-shrink-0">{STEP_STATUS_ICON(step.status)}</span>
      <div className="min-w-0">
        <p className="text-xs font-medium truncate">{step.title}</p>
        <p className="text-[10px] text-zinc-500 truncate mt-0.5">{step.description}</p>
      </div>
      <span className="ml-auto text-[10px] font-medium flex-shrink-0 opacity-70 mt-0.5">{step.status}</span>
    </motion.div>
  )
}

export function DashboardPage() {
  const navigate = useNavigate()
  const { job, goal, setGoal, setJobId, setPolling, reset, setLoading } = useRuntimeStore()
  const [quickGoal, setQuickGoal] = useState('')

  const handleQuickLaunch = async () => {
    const g = quickGoal.trim()
    if (!g) return
    reset()
    setGoal(g)
    setLoading(true)
    try {
      const { job_id } = await agentApi.start(g)
      setJobId(job_id)
      setPolling(true)
      navigate('/runtime')
    } catch {
      // error handled in Runtime store
    } finally {
      setLoading(false)
    }
  }

  const steps: PlanStep[] = job?.plan?.steps ?? []
  const progress = job?.plan_progress
  const pct = progress ? Math.round(progress.percentage_complete * 100) : 0

  return (
    <div className="flex flex-col h-full p-4 gap-4 overflow-y-auto">
      <h1 className="text-sm font-semibold text-zinc-200 tracking-wide">Mission Control</h1>

      {/* Quick Launch */}
      <div className="flex gap-2">
        <input
          id="dashboard-goal-input"
          value={quickGoal}
          onChange={e => setQuickGoal(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && void handleQuickLaunch()}
          placeholder="What should IntentOS do?"
          className="flex-1 bg-[#0d0e10] border border-white/[0.08] rounded-lg px-3 py-2 text-sm text-zinc-200 placeholder-zinc-600 focus:outline-none focus:border-sky-500/50 transition-colors"
        />
        <button
          id="dashboard-launch-btn"
          onClick={() => void handleQuickLaunch()}
          className="px-4 py-2 rounded-lg bg-sky-600 hover:bg-sky-500 text-white text-sm font-medium transition-colors flex items-center gap-1.5"
        >
          <Zap size={14} /> Run
        </button>
      </div>

      <div className="grid grid-cols-2 gap-4 flex-1 min-h-0">
        {/* Active Job Card */}
        <div className="flex flex-col bg-[#0d0e10] rounded-xl border border-white/[0.06] overflow-hidden">
          <div className="flex items-center gap-2 px-4 py-3 border-b border-white/[0.06]">
            <Activity size={13} className="text-sky-400" />
            <span className="text-xs font-medium text-zinc-400 tracking-wider uppercase">Active Job</span>
            {job && (
              <button
                id="dashboard-open-runtime-btn"
                onClick={() => navigate('/runtime')}
                className="ml-auto flex items-center gap-1 text-[10px] text-zinc-500 hover:text-zinc-300 transition-colors"
              >
                Open <ChevronRight size={11} />
              </button>
            )}
          </div>
          <div className="flex-1 p-4">
            {!job ? (
              <div className="flex flex-col items-center justify-center h-full text-center gap-2 py-8">
                <Circle size={20} className="text-zinc-700" />
                <p className="text-xs text-zinc-600">No active job. Launch one above.</p>
              </div>
            ) : (
              <div className="space-y-3">
                <div>
                  <p className="text-[10px] text-zinc-600 uppercase tracking-widest mb-1">Goal</p>
                  <p className="text-xs text-zinc-200 leading-relaxed">{goal || job.goal}</p>
                </div>
                <div>
                  <p className="text-[10px] text-zinc-600 uppercase tracking-widest mb-1">Stage</p>
                  <p className="text-xs text-sky-400 font-medium">{job.stage || '—'}</p>
                </div>
                {job.thought && (
                  <div>
                    <p className="text-[10px] text-zinc-600 uppercase tracking-widest mb-1">Thought</p>
                    <p className="text-xs text-zinc-400 italic leading-relaxed">{job.thought}</p>
                  </div>
                )}
                <div>
                  <p className="text-[10px] text-zinc-600 uppercase tracking-widest mb-1">Progress</p>
                  <div className="flex items-center gap-2">
                    <div className="flex-1 h-1 bg-white/[0.06] rounded-full">
                      <div className="h-full bg-sky-500 rounded-full transition-all" style={{ width: `${pct}%` }} />
                    </div>
                    <span className="text-[10px] text-zinc-500 tabular-nums">{job.step}/{job.max_steps}</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Plan Viewer */}
        <div className="flex flex-col bg-[#0d0e10] rounded-xl border border-white/[0.06] overflow-hidden">
          <div className="flex items-center gap-2 px-4 py-3 border-b border-white/[0.06]">
            <Clock size={13} className="text-zinc-400" />
            <span className="text-xs font-medium text-zinc-400 tracking-wider uppercase">Execution Plan</span>
            {progress && (
              <span className="ml-auto text-[10px] text-zinc-500">
                {progress.completed_steps}/{progress.total_steps} done
              </span>
            )}
          </div>
          <div className="flex-1 overflow-y-auto p-3">
            {steps.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full text-center gap-2 py-8">
                <Clock size={20} className="text-zinc-700" />
                <p className="text-xs text-zinc-600">No plan yet. Start a job to generate one.</p>
              </div>
            ) : (
              steps.map((step, i) => <PlanStepCard key={step.id} step={step} index={i} />)
            )}
          </div>
        </div>
      </div>

      {/* Footer: Recent Sessions shortcut */}
      <button
        id="dashboard-sessions-btn"
        onClick={() => navigate('/sessions')}
        className="flex items-center gap-2 text-xs text-zinc-600 hover:text-zinc-300 transition-colors"
      >
        <Archive size={12} /> View session history
      </button>
    </div>
  )
}
