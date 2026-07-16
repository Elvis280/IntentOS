import { AlertCircle, Keyboard } from 'lucide-react'
import type { VoiceError, VoiceState } from '../../../types/voice'

interface VoiceStatusProps {
  voiceState: VoiceState
  error: VoiceError | null
  isSupported: boolean
}

/**
 * Lightweight status indicator that sits below the ControlBar.
 * Shows the keyboard shortcut hint at idle, live state during recording,
 * and a user-friendly error message on failure.
 *
 * Renders null when there is nothing to display (job running, processing, etc.)
 * to avoid cluttering the UI.
 */
export function VoiceStatus({ voiceState, error, isSupported }: VoiceStatusProps) {
  if (!isSupported) {
    return (
      <div className="flex items-center gap-1.5 text-[10px] text-zinc-600">
        <AlertCircle size={10} />
        Speech recognition unavailable in this browser
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center gap-1.5 text-[10px] text-red-500">
        <AlertCircle size={10} />
        {error.message}
      </div>
    )
  }

  if (voiceState === 'listening') {
    return (
      <div className="flex items-center gap-1.5 text-[10px] text-red-400">
        {/* Animated dot */}
        <span className="w-1.5 h-1.5 rounded-full bg-red-500 animate-pulse" />
        Listening — release to stop
      </div>
    )
  }

  if (voiceState === 'processing') {
    return (
      <div className="flex items-center gap-1.5 text-[10px] text-sky-500">
        <span className="w-1.5 h-1.5 rounded-full bg-sky-500 animate-pulse" />
        Converting speech…
      </div>
    )
  }

  if (voiceState === 'idle') {
    return (
      <div className="flex items-center gap-1 text-[10px] text-zinc-700">
        <Keyboard size={9} />
        <kbd className="font-mono">Ctrl+Space</kbd>
        <span>to speak</span>
      </div>
    )
  }

  return null
}
