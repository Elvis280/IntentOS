import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { MessageSquare, Send, X } from 'lucide-react'
import { agentApi } from '../../../services/agentApi'
import { useRuntimeStore } from '../../../store/runtimeStore'

interface ClarificationBarProps {
  jobId: string
  question: string
}

export function ClarificationBar({ jobId, question }: ClarificationBarProps) {
  const [answer, setAnswer] = useState('')
  const [sending, setSending] = useState(false)
  const { setJob, job } = useRuntimeStore()

  const submit = async () => {
    const text = answer.trim()
    if (!text) return
    setSending(true)
    try {
      await agentApi.clarify(jobId, text)
      setAnswer('')
      // Optimistically update job status back to running
      if (job) setJob({ ...job, status: 'running', clarification_question: '' })
    } finally {
      setSending(false)
    }
  }

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: 12 }}
        className="mx-4 mb-2 bg-amber-950/30 border border-amber-600/30 rounded-xl p-3"
      >
        <div className="flex items-start gap-2 mb-2">
          <MessageSquare size={13} className="text-amber-400 flex-shrink-0 mt-0.5" />
          <p className="text-xs text-amber-200 leading-relaxed">{question}</p>
        </div>
        <div className="flex gap-2">
          <input
            id="clarification-answer-input"
            value={answer}
            onChange={e => setAnswer(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && !e.shiftKey && void submit()}
            placeholder="Your answer…"
            autoFocus
            className="flex-1 bg-black/30 border border-amber-700/30 rounded-lg px-3 py-1.5 text-xs text-zinc-200 placeholder-zinc-600 focus:outline-none focus:border-amber-500/60 transition-colors"
          />
          <button
            id="clarification-submit-btn"
            onClick={() => void submit()}
            disabled={!answer.trim() || sending}
            className="px-3 py-1.5 rounded-lg bg-amber-600 hover:bg-amber-500 disabled:opacity-50 text-white text-xs font-medium transition-colors flex items-center gap-1.5"
          >
            <Send size={12} /> Send
          </button>
        </div>
      </motion.div>
    </AnimatePresence>
  )
}
