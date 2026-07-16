import { Mic, MicOff, Loader2, CheckCircle, AlertCircle } from 'lucide-react'
import type { VoiceState } from '../../../types/voice'

interface VoiceButtonProps {
  state: VoiceState
  isSupported: boolean
  /** Called on mousedown — begin listening */
  onPressStart: () => void
  /** Called on mouseup / mouseleave — stop listening */
  onPressEnd: () => void
}

// ── Per-state visual config ───────────────────────────────────────────────────

const STATE_CONFIG: Record<
  VoiceState,
  { icon: React.ReactNode; label: string; ring: string; bg: string; text: string }
> = {
  idle: {
    icon: <Mic size={15} />,
    label: 'Hold to speak (Ctrl+Space)',
    ring: 'border-white/[0.10]',
    bg:   'bg-white/[0.03] hover:bg-white/[0.07]',
    text: 'text-zinc-500 hover:text-zinc-300',
  },
  listening: {
    icon: <Mic size={15} />,
    label: 'Listening… release to stop',
    ring: 'border-red-500/60',
    bg:   'bg-red-950/50 hover:bg-red-900/60',
    text: 'text-red-400',
  },
  processing: {
    icon: <Loader2 size={15} className="animate-spin" />,
    label: 'Processing…',
    ring: 'border-sky-500/40',
    bg:   'bg-sky-950/40',
    text: 'text-sky-400',
  },
  ready: {
    icon: <CheckCircle size={15} />,
    label: 'Transcript ready',
    ring: 'border-emerald-500/40',
    bg:   'bg-emerald-950/40',
    text: 'text-emerald-400',
  },
  error: {
    icon: <AlertCircle size={15} />,
    label: 'Error — try again',
    ring: 'border-red-500/30',
    bg:   'bg-red-950/30 hover:bg-red-950/50',
    text: 'text-red-400',
  },
}

// ── Listening pulse ring (animated) ──────────────────────────────────────────

function ListeningRing() {
  return (
    <span className="absolute inset-0 rounded-full border border-red-500/50 animate-ping opacity-60 pointer-events-none" />
  )
}

// ── Component ─────────────────────────────────────────────────────────────────

export function VoiceButton({
  state,
  isSupported,
  onPressStart,
  onPressEnd,
}: VoiceButtonProps) {
  if (!isSupported) {
    return (
      <button
        id="voice-btn"
        disabled
        title="Speech recognition is not supported in this browser"
        className="relative w-9 h-9 flex items-center justify-center rounded-full border border-white/[0.06] bg-white/[0.02] text-zinc-700 cursor-not-allowed"
      >
        <MicOff size={14} />
      </button>
    )
  }

  const cfg = STATE_CONFIG[state]
  const isListening = state === 'listening'
  const isProcessing = state === 'processing'
  const isDisabled = isProcessing

  return (
    <button
      id="voice-btn"
      title={cfg.label}
      disabled={isDisabled}
      onMouseDown={(e) => { e.preventDefault(); onPressStart() }}
      onMouseUp={onPressEnd}
      onMouseLeave={() => { if (isListening) onPressEnd() }}
      onTouchStart={(e) => { e.preventDefault(); onPressStart() }}
      onTouchEnd={onPressEnd}
      className={[
        'relative w-9 h-9 flex items-center justify-center rounded-full border transition-all select-none',
        cfg.ring,
        cfg.bg,
        cfg.text,
        isDisabled ? 'cursor-not-allowed opacity-60' : 'cursor-pointer',
      ].join(' ')}
    >
      {isListening && <ListeningRing />}
      {cfg.icon}
    </button>
  )
}
