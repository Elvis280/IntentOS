// ─── Voice State ─────────────────────────────────────────────────────────────

/** Lifecycle states the voice system can be in. */
export type VoiceState =
  | 'idle'        // Microphone not active
  | 'listening'   // Actively capturing audio
  | 'processing'  // Speech is done, converting to text
  | 'ready'       // Transcript is available; awaiting user confirmation
  | 'error'       // Non-fatal error; user can retry

// ─── Error Codes ─────────────────────────────────────────────────────────────

export type VoiceErrorCode =
  | 'not-supported'       // Browser does not support Web Speech API
  | 'permission-denied'   // User blocked microphone access
  | 'mic-unavailable'     // Hardware not accessible
  | 'recognition-failed'  // Network/service failure during recognition
  | 'no-speech'           // Timeout — no speech detected
  | 'aborted'             // Recognition was cancelled externally
  | 'unknown'

export interface VoiceError {
  code: VoiceErrorCode
  message: string        // User-facing, plain-English description
}

// ─── Recognition Result ───────────────────────────────────────────────────────

export interface VoiceResult {
  transcript: string
  confidence: number     // 0–1 confidence score from the recognition engine
  isFinal: boolean
}

// ─── Service Contract ─────────────────────────────────────────────────────────
// All future voice backends (Whisper, Gemini Live, OpenAI Realtime, etc.)
// must satisfy this interface. The Runtime must never reference a concrete impl.

export interface IVoiceService {
  isSupported(): boolean
  requestPermission(): Promise<boolean>
  startListening(): Promise<void>
  stopListening(): void
  destroy(): void

  onResult(cb: (result: VoiceResult) => void): void
  onError(cb: (error: VoiceError) => void): void
  onStateChange(cb: (state: VoiceState) => void): void
}
