import {
  Brain, Zap, Eye, CheckCircle, XCircle, PauseCircle,
  Clock, Target, ChevronRight, Activity, List, RefreshCw,
  AlertTriangle, MonitorCheck,
} from 'lucide-react'
import type { JobState, JobStatus, HistoryEntry } from '../../../types/agent'

interface RuntimeStatePanelProps {
  job: JobState | null
  goal: string
}

const STAGE_ICONS: Record<string, React.ReactNode> = {
  Observing:    <Eye size={13} />,
  Reasoning:    <Brain size={13} />,
  'Applying Policy': <Zap size={13} />,
  Executing:    <Zap size={13} />,
  Verifying:    <CheckCircle size={13} />,
  Reflecting:   <Activity size={13} />,
  Recovering:   <RefreshCw size={13} />,
  Replanning:   <List size={13} />,
  Planning:     <List size={13} />,
  Completed:    <CheckCircle size={13} />,
  'Completed Step': <CheckCircle size={13} />,
  Failed:       <XCircle size={13} />,
  Paused:       <PauseCircle size={13} />,
  'Awaiting User Clarification': <AlertTriangle size={13} />,
}

const STATUS_COLORS: Record<JobStatus, string> = {
  created:   'text-zinc-400 bg-zinc-800/60',
  running:   'text-sky-400 bg-sky-950/60',
  paused:    'text-amber-400 bg-amber-950/60',
  completed: 'text-emerald-400 bg-emerald-950/60',
  failed:    'text-red-400 bg-red-950/60',
  stopped:   'text-zinc-400 bg-zinc-800/60',
}

const STEP_STATUS_DOT: Record<string, string> = {
  Active:    'bg-sky-400',
  Completed: 'bg-emerald-400',
  Failed:    'bg-red-400',
  Pending:   'bg-zinc-700',
  Skipped:   'bg-zinc-800',
  Waiting:   'bg-amber-400',
}

function SectionLabel({ label }: { label: string }) {
  return <p className="text-[10px] font-semibold tracking-widest uppercase text-zinc-600 mb-1">{label}</p>
}

function getLastEntry(history: HistoryEntry[]): HistoryEntry | undefined {
  return history[history.length - 1]
}

