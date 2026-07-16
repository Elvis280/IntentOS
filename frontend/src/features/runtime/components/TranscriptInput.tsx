import { useRef } from 'react'
import { Send, X } from 'lucide-react'

interface TranscriptInputProps {
  transcript: string
  onTranscriptChange: (value: string) => void
  onSubmit: () => void
  onCancel: () => void
}

/**
 * Shown when a transcript is ready (voice state === 'ready').
 * The user can edit the text, submit it to start the Runtime, or cancel.
 * Never auto-submits — always requires explicit confirmation.
 */
export function TranscriptInput({
  transcript,
  onTranscriptChange,
  onSubmit,
  onCancel,
}: TranscriptInputProps) {
  const inputRef = useRef<HTMLInputElement>(null)

  return (
    <div
      id="transcript-input-container"
      className="flex items-center gap-2 px-3 py-2 bg-sky-950/20 border border-sky-500/20 rounded-lg"
    >
      {/* Waveform icon */}
      <div className="flex items-end gap-[2px] h-4 flex-shrink-0">
        {[3, 5, 4, 6, 3].map((h, i) => (
          <span
            key={i}
            className="w-[2px] bg-sky-500/70 rounded-full"
            style={{ height: `${h}px` }}
          />
        ))}
      </div>

      {/* Editable transcript */}
      <input
        ref={inputRef}
        id="transcript-text-input"
        type="text"
        value={transcript}
        onChange={(e) => onTranscriptChange(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === 'Enter') onSubmit()
          if (e.key === 'Escape') onCancel()
        }}
        autoFocus
        className="flex-1 bg-transparent text-sm text-zinc-200 outline-none placeholder-zinc-600 min-w-0"
        placeholder="Edit transcript…"
      />

      {/* Submit */}
      <button
        id="transcript-submit-btn"
        onClick={onSubmit}
        disabled={!transcript.trim()}
        title="Submit (Enter)"
        className="flex items-center gap-1 px-2 py-1 rounded text-xs font-medium bg-sky-600 hover:bg-sky-500 text-white transition disabled:opacity-40 disabled:cursor-not-allowed flex-shrink-0"
      >
        <Send size={11} />
        Run
      </button>

      {/* Cancel */}
      <button
        id="transcript-cancel-btn"
        onClick={onCancel}
        title="Cancel (Esc)"
        className="w-6 h-6 flex items-center justify-center rounded text-zinc-600 hover:text-zinc-300 hover:bg-white/[0.06] transition flex-shrink-0"
      >
        <X size={12} />
      </button>
    </div>
  )
}
