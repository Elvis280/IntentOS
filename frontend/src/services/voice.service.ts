/**
 * voice.service.ts
 *
 * MVP implementation of IVoiceService using the browser Web Speech API.
 *
 * Designed for replacement: swap this file with a Whisper, OpenAI Realtime,
 * or Gemini Live implementation. The hook and components never change.
 *
 * Future extension points:
 *   - Replace this class with a WhisperVoiceService, OpenAIRealtimeVoiceService, etc.
 *   - Wake word support would live in a WakeWordDetector wrapper that calls startListening().
 *   - Continuous conversation adds session state *around* this service, not inside it.
 */

import type {
  IVoiceService,
  VoiceError,
  VoiceErrorCode,
  VoiceResult,
  VoiceState,
} from '../types/voice'

// TypeScript shim for the non-standard Web Speech API
declare global {
  interface Window {
    SpeechRecognition: typeof SpeechRecognition | undefined
    webkitSpeechRecognition: typeof SpeechRecognition | undefined
  }
}

// ─── Error mapping ────────────────────────────────────────────────────────────

const ERROR_MAP: Record<string, { code: VoiceErrorCode; message: string }> = {
  'not-allowed':   { code: 'permission-denied',  message: 'Microphone access was denied. Please allow access in your browser settings.' },
  'audio-capture': { code: 'mic-unavailable',    message: 'No microphone found. Please connect one and try again.' },
  'network':       { code: 'recognition-failed', message: 'Speech recognition failed. Check your internet connection.' },
  'no-speech':     { code: 'no-speech',          message: 'No speech was detected. Hold the button and speak clearly.' },
  'aborted':       { code: 'aborted',            message: 'Recognition was cancelled.' },
  'service-not-allowed': { code: 'permission-denied', message: 'Speech recognition is blocked. Try allowing it in browser permissions.' },
}

function mapSpeechError(event: SpeechRecognitionErrorEvent): VoiceError {
  const mapped = ERROR_MAP[event.error]
  if (mapped) return mapped
  return { code: 'unknown', message: `Recognition error: ${event.error}` }
}

// ─── WebSpeechVoiceService ────────────────────────────────────────────────────

export class WebSpeechVoiceService implements IVoiceService {
  private recognition: SpeechRecognition | null = null

  private resultCb:      ((r: VoiceResult) => void) | null = null
  private errorCb:       ((e: VoiceError) => void) | null = null
  private stateChangeCb: ((s: VoiceState) => void) | null = null

  // ── Contract ──────────────────────────────────────────────────────────────

  isSupported(): boolean {
    return !!(window.SpeechRecognition ?? window.webkitSpeechRecognition)
  }

  async requestPermission(): Promise<boolean> {
    if (!navigator.mediaDevices?.getUserMedia) return false
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      stream.getTracks().forEach((t) => t.stop())
      return true
    } catch {
      return false
    }
  }

  onResult(cb: (r: VoiceResult) => void): void {
    this.resultCb = cb
  }

  onError(cb: (e: VoiceError) => void): void {
    this.errorCb = cb
  }

  onStateChange(cb: (s: VoiceState) => void): void {
    this.stateChangeCb = cb
  }

  async startListening(): Promise<void> {
    if (!this.isSupported()) {
      this.errorCb?.({ code: 'not-supported', message: 'Speech recognition is not supported in this browser.' })
      return
    }

    const hasPerm = await this.requestPermission()
    if (!hasPerm) {
      this.errorCb?.({ code: 'permission-denied', message: 'Microphone access was denied.' })
      return
    }

    // Clean up any previous instance
    this._teardown()

    const SpeechRecognitionImpl =
      window.SpeechRecognition ?? window.webkitSpeechRecognition

    if (!SpeechRecognitionImpl) {
      this.errorCb?.({ code: 'not-supported', message: 'Speech recognition is not available.' })
      return
    }

    const rec = new SpeechRecognitionImpl()
    rec.continuous     = false  // Stop after a single utterance
    rec.interimResults = false  // Only return final results for MVP
    rec.lang           = 'en-US'
    rec.maxAlternatives = 1

    rec.onstart = () => {
      this.stateChangeCb?.('listening')
    }

    rec.onresult = (event: SpeechRecognitionEvent) => {
      this.stateChangeCb?.('processing')
      const best = event.results[event.results.length - 1]
      if (best.isFinal) {
        const alt = best[0]
        this.resultCb?.({
          transcript: alt.transcript.trim(),
          confidence: alt.confidence,
          isFinal: true,
        })
        this.stateChangeCb?.('ready')
      }
    }

    rec.onerror = (event: SpeechRecognitionErrorEvent) => {
      // 'aborted' fires when we call stop() manually — not a real error
      if (event.error === 'aborted') {
        this.stateChangeCb?.('idle')
        return
      }
      this.errorCb?.(mapSpeechError(event))
      this.stateChangeCb?.('error')
    }

    rec.onend = () => {
      // If we never got a result (e.g., user released the button before speaking)
      // and we are still in 'listening', transition to idle silently
      // The actual state will have been set by onresult or onerror before this fires.
    }

    this.recognition = rec
    rec.start()
  }

  stopListening(): void {
    if (this.recognition) {
      this.stateChangeCb?.('processing')
      this.recognition.stop()
    }
  }

  destroy(): void {
    this._teardown()
    this.resultCb      = null
    this.errorCb       = null
    this.stateChangeCb = null
  }

  // ── Private ───────────────────────────────────────────────────────────────

  private _teardown(): void {
    if (this.recognition) {
      this.recognition.onstart  = null
      this.recognition.onresult = null
      this.recognition.onerror  = null
      this.recognition.onend    = null
      try { this.recognition.abort() } catch { /* already stopped */ }
      this.recognition = null
    }
  }
}

// ─── Singleton export ─────────────────────────────────────────────────────────
// Components and hooks import this singleton.
// Swap `WebSpeechVoiceService` here to change the backend globally.

export const voiceService = new WebSpeechVoiceService()
