import { useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Archive, CheckCircle2, XCircle, ChevronRight, X, Clock, Loader2 } from 'lucide-react'
import { agentApi } from '../../services/agentApi'
import type { SessionSummary, JobState } from '../../types/agent'
import { Timeline } from '../runtime/components/Timeline'

const STATUS_STYLES: Record<string, string> = {
  completed: 'text-emerald-400 bg-emerald-950/50 border-emerald-700/30',
  failed:    'text-red-400 bg-red-950/50 border-red-700/30',
  running:   'text-sky-400 bg-sky-950/50 border-sky-700/30',
  paused:    'text-amber-400 bg-amber-950/50 border-amber-700/30',
  stopped:   'text-zinc-500 bg-zinc-900/50 border-zinc-700/30',
  created:   'text-zinc-500 bg-zinc-900/50 border-zinc-700/30',
}

export function SessionsPage() {
  const [sessions, setSessions] = useState<SessionSummary[]>([])
  const [loading, setLoading] = useState(true)
  const [selected, setSelected] = useState<JobState | null>(null)
  const [detailLoading, setDetailLoading] = useState(false)

  useEffect(() => {
    agentApi.getSessions().then(r => {
      setSessions(r.sessions)
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [])

  const openSession = async (jobId: string) => {
    setDetailLoading(true)
    try {
      const detail = await agentApi.getSession(jobId)
      setSelected(detail)
    } finally {
      setDetailLoading(false)
    }
  }

  const fmtDate = (d?: string) => {
    if (!d) return '—'
    try { return new Date(d).toLocaleString() } catch { return d }
  }

  return (
    <div className="flex h-full">
      {/* List */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <div className="flex items-center gap-2 px-5 py-4 border-b border-white/[0.06]">
          <Archive size={14} className="text-zinc-500" />
          <h1 className="text-sm font-semibold text-zinc-200">Sessions</h1>
          <span className="ml-2 text-[10px] text-zinc-600">{sessions.length} archived</span>
        </div>
        <div className="flex-1 overflow-y-auto p-4">
          {loading ? (
            <div className="flex items-center justify-center h-32 text-zinc-600">
              <Loader2 size={18} className="animate-spin mr-2" /> Loading…
            </div>
          ) : sessions.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-32 text-zinc-600 gap-2">
              <Archive size={20} />
              <p className="text-xs">No sessions yet. Run your first job to create one.</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 gap-2">
              {sessions.map((s, i) => (
                <motion.button
                  key={s.job_id}
                  id={`session-card-${s.job_id}`}
                  initial={{ opacity: 0, y: 6 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.03 }}
                  onClick={() => void openSession(s.job_id)}
                  className="w-full text-left bg-[#0d0e10] border border-white/[0.06] hover:border-white/[0.12] rounded-xl p-4 transition-all group"
                >
                  <div className="flex items-start gap-3">
                    <div className="flex-1 min-w-0">
                      <p className="text-xs font-medium text-zinc-200 truncate">{s.goal || 'Untitled'}</p>
                      <p className="text-[10px] text-zinc-600 mt-1">{fmtDate(s.created_at)}</p>
                    </div>
                    <div className="flex items-center gap-2 flex-shrink-0">
                      <span className={`text-[10px] px-2 py-0.5 rounded-full border font-medium ${STATUS_STYLES[s.status] ?? STATUS_STYLES.stopped}`}>
                        {s.status}
                      </span>
                      <span className="text-[10px] text-zinc-600 tabular-nums">{s.step}/{s.max_steps}</span>
                      <ChevronRight size={13} className="text-zinc-700 group-hover:text-zinc-400 transition-colors" />
                    </div>
                  </div>
                  {s.error && (
                    <p className="text-[10px] text-red-400 mt-2 truncate">{s.error}</p>
                  )}
                </motion.button>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Detail Drawer */}
      <AnimatePresence>
        {(selected || detailLoading) && (
          <motion.aside
            initial={{ x: 400, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: 400, opacity: 0 }}
            transition={{ type: 'spring', stiffness: 280, damping: 28 }}
            className="w-96 flex-shrink-0 bg-[#0a0b0c] border-l border-white/[0.06] flex flex-col"
          >
            <div className="flex items-center gap-2 px-4 py-3 border-b border-white/[0.06]">
              <span className="text-xs font-medium text-zinc-400 flex-1">Session Detail</span>
              <button onClick={() => setSelected(null)} className="text-zinc-600 hover:text-zinc-300 transition-colors">
                <X size={14} />
              </button>
            </div>
            {detailLoading ? (
              <div className="flex items-center justify-center flex-1 text-zinc-600">
                <Loader2 size={18} className="animate-spin mr-2" /> Loading…
              </div>
            ) : selected && (
              <div className="flex-1 overflow-y-auto p-4 space-y-4">
                <div>
                  <p className="text-[10px] text-zinc-600 uppercase tracking-widest mb-1">Goal</p>
                  <p className="text-xs text-zinc-200 leading-relaxed">{selected.goal}</p>
                </div>
                <div className="flex gap-3">
                  <div>
                    <p className="text-[10px] text-zinc-600 uppercase tracking-widest mb-1">Status</p>
                    <span className={`text-[10px] px-2 py-0.5 rounded-full border font-medium ${STATUS_STYLES[selected.status] ?? STATUS_STYLES.stopped}`}>
                      {selected.status}
                    </span>
                  </div>
                  <div>
                    <p className="text-[10px] text-zinc-600 uppercase tracking-widest mb-1">Steps</p>
                    <p className="text-xs text-zinc-300">{selected.step} / {selected.max_steps}</p>
                  </div>
                </div>
                {selected.plan && (
                  <div>
                    <p className="text-[10px] text-zinc-600 uppercase tracking-widest mb-2">Plan</p>
                    {selected.plan.steps.map((s, i) => (
                      <div key={i} className="flex items-center gap-2 mb-1.5">
                        {s.status === 'Completed' ? <CheckCircle2 size={12} className="text-emerald-400" /> : s.status === 'Failed' ? <XCircle size={12} className="text-red-400" /> : <Clock size={12} className="text-zinc-600" />}
                        <span className="text-[11px] text-zinc-300">{s.title}</span>
                      </div>
                    ))}
                  </div>
                )}
                <div>
                  <p className="text-[10px] text-zinc-600 uppercase tracking-widest mb-2">Timeline</p>
                  <Timeline history={selected.history} />
                </div>
                {selected.error && (
                  <div>
                    <p className="text-[10px] text-zinc-600 uppercase tracking-widest mb-1">Error</p>
                    <p className="text-xs text-red-400">{selected.error}</p>
                  </div>
                )}
              </div>
            )}
          </motion.aside>
        )}
      </AnimatePresence>
    </div>
  )
}