export function RuntimeStatePanel({ job, goal }: RuntimeStatePanelProps) {
  const noJob = !job
  const lastEntry = job ? getLastEntry(job.history) : undefined
  const lastVerification = lastEntry && typeof lastEntry.verified === 'object' ? lastEntry.verified : null
  const lastReflection = lastEntry?.reflection ?? null
  const lastRecovery = lastEntry?.recovery ?? null
  const steps = job?.plan?.steps ?? []
  const progress = job?.plan_progress

  return (
    <div className="flex flex-col h-full bg-[#0d0e10] rounded-lg border border-white/[0.06] overflow-hidden">
      {/* Header */}
      <div className="flex items-center gap-2 px-4 py-2.5 border-b border-white/[0.06]">
        <Brain size={13} className="text-zinc-500" />
        <span className="text-xs font-medium text-zinc-500 tracking-wider uppercase">Inspector</span>
        {job && (
          <span className={`ml-auto text-[10px] font-medium px-2 py-0.5 rounded-full ${STATUS_COLORS[job.status]}`}>
            {job.status}
          </span>
        )}
      </div>

      {/* Body */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {noJob ? (
          <div className="flex flex-col items-center justify-center h-full gap-3 text-center py-12">
            <Target size={24} className="text-zinc-700" />
            <p className="text-xs text-zinc-600">Submit a goal to start the runtime.</p>
          </div>
        ) : (
          <>
            {/* Stage */}
            <div>
              <SectionLabel label="Stage" />
              <div className="flex items-center gap-1.5 text-xs text-zinc-200 font-medium">
                <span className="text-zinc-500">{STAGE_ICONS[job.stage] ?? <Clock size={13} />}</span>
                {job.stage || '—'}
              </div>
            </div>

            {/* Progress */}
            <div>
              <SectionLabel label="Progress" />
              <div className="flex items-center gap-2">
                <div className="flex-1 h-1 bg-white/[0.06] rounded-full overflow-hidden">
                  <div
                    className="h-full bg-sky-500 rounded-full transition-all duration-300"
                    style={{ width: `${Math.round(((job.step ?? 0) / (job.max_steps ?? 20)) * 100)}%` }}
                  />
                </div>
                <span className="text-[10px] text-zinc-500 tabular-nums whitespace-nowrap">
                  {job.step ?? 0} / {job.max_steps ?? 20}
                </span>
              </div>
            </div>

            {/* Goal */}
            <div>
              <SectionLabel label="Goal" />
              <p className="text-xs text-zinc-300 leading-relaxed">{goal || job.goal || '—'}</p>
            </div>

            {/* Active Plan Step */}
            {steps.length > 0 && (
              <div>
                <SectionLabel label={`Plan  (${progress?.completed_steps ?? 0}/${progress?.total_steps ?? steps.length})`} />
                <div className="space-y-1">
                  {steps.map(s => (
                    <div key={s.id} className="flex items-center gap-2">
                      <span className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${STEP_STATUS_DOT[s.status] ?? 'bg-zinc-700'}`} />
                      <span className={`text-[11px] truncate ${s.status === 'Active' ? 'text-sky-300 font-medium' : s.status === 'Completed' ? 'text-zinc-500 line-through' : 'text-zinc-400'}`}>
                        {s.title}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Thought */}
            {job.thought && (
              <div>
                <SectionLabel label="Thought" />
                <p className="text-xs text-zinc-400 leading-relaxed italic">{job.thought}</p>
              </div>
            )}

            {/* Action */}
            {job.action && (
              <div>
                <SectionLabel label="Action" />
                <div className="bg-white/[0.03] border border-white/[0.06] rounded p-2.5">
                  <div className="flex items-center gap-1.5 mb-1">
                    <ChevronRight size={11} className="text-sky-500" />
                    <span className="text-xs font-mono text-sky-400">{job.action.action}</span>
                  </div>
                  {job.action.parameters &&
                    Object.entries(job.action.parameters).map(([k, v]) => (
                      <div key={k} className="flex gap-2 text-[10px] font-mono">
                        <span className="text-zinc-600">{k}:</span>
                        <span className="text-zinc-400">{String(v)}</span>
                      </div>
                    ))}
                </div>
              </div>
            )}

            {/* Verification */}
            {lastVerification && (
              <div>
                <SectionLabel label="Verification" />
                <div className="flex items-center gap-2 mb-1">
                  {lastVerification.verified
                    ? <CheckCircle size={12} className="text-emerald-400" />
                    : <XCircle size={12} className="text-red-400" />}
                  <span className="text-xs text-zinc-300">{lastVerification.verified ? 'Verified' : 'Failed'}</span>
                  <span className="ml-auto text-[10px] text-zinc-500">{Math.round((lastVerification.confidence ?? 0) * 100)}% conf.</span>
                </div>
                {lastVerification.verification_reason && (
                  <p className="text-[11px] text-zinc-500 leading-relaxed">{lastVerification.verification_reason}</p>
                )}
              </div>
            )}

            {/* Reflection */}
            {lastReflection && (
              <div>
                <SectionLabel label="Reflection" />
                <p className="text-[11px] text-zinc-400 leading-relaxed">{lastReflection.execution_summary}</p>
                <div className="flex gap-2 mt-1.5">
                  {lastReflection.recovery_required && (
                    <span className="text-[10px] px-1.5 py-0.5 rounded border text-amber-400 bg-amber-950/40 border-amber-700/30">Recovery</span>
                  )}
                  {!lastReflection.success && (
                    <span className="text-[10px] px-1.5 py-0.5 rounded border text-sky-400 bg-sky-950/40 border-sky-700/30">Retry</span>
                  )}
                </div>
              </div>
            )}

            {/* Recovery */}
            {lastRecovery && (
              <div>
                <SectionLabel label="Recovery" />
                <div className="flex items-center gap-2">
                  <RefreshCw size={11} className="text-zinc-500" />
                  <span className="text-[11px] text-zinc-300 font-medium">{lastRecovery.strategy}</span>
                </div>
                <p className="text-[11px] text-zinc-500 mt-1 leading-relaxed">{lastRecovery.explanation}</p>
              </div>
            )}

            {/* Context summary */}
            <div>
              <SectionLabel label="Context" />
              <div className="space-y-1">
                <div className="flex gap-2 text-[10px]">
                  <span className="text-zinc-600 w-20 flex-shrink-0">App</span>
                  <span className="text-zinc-400 truncate">{(job.world as Record<string, unknown>)?.active_application as string ?? '—'}</span>
                </div>
                <div className="flex gap-2 text-[10px]">
                  <span className="text-zinc-600 w-20 flex-shrink-0">Window</span>
                  <span className="text-zinc-400 truncate">{(job.world as Record<string, unknown>)?.focused_window as string ?? '—'}</span>
                </div>
              </div>
            </div>

            {/* Error */}
            {job.error && (
              <div>
                <SectionLabel label="Error" />
                <p className="text-xs text-red-400">{job.error}</p>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}
