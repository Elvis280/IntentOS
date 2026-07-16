/**
 * useVoice.ts
 *
 * Central hook for voice interaction. Manages:
 *   - Voice state machine
 *   - Push-to-talk keyboard shortcut (Ctrl+Space)
 *   - Transcript capture
 *   - Microphone button hold-to-talk
 *
 * The hook never imports a concrete voice implementation.
 * It consumes IVoiceService through the voiceService singleton,
 * which can be swapped independently.
 */

import { useCallback, useEffect, useRef, useState } from 'react'
import { voiceService } from '../../../services/voice.service'
import type { VoiceError, VoiceState } from '../../../types/voice'

export interface UseVoiceReturn {
  voiceState: VoiceState
  transcript: string
  error: VoiceError | null
  isSupported: boolean

  /** Begin listening (called on button mousedown or Ctrl+Space keydown). */
  startListening: () => void
  /** Stop capturing audio (called on mouseup or Ctrl+Space keyup). */
  stopListening: () => void
  /** Accept the current transcript — caller decides what to do with it. */
  confirmTranscript: () => string
  /** Discard the transcript and return to idle. */
  cancelTranscript: () => void
  /** Overwrite the transcript text (for inline editing). */
  setTranscript: (text: string) => void
}

export function useVoice(): UseVoiceReturn {
  const [voiceState, setVoiceState]   = useState<VoiceState>('idle')
  const [transcript, setTranscript]   = useState('')
  const [error, setError]             = useState<VoiceError | null>(null)

  // Track whether Ctrl+Space is currently held to avoid repeat keydown events
  const ctrlSpaceHeld = useRef(false)

  // ── Wire callbacks once on mount ─────────────────────────────────────────

  useEffect(() => {
    voiceService.onStateChange((state) => {
      setVoiceState(state)
      if (state !== 'error') setError(null)
    })

    voiceService.onResult((result) => {
      if (result.transcript) {
        setTranscript(result.transcript)
      }
    })

    voiceService.onError((err) => {
      setError(err)
      setVoiceState('error')
    })

    return () => {
      voiceService.destroy()
    }
  }, [])

  // ── Actions ───────────────────────────────────────────────────────────────

  const startListening = useCallback(() => {
    setTranscript('')
    setError(null)
    void voiceService.startListening()
  }, [])

  const stopListening = useCallback(() => {
    voiceService.stopListening()
  }, [])

  const confirmTranscript = useCallback((): string => {
    const text = transcript.trim()
    setVoiceState('idle')
    return text
  }, [transcript])

  const cancelTranscript = useCallback(() => {
    setTranscript('')
    setVoiceState('idle')
    setError(null)
  }, [])

  // ── Ctrl+Space push-to-talk ───────────────────────────────────────────────

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ctrl+Space — ignore if focus is inside a text input (allow normal typing)
      const tag = (e.target as HTMLElement).tagName
      if (tag === 'INPUT' || tag === 'TEXTAREA') return
      if (e.ctrlKey && e.code === 'Space' && !ctrlSpaceHeld.current) {
        e.preventDefault()
        ctrlSpaceHeld.current = true
        startListening()
      }
    }

    const handleKeyUp = (e: KeyboardEvent) => {
      if (e.ctrlKey && e.code === 'Space' && ctrlSpaceHeld.current) {
        e.preventDefault()
        ctrlSpaceHeld.current = false
        stopListening()
      }
      // Also release on plain Space-key-up in case Ctrl was released first
      if (e.code === 'Space' && ctrlSpaceHeld.current) {
        ctrlSpaceHeld.current = false
        stopListening()
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    window.addEventListener('keyup', handleKeyUp)
    return () => {
      window.removeEventListener('keydown', handleKeyDown)
      window.removeEventListener('keyup', handleKeyUp)
    }
  }, [startListening, stopListening])

  return {
    voiceState,
    transcript,
    error,
    isSupported: voiceService.isSupported(),
    startListening,
    stopListening,
    confirmTranscript,
    cancelTranscript,
    setTranscript,
  }
}
