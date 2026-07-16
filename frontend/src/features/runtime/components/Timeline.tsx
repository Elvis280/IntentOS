import { CheckCircle, XCircle, Clock } from 'lucide-react'
import type { HistoryEntry } from '../../../types/agent'

interface TimelineProps {
  history: HistoryEntry[]
}

function TimelineRow({ entry, index }: { entry: HistoryEntry; index: number }) {
  const verified = entry.verified

  return (
    <div className="flex items-start gap-3 group">
      {/* Line + icon */}
      <div className="flex flex-col items-center">
        <div
          className={`w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0 border ${
            verified
              ? 'border-emerald-500/40 bg-emerald-950/60'
              : 'border-red-500/40 bg-red-950/60'
          }`}
        >
          {verified ? (
            <CheckCircle size={11} className="text-emerald-400" />
          ) : (
            <XCircle size={11} className="text-red-400" />
          )}
        </div>
        <div className="w-px flex-1 bg-white/[0.04] mt-1" />
      </div>

      {/* Content */}
      <div className="pb-4 min-w-0">
        <div className="flex items-center gap-2 mb-0.5">
          <span className="text-[10px] text-zinc-600 tabular-nums">#{index + 1}</span>
          <span className="text-xs font-mono font-medium text-zinc-300">
            {entry.action.action}
          </span>
          <span
            className={`text-[10px] font-medium px-1.5 py-0.5 rounded ${
              verified
                ? 'text-emerald-400 bg-emerald-950/60'
                : 'text-red-400 bg-red-950/60'
            }`}
          >
            {verified ? 'pass' : 'fail'}
          </span>
        </div>

        {entry.action.parameters && Object.keys(entry.action.parameters).length > 0 && (
          <div className="flex flex-wrap gap-x-3 gap-y-0.5">
            {Object.entries(entry.action.parameters).map(([k, v]) => (
              <span key={k} className="text-[10px] font-mono text-zinc-600">
                {k}=<span className="text-zinc-500">{String(v)}</span>
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export function Timeline({ history }: TimelineProps) {
  return (
    <div className="flex flex-col h-full bg-[#0d0e10] rounded-lg border border-white/[0.06] overflow-hidden">
      {/* Header */}
      <div className="flex items-center gap-2 px-4 py-2.5 border-b border-white/[0.06]">
        <Clock size={13} className="text-zinc-500" />
        <span className="text-xs font-medium text-zinc-500 tracking-wider uppercase">
          Timeline
        </span>
        {history.length > 0 && (
          <span className="ml-auto text-[10px] text-zinc-600 tabular-nums">
            {history.length} steps
          </span>
        )}
      </div>

      {/* Events */}
      <div className="flex-1 overflow-y-auto p-4">
        {history.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full gap-2">
            <Clock size={20} className="text-zinc-700" />
            <p className="text-xs text-zinc-600">Execution events will appear here</p>
          </div>
        ) : (
          <div>
            {history.map((entry, i) => (
              <TimelineRow key={i} entry={entry} index={i} />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
